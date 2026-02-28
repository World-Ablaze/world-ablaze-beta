# AI Railway System - Edge Case Analysis

## File References

All code references use the current refactored file structure:

| Abbreviation | Full Path |
|---|---|
| `core.txt` | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt` |
| `strategies.txt` | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt` |
| `helpers.txt` | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt` |
| `primitives.txt` | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_primitives.txt` |
| `on_actions.txt` | `common/on_actions/WA_AI_misc_on_actions.txt` |

---

## Summary Table

| # | Edge Case | Severity | Frequency | Status |
|---|-----------|----------|-----------|--------|
| 1 | Puppet false borders | Medium | Rare | FIXED (Fix 25) |
| 2 | Owned vs Controlled mismatch | Medium | Occasional | FIXED (Fix 24) |
| 3 | Multi-front central hub | Medium | Common | OUTSTANDING |
| 4 | Update interval lag | Low | Always | DESIGN CHOICE |
| 5 | Non-neighbor claims overseas | High | Rare | FIXED (Fix 22) |
| 6 | Beachhead size vs strategy | Medium | Occasional | OUTSTANDING |
| 7 | Allied territory pathfinding | High | Common | FIXED (Fix 21) |
| 8 | Middle East vs Asia continent | Low | Rare | DESIGN LIMITATION |
| 9 | Minor nation civ threshold | Medium | Common | OUTSTANDING |
| 10 | No pre-war pathfinding | Medium | Occasional | FIXED (Fix 23) |
| 11 | Enemy puppet frontlines | Medium | Occasional | OUTSTANDING |
| 12 | Single beachhead per continent | Medium | Occasional | DESIGN LIMITATION |

---

## Fixed Edge Cases

### EDGE CASE 1: Puppet Territories Triggering False Borders (Fix 25)

**Location:** `helpers.txt` line 400 (`WA_AI_PC_railway_country_borders_enemy`)

**Issue:** The border check previously included ROOT's puppets' territories. This could cause countries to build railways towards distant fronts through puppet chain territories that don't make strategic sense.

**Fix Applied:** The `every_subject_country` block was completely removed (line 406-407). ROOT now only checks its own controlled states, not puppet territories. With Fix 21 (pathfinding type 2), ROOT cannot build railways through puppet territory anyway, so puppet borders are useless for railway planning.

**Current Code (lines 408-418):**
```
every_controlled_state = {
    limit = {
        any_neighbor_state = {
            OR = {
                is_controlled_by = var:_enemy_tag
                controller = { is_subject_of = var:_enemy_tag }
            }
        }
    }
    ROOT = { set_temp_variable = { borders_enemy_ = 1 } }
}
```

---

### EDGE CASE 2: Owned vs Controlled State Mismatch (Fix 24)

**Location:** `helpers.txt` line 400 (`WA_AI_PC_railway_country_borders_enemy`) and `strategies.txt` line 61 (frontline detection)

**Issue:** The border check previously used `any_owned_state` but frontline detection used `every_controlled_state`, creating inconsistency when ROOT owns but doesn't control a state (enemy occupation).

**Fix Applied:** Both border check and frontline detection now use `every_controlled_state` consistently (see lines 403-405 in helpers.txt). This eliminates the mismatch between owned and controlled state checks.

---

### EDGE CASE 5: Non-Neighbor Claims Going to Overseas Logic (Fix 22)

**Location:** `strategies.txt` line 757-761 (`STRATEGY_prewar_preparation`)

**Issue:** Countries with claims on non-neighboring countries (via `every_country` + `any_owned_state = { is_claimed_by = ROOT }` at line 617) could trigger the overseas logic branch. For landlocked nations like Hungary with claims on Romania, this meant nonsensical port construction attempts.

**Fix Applied:** Changed `else` to `else_if` with a coastal check (line 757-761):
```
else_if = {
    limit = { any_controlled_state = { is_coastal = yes } }
    # Overseas logic only for nations with coastal access
}
```
Landlocked nations now skip the overseas port infrastructure block entirely.

---

### EDGE CASE 7: Pathfinding Through Allied Territory (Fix 21)

**Location:** All pathfinding calls in `strategies.txt` and `core.txt`

**Issue:** Pathfinding previously used type 1 (ROOT + allies), but `build_railway` can only construct in ROOT-controlled territory. This caused partial railways, build failures, and resource waste when paths routed through allied provinces.

**Fix Applied:** All railway pathfinding calls now use `_pathfind_prov_type = 2`, which restricts pathfinding to ROOT-controlled provinces only. See:
- `strategies.txt` line 740 (pre-war)
- `strategies.txt` (land war and overseas sections)
- `core.txt` line 110

---

### EDGE CASE 10: No Pre-War Pathfinding Validation (Fix 23)

**Location:** `strategies.txt` lines 737-750 (`STRATEGY_prewar_preparation` land target handling)

**Issue:** Unlike land war strategy (which validates paths), pre-war preparation previously queued railways without pathfinding validation. This caused railways to be queued to impossible destinations (e.g., enclaves separated by foreign territory).

**Fix Applied:** Added pathfinding validation to pre-war land target handling (lines 738-750):
```
set_temp_variable = { _pathfind_prov_type = 2 }
set_temp_variable = { _pathfind_prov_allow_partial = 1 }
WA_AI_PATHFIND_PROV_get_path = yes

if = {
    limit = { check_variable = { pathfind_prov_success_ > 0 } }
    # Only queue if path exists
}
```

---

## Outstanding Edge Cases

### EDGE CASE 3: Multi-Front War - Central Hub Miscalculation

**Location:** `helpers.txt` line 428 (`WA_AI_PC_railway_score_and_sort_by_enemy_threat`)

**Issue:** The system calculates geometric center of ALL frontline supply hubs and prioritizes the closest hub. With the threat scoring system, the highest-threat enemy's first target gets +10% priority boost. However, this still treats all fronts as a single strategic blob.

**Example:** Germany fighting UK (in France) and SOV (in Poland):
- Front targets from both enemies mixed together
- Threat scoring helps (SOV likely scores higher), but geographic prioritization within each enemy's targets uses proximity, not strategic importance

**Impact:** Medium. The threat scoring system partially mitigates this by sorting targets by enemy danger level.

---

### EDGE CASE 6: Beachhead Selection Favors Size Over Strategy

**Location:** `helpers.txt` line 544 (`WA_AI_PC_get_best_port_on_landmass`)

**Issue:** Beachhead is selected purely as "largest naval base on enemy continent" with only a 15-state distance check and theatre separation check. Doesn't account for strategic positioning or proximity to actual frontlines.

**Example:** UK has Gibraltar (level 10) and Normandy (level 3). Gibraltar is within 15 states of Berlin but routing through Spain is impractical. Normandy is geographically better but loses the port level comparison.

**Mitigation:** Beachhead pathfinding validation (must find valid path to at least one frontline) prevents truly useless beachheads. But suboptimal selection still occurs.

---

### EDGE CASE 9: Civilian Factory Threshold Excludes Minor Nations

**Location:** `core.txt` lines 19-21, `on_actions.txt` lines 110-145

**Issue:** Two thresholds apply:
- **on_actions eligibility**: Peace requires 75+ civs (`@MIN_CIVS_PEACE`), war is always eligible
- **core.txt check**: 50 civs base, 30 during war (50 * 0.6)

Minor nations (Romania ~25 civs, Yugoslavia ~20 civs) fall below the peace threshold and the wartime core threshold. They receive no automated railway support.

The `@MINOR_CIV_THRESHOLD = 50` bypass in on_actions only helps nations above 50 civs, which are no longer "minor" in factory terms.

**Impact:** Medium. Creates a "rich get richer" effect where majors with good infrastructure get even better railway support.

---

### EDGE CASE 11: Enemy Puppet Territory Not Detected as Frontline

**Location:** `strategies.txt` lines 66-71 (land war frontline detection)

**Issue:** Frontline detection includes enemy puppets in the border check:
```
any_neighbor_state = {
    OR = {
        is_controlled_by = var:_current_enemy_tag
        controller = { is_subject_of = var:_current_enemy_tag }
    }
}
```

This is actually FIXED in the current code. The frontline detection at line 66-71 already includes `controller = { is_subject_of = var:_current_enemy_tag }`, matching the border detection logic.

**Status:** This was marked as outstanding in previous documentation but appears to be already resolved in the current code. The frontline detection at strategies.txt:66-71 correctly includes enemy puppet checks.

---

## Design Limitations

### EDGE CASE 4: Update Interval with Fast-Moving Fronts

**Location:** `core.txt` lines 15-17

**Issue:** Railways are planned every 8 weeks during war (previously 12 during peace). In a fast-moving war, frontlines may shift significantly between updates.

**Current behavior:**
- **War interval**: 8 weeks (~2 months)
- **Peace interval**: 12 weeks (~3 months)
- Stale project validation at lines 170-173 cancels projects targeting states no longer on the frontline

**Mitigation:** The 8-week war interval is a reasonable tradeoff. Shorter intervals would cause more frequent expensive recalculations. Stale project cancellation prevents building to outdated targets.

---

### EDGE CASE 8: Middle East vs Asia Continent Split

**Location:** `helpers.txt` line 35 (`WA_AI_PC_railway_get_continent`)

**Issue:** Middle East is treated as a separate continent (6) from Asia (4). Geographic proximity ignored at continent boundaries.

**Example:** UK at war with Iraq (Middle East=6). India (Asia=4) is geographically closest but wrong continent. System looks for Middle East beachhead instead.

**Impact:** Low. Matches HOI4's own continent definitions. A landmass-based approach (used elsewhere in the system) partially compensates.

---

### EDGE CASE 12: Single Beachhead Per Continent Limitation

**Location:** `strategies.txt` (overseas strategy, continent tracking)

**Issue:** The theatre separation check (`WA_AI_PC_check_theatre_separation` in helpers.txt:147) allows multiple beachheads on the same continent if they are 10+ BFS states apart. However, the continent-level processing still limits how many beachheads get full infrastructure support.

**Impact:** Medium. Multi-front operations on the same continent get partial support. Theatre separation prevents redundant beachheads close to each other.

---

## Critical Fixes Summary

| Fix # | Edge Case | Risk Before Fix | Fix Description |
|-------|-----------|----------------|-----------------|
| 21 | Allied territory pathfinding | Build failures, partial railways | Changed pathfinding type to 2 (ROOT-only) |
| 22 | Landlocked overseas logic | Nonsensical port construction | Added coastal check before overseas logic |
| 23 | No pre-war pathfinding | Invalid railway queues | Added pathfinding validation to pre-war targets |
| 24 | Owned vs controlled | Inconsistent border/frontline | Changed to `every_controlled_state` consistently |
| 25 | Puppet false borders | Illogical railway decisions | Removed puppet border extension from border check |
