# AI Railway System - Edge Case Analysis Report

## Architecture Note

**This document has been updated to reflect the new dynamic queue-based PC system architecture.**

The railway system now uses:
- **Dynamic queue** (`WA_AI_PC_queue`) with unlimited projects (no more 5-slot limit)
- **Progress-based construction** with weekly progress calculation
- **Dynamic factory allocation** (35% of available civs, up to 15 per project)
- **Railway-specific variables** (`WA_AI_PC_target_province^X`, `WA_AI_PC_connect_province^X`)

This addresses several previous edge cases related to queue limits and factory allocation.

## Summary of Test Cases

| Test Case | Expected Behavior | System Verdict |
|-----------|-------------------|----------------|
| 1. Germany → SOV frontline | ✅ Should build | **WORKS** - Direct border check passes |
| 2. Italy → SOV frontline | ❌ Should NOT build | **WORKS** - `WA_AI_PC_railway_country_borders_enemy` prevents it (Italy doesn't border SOV) |
| 3. ENG → European frontline | ✅ Should build via beachhead | **WORKS** - Overseas strategy handles this |
| 4. ENG → Hong Kong vs China | ❌ Should NOT build | **WORKS** - Beachhead validation fails pathfinding test |
| 5. Romania → SOV frontline | ✅ Should build | **WORKS** - Direct border |
| 5b. Romania → France | ❌ Should NOT build | **WORKS** - No direct border |

---

## Edge Cases That May Cause Unexpected Behavior

### **EDGE CASE 1: Puppet Territories Triggering False Borders** ✅ FIXED (Fix 25)

**Location:** `WA_AI_PC_railway_country_borders_enemy` (lines 343-376)

**Severity:** Medium | **Frequency:** Rare | **Fix Complexity:** Medium

**Issue:** The border check previously included ROOT's puppets' territories. This could cause countries to build railways towards distant fronts through puppet chain territories that don't make strategic sense.

**Example:**
If Germany puppets Croatia, and Croatia borders Soviet-controlled territory:
- Italy (allied with Germany) would NOT trigger this since it checks ROOT's puppets, not faction allies' puppets
- BUT: If Italy itself puppets Albania, and Albania somehow borders Yugoslavia (SOV puppet), Italy would suddenly start building railways towards Albania

**Current Behavior (FIXED - Fix 25):**
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

**Fix Applied:** The `every_subject_country` block has been completely removed. ROOT now only checks its own controlled states, not puppet territories. This prevents illogical railway decisions through puppet chains. Additionally, with Fix 21 (pathfinding type 2), ROOT cannot build railways through puppet territory anyway, so puppet borders are useless for railway planning.

---

### **EDGE CASE 2: Owned vs Controlled State Mismatch** ✅ FIXED (Fix 24)

**Location:** Border check and frontline detection in `WA_AI_PC_railway_country_borders_enemy` and `WA_AI_PC_railway_STRATEGY_land_war`

**Severity:** Medium | **Frequency:** Occasional | **Fix Complexity:** Low

**Issue:** The border check previously used `any_owned_state` but the frontline detection used `every_controlled_state`, creating inconsistency.

**Example:**
- Germany owns Alsace-Lorraine but France currently controls it (occupation/peace deal)
- Border check: Germany's **owned** states border France ✅
- Frontline detection: Germany's **controlled** states border France... but Alsace is not controlled

**Result:** Germany might believe it borders France but find no controlled frontline states, resulting in:
- No railways being built despite passing the border check
- Inconsistent decision-making between border detection and target selection

**Fix Applied:** Both border check and frontline detection now consistently use `every_controlled_state` and `is_controlled_by`, eliminating the mismatch between owned and controlled state checks. This ensures that border detection and frontline target selection use the same criteria.

---

### **EDGE CASE 3: Multi-Front War - Central Hub Miscalculation**

**Location:** `WA_AI_PC_railway_prioritize_central_hub` (lines 922-977)

**Severity:** Medium | **Frequency:** Common | **Fix Complexity:** Medium

**Issue:** The system calculates the geometric center of ALL frontline supply hubs and prioritizes the closest hub. This treats all fronts as a single strategic blob rather than independently.

**Example:**
Germany fighting both UK (in France) and SOV (in Poland):
- Frontline hubs detected: Bordeaux, Paris, Metz, Warsaw, Brest-Litovsk, Kiev
- Geometric center calculation: somewhere in central Europe
- "Central hub" prioritized: probably Metz or other western hubs (weighted by multiple French/UK hubs)
- Eastern front (potentially more critical against SOV): deprioritized

**Result:**
- Western front gets 1.1x priority multiplier
- Eastern front gets normal 1.0x priority
- Railway construction skews toward less critical theaters
- Does not account for threat level, current defensive strength, or enemy army size

**Code Pattern:**
```
# Calculates average position of all targets
# Moves closest hub to index 0 with 1.1x boost
# Ignores which front is strategically more important
```

**Better approach:** Prioritize by threat level (enemy divisions present, supply status) rather than geographic center.

---

### **EDGE CASE 4: 12-Week Update Interval with Fast-Moving Fronts**

**Location:** Line 21 (interval check: `check_variable = { WA_AI_PC_railway_INTERVAL_counter = 0 }`)

**Severity:** Low | **Frequency:** Always | **Fix Complexity:** Design Choice

**Issue:** Railways are planned every 3 months (12 weeks). In a fast-moving war, frontlines may still shift significantly between updates, though less than the previous 6-month interval.

**Example:**
1. **January 1942:** SOV frontline is at Smolensk (Smolensk supply hub selected)
2. **January-April:** Railway construction to Smolensk begins (3 months to build)
3. **April 1942:** Front collapses, now at Moscow (100+ km away)
4. **April 1942:** Next 3-month update happens (improved from previous 6-month cycle)
   - Smolensk railway may still be in progress
   - New queue starts building to Moscow sooner
   - Reduced lag compared to 6-month interval

**Result:**
- Railway construction still lags behind the actual front, but by 3 months instead of 6+
- More responsive to front line changes than previous 6-month interval
- Defensive infrastructure updates more frequently
- Offensive infrastructure supports advances more quickly

**Impact:** Reduced compared to 6-month interval, but still present in rapidly changing scenarios (Soviet invasions, strategic retreats, large-scale breakthroughs).

**Note:** Interval was reduced from 26 weeks (6 months) to 12 weeks (3 months) to improve responsiveness.

---

### **EDGE CASE 5: Pre-War Claims on Non-Neighbors Going to Overseas Logic**

**Location:** Lines 803-816 (Fix 14) and 832-862

**Severity:** High | **Frequency:** Rare | **Fix Complexity:** Low

**Issue:** Fix 14 adds countries with claims even if not neighbors. But the land/overseas check (line 833) can misclassify these:

**Example:**
- Hungary has claims on Transylvania (Romania)
- Hungary does NOT control states bordering Romania directly (Slovakia is in between)
- Romania gets added to `_target_countries_` via Fix 14 ✅
- `target_has_land_border` check: Does Hungary control states bordering Romania? NO
- `target_has_land_border = 0` ✅
- Goes to `else` block (line 862) → **overseas logic branch**
- Tries to find home port within 5 states

**Result:**
- **Landlocked Hungary executes overseas port infrastructure logic for Romania**
- System tries to upgrade "best port within 5 states"
- This is absurd: Hungary has no ports and is attacking a neighbor
- Wasted construction queue on impossible logic

**Code Location:**
```
# Lines 803-816: Add non-neighbor countries with claims
every_country = {
    NOT = { is_in_array = { _target_countries_ = THIS } }
    any_owned_state = {
        is_claimed_by = ROOT  # Can include distant claims
    }
    add_to_temp_array = { _target_countries_ = THIS }
}

# Lines 822-830: Check border
any_controlled_state = {
    any_neighbor_state = { is_owned_by = var:_target_tag }
    set_temp_variable = { target_has_land_border = 1 }
}

# Line 832-862: If no land border, execute overseas logic
else = {
    # Tries to build port infrastructure for landlocked attacker
    WA_AI_PC_railway_get_states_within_distance = yes
}
```

**Fix:** Add a check `if = { limit = { NOT = { is_coastal = yes } } ... skip this target ... }`

---

### **EDGE CASE 6: Beachhead Selection Favors Size Over Strategy**

**Location:** Lines 583-619 (beachhead selection)

**Severity:** Medium | **Frequency:** Occasional | **Fix Complexity:** Medium

**Issue:** Beachhead is selected purely as "largest naval base on enemy continent" with only a 15-state distance check. Doesn't account for strategic positioning or existing control near beachhead.

**Example:**
UK at war with Germany in 1942:
- UK controls Gibraltar (level 10 port, very large)
- UK controls Normandy beachhead (level 3 port, small)
- Gibraltar is within 15 states of Berlin ✅
- Normandy is within 15 states of Berlin ✅

**Algorithm decision:**
- Compares port levels: Gibraltar (10) > Normandy (3)
- Selects Gibraltar as beachhead
- Builds railways from Gibraltar → through Spain (neutral?) → into Germany

**Result:**
- Illogical logistics: supplies route through Gibraltar instead of nearby Normandy
- May require building through neutral territory (if Spain is not controlled)
- Ignores that Normandy has much better geographic positioning for Germany invasion

**Code Pattern:**
```
for_each_loop = { array = states_within_distance_ value = _check_state
    var:_check_state = {
        if = { limit = { naval_base > best_home_port_level } }
            set_temp_variable = { best_home_port_level = naval_base_level }
            set_temp_variable = { best_beachhead_province = naval_base_province }
        }
    }
}
# Only compares level, not distance, threat proximity, or existing control
```

**Better approach:** Prioritize by distance to enemy capital, not just port level.

---

### **EDGE CASE 7: Pathfinding Through Allied Territory May Fail at Build Time**

**Location:** Lines 435-443 (neighbor filtering in pathfinding)

**Severity:** High | **Frequency:** Common | **Fix Complexity:** High

**Issue:** Pathfinding allows provinces controlled by ROOT OR any allied country. But railways can only be built in your own territory!

**Example:**
- UK controls Normandy beachhead (Normandy province: UK)
- France (ally) controls everything between Normandy and German front
  - Province A: France-controlled
  - Province B: France-controlled
  - Province C: France-controlled
  - Province D: German-controlled (target)

**Pathfinding execution:**
1. Start at Normandy (UK-controlled) ✅
2. Expand to Province A (France-controlled) - passes ally check ✅
3. Expand to Province B (France-controlled) - passes ally check ✅
4. Expand to Province C (France-controlled) - passes ally check ✅
5. Finds path: Normandy → A → B → C → D
6. Reports: `pathfind_prov_success_ = 1` ✅

**At build time:**
```
build_railway = {
    start_province_id = Normandy
    target_province_id = Province_A
    # SUCCESS: Both UK
}

# Next segment:
build_railway = {
    start_province_id = Province_A
    target_province_id = Province_B
    # ERROR: UK is not France! Cannot build railway
}
```

**Result:**
- Pathfinding validation passes (path exists through allies)
- Actual railway building fails (can't build in allied territory)
- Railyay gets partially built, leaving disconnected segments
- Construction queue hangs or produces errors

**Code Issue:**
```
# Lines 437-443: Pathfinding allows allied territory
if = { limit = { check_variable = { _pathfind_prov_type = 1 } }
    OR = {
        controls_province = neighbor_id
        any_allied_country = {
            controls_province = neighbor_id  # ← PROBLEM
        }
    }
}

# But actual build command can only use ROOT-controlled provinces
build_railway = {
    start_province = prov_a
    target_province = prov_b
    # Both MUST be controlled by ROOT
}
```

**Critical Impact:** This could be the most serious issue, causing:
- Invalid construction queues
- Partial railways
- Resource waste

---

### **EDGE CASE 8: Middle East vs Asia Continent Split**

**Location:** Lines 554-560 (continent assignment)

**Severity:** Low | **Frequency:** Rare | **Fix Complexity:** Low

**Issue:** Middle East is treated as a separate continent from Asia. Geographic proximity ignored for continent boundaries.

**Example:**
- UK at war with Japan (Asia continent = 4)
- UK has strong positions in India (Asia continent = 4)
- UK also controls Aden/bases (Middle East continent = 6)

**Scenario:** UK at war with Iraq (Middle East = 6) AND Japan (Asia = 4):
- India (best port, closest to both): Asia continent = 4
- Iraq capital: Middle East continent = 6
- System looks for beachhead on Middle East continent
- Ignores India because wrong continent
- Selects weaker, more distant port

**Result:**
- Geographic logic ignored in favor of arbitrary continent labels
- India-to-Iraq is closer but won't be considered
- Sub-optimal beachhead selection

**Workaround:** System is technically correct per continent definitions, but definition itself is flawed.

---

### **EDGE CASE 9: 50 Civilian Factory Threshold Excludes Minor Nations**

**Location:** Lines 34-38 (minimum requirements)

**Severity:** Medium | **Frequency:** Common (for minor nations) | **Fix Complexity:** Low

**Issue:** Railway system requires minimum 50 civs (30 during war). Many minor nations fall below this.

**Example:**
1. Romania 1940: ~25-30 civilian factories
2. Romania justifies on Soviet Union
3. Pre-war strategy checks: civil factories >= 50? NO
4. Pre-war railways never queue
5. Romania declares war on SOV
6. War adjustment: civil factories >= 30? YES (if at 30)
7. Land war strategy triggers
8. But: Still 6 months until next update, no railways until July

**Result:**
- Minor nations with legitimate supply needs get infrastructure freeze
- Only major powers benefit from automated railway construction
- Creates "rich get richer" effect: majors already have good infrastructure, minors struggle

**Impact on gameplay:**
- Romania, Yugoslavia, Greece, smaller nations: NO railway support
- Germany, UK, USSR: Full railway support
- Disproportionate gameplay experience

**Current Threshold:**
```
if = { limit = {
    check_variable = { num_factories >= 50 }  # Pre-war
    # OR during war: >= 30
} }
```

**Alternative:** Scale minimum threshold by country size or starting factory count.

---

### **EDGE CASE 10: No Pathfinding Validation in Pre-War Strategy**

**Location:** Lines 832-860 (pre-war land target handling)

**Severity:** Medium | **Frequency:** Occasional | **Fix Complexity:** Low

**Issue:** Unlike land war strategy (lines 432-445 with pathfinding validation), pre-war preparation does NOT validate pathfinding before queuing railways.

**Example:**
- Germany has claims on Memel (Lithuania)
- Memel is separated from main Germany (requires path through East Prussia)
- Pre-war strategy queues railway: Capital → Memel (without validation)
- Pathfinding check skipped
- No validation that a land path exists

**During war:**
- Germany at war with Lithuania
- Railways already queued to Memel (validated at war time)
- But if Memel was detached by peace deal, railway path might fail

**Result:**
- Railways get queued to impossible destinations
- Wasting construction resources
- Causing errors at build time

**Code Comparison:**

Land War (lines 432-445) - **WITH validation:**
```
set_temp_variable = { _pathfind_prov_start = route_start }
set_temp_variable = { _pathfind_prov_end = supply_hub_province_ }
set_temp_variable = { _pathfind_prov_type = 1 }
WA_AI_PATHFIND_PROV_get_path = yes

if = { limit = { check_variable = { pathfind_prov_success_ = 1 } }
    add_to_temp_array = { railway_start_provinces_ = route_start }
}
```

Pre-War (lines 832-860) - **WITHOUT validation:**
```
WA_AI_PC_railway_get_supply_hub_province = yes

if = { limit = { check_variable = { supply_hub_province_ > 0 } }
    # Immediately adds without pathfinding check!
    add_to_temp_array = { railway_start_provinces_ = route_start }
    add_to_temp_array = { railway_end_provinces_ = supply_hub_province_ }
}
```

---

### **EDGE CASE 11: Enemy Puppet Territory Not Checked as Enemy Frontline**

**Location:** Lines 414-416 (frontline detection)

**Severity:** Medium | **Frequency:** Occasional | **Fix Complexity:** Low

**Issue:** Frontline detection checks `is_controlled_by = var:_current_enemy_tag` but doesn't check enemy's puppets. Creates inconsistency with border check.

**Example:**
- Germany at war with UK
- UK puppets Canada
- Germany's Newfoundland occupation borders Canadian-controlled states
- Border check (lines 350-353): Does state neighbor enemy OR enemy puppet?
  ```
  OR = {
      is_owned_by = var:_enemy_tag      # UK
      owner = { is_subject_of = var:_enemy_tag }  # Canada
  }
  ```
  Result: YES ✅ (Canada is UK puppet)

- Frontline detection (line 415): Does neighbor state border enemy?
  ```
  any_neighbor_state = {
      is_controlled_by = var:_current_enemy_tag  # Only checks UK
  }
  ```
  Result: NO ❌ (Neighbors controlled by Canada, not UK)

**Result:**
- Border check says: "Yes, Germany borders UK"
- Frontline check says: "No frontlines with UK found"
- Contradiction in decision-making
- No railways to Canadian-controlled frontlines despite having direct border

**Code Inconsistency:**
```
# Border check: Line 350-353 (inclusive)
OR = {
    is_owned_by = var:_enemy_tag
    owner = { is_subject_of = var:_enemy_tag }
}

# Frontline check: Line 415 (exclusive of puppets)
is_controlled_by = var:_current_enemy_tag
```

**Fix:** Add puppet check to frontline detection:
```
any_neighbor_state = {
    OR = {
        is_controlled_by = var:_current_enemy_tag
        controller = { is_subject_of = var:_current_enemy_tag }
    }
}
```

---

### **EDGE CASE 12: Single Beachhead Per Continent Limitation (Fix 8)**

**Location:** Lines 528-577 (Fix 8: continent tracking)

**Severity:** Medium | **Frequency:** Occasional | **Fix Complexity:** Medium

**Issue:** Only one beachhead per continent is processed due to Fix 8. Multi-theater operations on same continent get limited support.

**Example:**
UK at war with both Germany AND Italy in 1943:
- Both on Europe continent (continent = 1)
- Fix 8 adds continent 1 to `_processed_continents_` array
- First enemy processed: Germany
  - Finds Normandy as beachhead
  - Builds railways from Normandy to German supply hubs
- Second enemy processed: Italy
  - Checks: Is Europe already processed? YES
  - Line 574: `if = { limit = { check_variable = { _skip_continent = 0 } } }`
  - Skips entire Italy beachhead logic
  - No railway construction to Sicily or Italian front

**Result:**
- Two-front theater on one continent only gets infrastructure for first enemy processed
- Second front (could be strategically important) gets zero railway support
- No parallel operations on same continent

**Code Location (lines 563-577):**
```
for_each_loop = { array = _processed_continents_ value = _proc_cont
    if = { limit = { check_variable = { _proc_cont = enemy_continent } }
        set_temp_variable = { _skip_continent = 1 }
    }
}

if = { limit = { check_variable = { _skip_continent = 0 } }
    # Only executes once per continent!
}
```

**Why it exists:** Prevents resource waste on multiple overseas targets, but too restrictive.

**Impact:** Theater selection becomes luck-based (enemy iteration order) rather than strategic.

---

## Summary Table

| Edge Case | Severity | Frequency | Fix Complexity | Impact Type | Status |
|-----------|----------|-----------|----------------|------------|--------|
| 1. Puppet false borders | Medium | Rare | Medium | Logic error | ✅ FIXED (Fix 25) |
| 2. Owned vs Controlled | Medium | Occasional | Low | Inconsistency | ✅ FIXED (Fix 24) |
| 3. Multi-front central hub | Medium | Common | Medium | Suboptimal strategy | ⚠️ OUTSTANDING |
| 4. 26-week lag | Low | Always | Design choice | Gameplay mechanic | ℹ️ DESIGN CHOICE |
| 5. Non-neighbor claims → overseas | High | Rare | Low | Critical flaw | ✅ FIXED (Fix 22) |
| 6. Beachhead size vs strategy | Medium | Occasional | Medium | Suboptimal strategy | ⚠️ OUTSTANDING |
| 7. Allied territory path | **High** | **Common** | **High** | **Build failure** | ✅ **FIXED (Fix 21)** |
| 8. Continent split | Low | Rare | Low | Niche issue | ℹ️ DESIGN LIMITATION |
| 9. 50 civ threshold | Medium | Common (minors) | Low | Balance issue | ⚠️ OUTSTANDING |
| 10. No pre-war pathfinding | Medium | Occasional | Low | Validation gap | ✅ FIXED (Fix 23) |
| 11. Enemy puppet frontlines | Medium | Occasional | Low | Inconsistency | ⚠️ OUTSTANDING |
| 12. Single beachhead per continent | Medium | Occasional | Medium | Restriction issue | ℹ️ DESIGN LIMITATION |

---

## Critical Issues Status

### **✅ FIXED: EDGE CASE 7 - Allied Territory Pathfinding (Fix 21)**
- **Risk:** Partial railway construction, build errors
- **Fix Applied:** Changed `_pathfind_prov_type` from 1 to 2 in all railway pathfinding calls
- **Result:** Pathfinding now only considers ROOT-controlled provinces

### **✅ FIXED: EDGE CASE 5 - Pre-War Overseas Logic for Landlocked Nations (Fix 22)**
- **Risk:** Nonsensical port construction attempts
- **Fix Applied:** Changed `else` to `else_if` with coastal check before overseas logic
- **Result:** Landlocked nations skip overseas port infrastructure logic

### **✅ FIXED: EDGE CASE 10 - Pre-War Pathfinding Validation (Fix 23)**
- **Risk:** Invalid railway queues to unreachable targets
- **Fix Applied:** Added pathfinding validation to pre-war land target handling
- **Result:** Pre-war railways validated before queuing (matches land war strategy)

### **✅ FIXED: EDGE CASE 1 - Puppet False Borders (Fix 25)**
- **Risk:** Illogical railway decisions through puppet chain territories
- **Fix Applied:** Removed `every_subject_country` block from `WA_AI_PC_railway_country_borders_enemy`
- **Result:** ROOT only checks its own controlled states for border detection, not puppet territories
- **Rationale:** With Fix 21, ROOT cannot build railways through puppet territory anyway, so puppet borders are useless

### **✅ FIXED: EDGE CASE 2 - Owned vs Controlled Mismatch (Fix 24)**
- **Risk:** Inconsistent behavior when ROOT owns but doesn't control a state
- **Fix Applied:** Changed `any_owned_state` to `every_controlled_state` in border check
- **Result:** Both border check and frontline detection now use `every_controlled_state` consistently

---

## Outstanding Issues

### **High Priority Remaining:**

1. **EDGE CASE 11:** Enemy puppet frontlines not detected
   - Add puppet check to frontline detection (match border check logic)
   - Simple fix, medium impact

### **Medium Priority Remaining:**

1. **EDGE CASE 3:** Multi-front central hub miscalculation
   - Geometric center may prioritize wrong front
   - Consider threat-level prioritization instead

2. **EDGE CASE 6:** Beachhead size vs strategy
   - Port level prioritized over strategic positioning

3. **EDGE CASE 9:** 50 civ threshold excludes minors
   - Minor nations get no railway support
   - Consider scaling threshold by country size

### **Design Limitations (May Not Need Fixing):**

1. **EDGE CASE 4:** 26-week update interval
   - Design choice for performance

2. **EDGE CASE 8:** Middle East vs Asia continent split
   - Matches game's continent definitions

3. **EDGE CASE 12:** Single beachhead per continent
   - Prevents resource waste but limits multi-theater ops

