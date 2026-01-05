# Reserve Creation and Spawning System Analysis
## World Ablaze Beta - Hearts of Iron IV Mod

**Analysis Date:** January 5, 2026  
**System Version:** Current build  
**Files Analyzed:** 
- `/common/decisions/_reserves.txt`
- `/common/scripted_guis/reserves_scripted_gui.txt`
- `/common/scripted_localisation/05_scripted_localisation.txt`
- `/common/on_actions/100_wa_on_actions.txt`
- `/events/wa_sov_events.txt`

---

## Executive Summary

The reserve system allows major nations to recruit and deploy reserve divisions during peacetime, which can be activated during war. The system uses a variable-based approach to track reserve levels (0-100 in increments of 10) and provides both infantry and specialized division templates. This analysis identifies **7 critical bugs**, **12 edge cases**, and **9 inefficiency issues** that affect gameplay balance, AI behavior, and player experience.

---

## System Architecture Overview

### Core Components

1. **Reserve Variable System**
   - `reserves` variable: Tracks available reserve levels (0-100)
   - `reserves_equipment` variable: Tracks equipment bonuses for FRA/SOV
   - Increments in steps of 10

2. **Decision System**
   - `recruit_more_reserves`: 90-day decision to gain 10 reserves
   - `early_reserve_mobilization`: Allows deployment before peace ends
   - `finish_recruitment_of_reserves`: Unlocks reserve templates for editing
   - Country-specific decisions (USA, ENG, CAN)

3. **Spawning Mechanism**
   - Creates division templates with specific names
   - Spawns divisions at capital or specific locations
   - Different templates for 1st and 2nd wave reserves
   - Separate AI spawning logic with better equipment

4. **Allowed Nations**
   - Major Powers: FRA, ITA, JAP, GER, SOV, ENG, USA
   - Minor Powers: POL, HUN, ROM, CAN, AST, RAJ, SAF, CZE, YUG, SPR, HOL, BEL, GRE, FIN, BUL

---

## BUGS IDENTIFIED

### 1. **CRITICAL: Division Template Name Typo**
**Location:** Lines 768-985+ in `_reserves.txt`  
**Severity:** Critical - Prevents system from working

**Issue:**
All reserve division template names have a typo: "Divisíon" instead of "Division" (using í instead of i).

**Example:**
```
has_template = "French Reserve Divisíon"
has_template = "Italian Reserve Divisíon"
has_template = "Japanese Reserve Divisíon"
```

**Impact:**
- System cannot find templates if they're created with correct spelling
- Players cannot edit or deploy reserves properly
- Affects all 22 countries across 66+ division templates

**Fix Required:**
Replace all instances of "Divisíon" with "Division" throughout the file.

---

### 2. **CRITICAL: Variable Check Logic Error**
**Location:** Lines 192-533 in `_reserves.txt`  
**Severity:** Critical - Wrong condition operator

**Issue:**
The decision uses `check_variable = { ROOT.reserves = 10 }` which checks for EXACTLY 10, not "greater than or equal to 10". This creates impossible progression conditions.

**Example:**
```
if = {
    limit = {
        check_variable = { ROOT.reserves = 10 }  # Wrong: checks for == 10
        NOT = { has_completed_focus = SOV_reserve_armies_administration }
    }
    check_variable = { ROOT.reserves = 10 }  # Wrong again
```

**Impact:**
- After reaching 10 reserves, requirements immediately fail
- Players get stuck and cannot progress
- Each tier (10, 20, 30... 90) has this bug

**Fix Required:**
Change all instances to `check_variable = { ROOT.reserves > 9 }` or similar proper comparisons.

---

### 3. **HIGH: Missing SOV Reserves Check**
**Location:** Lines 573-577 in `_reserves.txt`  
**Severity:** High - Breaks Soviet gameplay

**Issue:**
The `recruit_more_reserves` decision is hidden for SOV if government is not communism, but there's no alternative system for non-communist Soviet.

```
if = {
    limit = { tag = SOV }
    NOT = { has_government = communism }
}
```

**Impact:**
- Non-communist Soviet Union cannot recruit reserves
- Historical SOV path gets all 100 from focuses (line 604)
- Alternate history paths are disadvantaged

---

### 4. **MEDIUM: Inconsistent Equipment Requirements**
**Location:** Lines 209-565 in `_reserves.txt`  
**Severity:** Medium - Balance issue

**Issue:**
Equipment requirements scale inconsistently:
- 10 reserves: 15K equipment (player), 25K (non-USA)
- 20 reserves: 20K equipment (player), 35K (non-USA)
- Scaling is not linear and differs by country

**Impact:**
- Unpredictable progression
- USA gets massive advantage
- SOV with special focus gets half requirements

---

### 5. **MEDIUM: Race Condition in Template Check**
**Location:** Lines 762-912 in `_reserves.txt`  
**Severity:** Medium - Timing issue

**Issue:**
`finish_recruitment_of_reserves` decision checks for template existence but doesn't verify the template was created by the reserves system.

```
available = {
    hidden_trigger = {
        OR = {
            has_template = "French Reserve Divisíon"
            # ... etc
```

**Impact:**
- Players can manually create templates with these names
- Can unlock reserves early by exploiting template names
- Breaks intended progression

---

### 6. **LOW: Event Does Nothing**
**Location:** Event `sov_armor.817` in `wa_sov_events.txt` lines 1643-1658  
**Severity:** Low - Dead code

**Issue:**
The event triggered on reserve completion has no effects, just displays a message.

```
country_event = {
    id = sov_armor.817
    # ... only has a single option with no effects
}
```

**Impact:**
- Wasted event call
- Could be used for feedback or effects
- Minor performance impact

---

### 7. **LOW: Missing Validation on Early Mobilization**
**Location:** Lines 669-729 in `_reserves.txt`  
**Severity:** Low - Edge case exploit

**Issue:**
`early_reserve_mobilization` doesn't check if reserves are actually available to deploy.

```
available = {
    threat > 0.39
    # ... no check if reserves > 0 for deployment
}
```

**Impact:**
- Can set flag without deployable reserves
- Confusing player experience
- May break scripted logic

---

## EDGE CASES IDENTIFIED

### 1. **Faction Change During Recruitment**
**Scenario:** Country changes faction while recruiting reserves  
**Impact:** No cancellation logic; continues with old faction alignment  
**Risk:** Medium - May cause diplomatic issues

### 2. **Government Change Mid-Recruitment**
**Scenario:** Civil war or coup during 90-day recruitment period  
**Impact:** No handling for government change; decision continues  
**Risk:** High - Can result in wrong faction divisions

### 3. **Capital Relocation**
**Scenario:** Capital moves while reserves are being recruited  
**Current Behavior:** Spawns at old capital location  
**Risk:** Low - Divisions spawn in enemy territory

### 4. **Puppet/Subject Status**
**Scenario:** Country becomes puppet during recruitment  
**Impact:** No checks for subject status; can still recruit  
**Risk:** Medium - Overlord may not want subject to have reserves

### 5. **Manpower Exhaustion**
**Scenario:** Country has no manpower when reserves finish  
**Impact:** Divisions spawn but cannot be filled  
**Risk:** Low - Wasteful but not game-breaking

### 6. **Equipment Shortage at Spawn**
**Scenario:** Not enough equipment when reserves deploy  
**Current Behavior:** `start_equipment_factor=0.1` or `0.75`  
**Risk:** Low - Intended behavior, but confusing

### 7. **Multiple Template Variants**
**Scenario:** Player creates infantry, motorized, and mechanized variants  
**Impact:** All three types can spawn simultaneously  
**Risk:** Medium - Can overwhelm economy

### 8. **USA Flag Conflicts**
**Scenario:** USA has both `USA_selective_service_act_flag` and `USA_265_plan_flag`  
**Impact:** Reduced requirements stack; may be too powerful  
**Risk:** Low - Likely intentional but undocumented

### 9. **Reserve Deletion After Deployment**
**Scenario:** Player deletes reserve divisions after deployment  
**Impact:** No tracking; variable not updated  
**Risk:** Low - Can exploit to regain reserves

### 10. **SOV Focus Path Interaction**
**Scenario:** SOV gets reserves from both focuses and decisions  
**Impact:** AI intentionally disabled (line 604) but player can exploit  
**Risk:** Medium - Can exceed 100 reserves cap

### 11. **Maximum Reserve Cap**
**Scenario:** Variable goes above 100  
**Impact:** GUI only shows 0-100; behavior undefined  
**Risk:** Low - No upper bound validation

### 12. **Tag Change (e.g., FRA → VIC)**
**Scenario:** Country changes tag during recruitment  
**Impact:** Loses access to reserve decisions  
**Risk:** Medium - Investment lost

---

## INEFFICIENCIES IDENTIFIED

### 1. **Excessive Code Duplication**
**Location:** Throughout `_reserves.txt`  
**Severity:** Critical - Maintainability

**Issue:**
- 22 countries × 3 template types × 2 waves = 132 near-identical code blocks
- Each unlock section repeats 66 times (lines 1077-1591)
- Each spawn section repeats 132 times (lines 1593-5758)

**Impact:**
- 5000+ lines of repetitive code
- Any bug fix requires 100+ edits
- High risk of inconsistency
- Difficult to add new countries

**Recommendation:**
Use scripted effects with parameters:
```
recruit_reserves_effect = {
    country = FRA
    template_base = "French"
    location = 11506
}
```

---

### 2. **Inefficient Variable Comparisons**
**Location:** Lines 192-533 in `_reserves.txt`  
**Severity:** High - Performance

**Issue:**
Nested if-statements check each tier sequentially instead of using proper comparison operators.

```
if = { limit = { check_variable = { ROOT.reserves = 10 } } ... }
if = { limit = { check_variable = { ROOT.reserves = 20 } } ... }
# ... repeated 9 times per path
```

**Impact:**
- O(n) complexity instead of O(1)
- Evaluated every day for every country
- Unnecessary CPU cycles

**Recommendation:**
Use >= comparisons and reverse order:
```
if = {
    limit = { check_variable = { ROOT.reserves >= 90 } }
    # highest requirements
}
else_if = {
    limit = { check_variable = { ROOT.reserves >= 80 } }
    # next tier
}
```

---

### 3. **Hardcoded State IDs**
**Location:** Lines 1593-6708 in `_reserves.txt`  
**Severity:** Medium - Flexibility

**Issue:**
Every spawn location uses hardcoded state IDs and province IDs.

**Example:**
```
prioritize_location = 11506  # Paris
prioritize_location = 9904   # Rome
prioritize_location = 1182   # Tokyo
```

**Impact:**
- Breaks with map mods
- Cannot be configured by players
- Requires mod knowledge to modify

**Recommendation:**
Use `capital_scope` consistently or define spawn locations in variables.

---

### 4. **Redundant AI Logic**
**Location:** Lines 6012-6246 in `_reserves.txt`  
**Severity:** Medium - Performance

**Issue:**
AI spawning logic duplicates player logic with only equipment factor changes.

**Impact:**
- 1000+ lines of duplicated code
- Same templates defined twice
- Harder to maintain balance changes

**Recommendation:**
Use single effect with conditional equipment factor:
```
set_temp_variable = { equip_factor = 0.1 }
if = { limit = { is_ai = yes } set_temp_variable = { equip_factor = 0.75 } }
```

---

### 5. **Missing Localization Variables**
**Location:** `_reserves.txt` and localisation files  
**Severity:** Low - User experience

**Issue:**
Requirements use `custom_override_tooltip` but recalculate values in multiple places.

**Impact:**
- Potential desync between display and logic
- Hard to maintain consistent messaging

**Recommendation:**
Use scripted localization for dynamic values.

---

### 6. **No Centralized Configuration**
**Location:** Scattered throughout files  
**Severity:** High - Modifiability

**Issue:**
Magic numbers everywhere:
- `days_remove = 90` (recruitment time)
- `cost = 0` or `cost = 50` (PP cost)
- `industrial_capacity_factory = -0.05` (factory penalty)
- `training_time_factor = 1.0` (training penalty)

**Impact:**
- Cannot easily rebalance system
- Requires searching entire file for changes
- Risk of inconsistency

**Recommendation:**
Create defines or scripted values:
```
@reserve_recruitment_days = 90
@reserve_factory_penalty = 0.05
@reserve_training_penalty = 1.0
```

---

### 7. **Suboptimal AI Weights**
**Location:** Lines 580-636 in `_reserves.txt`  
**Severity:** Medium - AI behavior

**Issue:**
AI decision weights are simple and don't consider:
- Current manpower situation
- Front-line pressure
- Equipment availability
- Strategic reserves needed

**Example:**
```
ai_will_do = {
    factor = 500  # Fixed high value
    modifier = { factor = 0 ... }  # Binary on/off
}
```

**Impact:**
- AI over-recruits or under-recruits
- Doesn't adapt to situation
- Can waste resources during critical moments

**Recommendation:**
Add dynamic factors:
```
ai_will_do = {
    base = 100
    modifier = { factor = 2 any_enemy_country = { strength_ratio = { tag = ROOT ratio > 1.5 } } }
    modifier = { factor = 0.5 has_manpower < 100000 }
}
```

---

### 8. **Inefficient Template Locking System**
**Location:** Lines 1077-1591 in `_reserves.txt`  
**Severity:** Low - User experience

**Issue:**
Templates are locked until player clicks decision, but all templates are pre-created.

**Impact:**
- Clutters division template list
- Confusing for players
- Can't customize before deployment

**Recommendation:**
Create templates dynamically on deployment, not pre-locked.

---

### 9. **Missing Progress Feedback**
**Location:** Entire system  
**Severity:** Low - User experience

**Issue:**
No visual feedback during 90-day recruitment:
- No progress bar
- No monthly events
- No cost/benefit preview

**Impact:**
- Player doesn't know what they're getting
- Can't plan around recruitment completion
- Poor user experience

**Recommendation:**
- Add timed tooltips showing progress
- Create preview tooltips showing expected divisions
- Add milestone events at 30/60/90 days

---

## RECOMMENDATIONS

### Priority 1 (Critical - Fix Immediately)
1. **Fix Division Template Typo** - Change "Divisíon" to "Division"
2. **Fix Variable Comparison Logic** - Use >= instead of =
3. **Add Upper Bound Validation** - Prevent reserves > 100

### Priority 2 (High - Fix Soon)
4. **Refactor Code Duplication** - Use scripted effects
5. **Fix SOV Non-Communist Path** - Add alternative reserve access
6. **Improve AI Decision Logic** - Make context-aware
7. **Add Configuration System** - Use defines for magic numbers

### Priority 3 (Medium - Future Enhancement)
8. **Add Progress Feedback** - Show recruitment status
9. **Improve Edge Case Handling** - Add checks for government/faction changes
10. **Optimize Variable Checks** - Use reverse-order else-if chains
11. **Add Validation to Early Mobilization** - Check reserve availability

### Priority 4 (Low - Quality of Life)
12. **Remove Dead Event Code** - Clean up sov_armor.817
13. **Add Dynamic Spawn Locations** - Use variables instead of hardcoded IDs
14. **Improve Equipment Scaling** - Make more consistent and predictable

---

## TESTING RECOMMENDATIONS

### Automated Tests Needed
1. **Template Name Validation** - Verify all templates can be found
2. **Variable Boundary Tests** - Test reserves at 0, 10, 20... 100, 110
3. **Decision Availability** - Test all countries can access decisions
4. **Spawn Location Validation** - Verify all spawn points are valid

### Manual Testing Scenarios
1. **Happy Path** - Each country recruits and deploys successfully
2. **Edge Cases** - Government change, civil war, puppet status during recruitment
3. **AI Behavior** - Verify AI recruits appropriately for each nation
4. **Performance** - Test with all 22 nations recruiting simultaneously
5. **Compatibility** - Test with map mods and other major mods

---

## CONCLUSION

The reserve system is functional but suffers from critical bugs, poor code organization, and lack of edge case handling. The most urgent issue is the typo in division template names, which likely prevents the entire system from working correctly. The second critical issue is the variable comparison logic error that prevents progression beyond the first tier.

After fixing these critical bugs, refactoring for code reuse should be the next priority to improve maintainability and reduce the risk of future bugs.

**Estimated Fix Time:**
- Critical bugs: 4-6 hours
- High priority: 16-24 hours  
- Medium priority: 24-40 hours
- Low priority: 8-16 hours
- **Total: 52-86 hours** (1-2 weeks of development time)

---

## APPENDIX A: Affected Code Locations

### Primary Files
- `/common/decisions/_reserves.txt` (6,984 lines)
  - Lines 137-665: `recruit_more_reserves` decision
  - Lines 669-729: `early_reserve_mobilization` decision
  - Lines 733-6373: `finish_recruitment_of_reserves` decision
  - Lines 6375-6850: Home Guard decisions (CAN, ENG)

### Supporting Files
- `/common/scripted_guis/reserves_scripted_gui.txt` (56 lines)
- `/common/scripted_localisation/05_scripted_localisation.txt` (Lines 4676-4812)
- `/common/on_actions/100_wa_on_actions.txt` (Reserve variable initialization)
- `/events/wa_sov_events.txt` (Event sov_armor.817)

### Localization Files
- `/localisation/english/production_l_english.yml`
- Various country-specific localisation files

---

## APPENDIX B: Variable Usage

### Global Variables
- `ROOT.reserves` - Integer 0-100, increments of 10
- `ROOT.reserves_equipment` - Float 0.0-1.0 for FRA/SOV
- `global.reserves` - Not used (potential confusion)

### Country Flags
- `early_reserve_mobilization_flag` - Allows wartime deployment
- `reserves_finished_1` - First wave unlocked
- `reserves_finished_2` - Second wave unlocked
- `reserves_deployed_flag` - USA stockpile deployment flag
- `home_guard_deployed` - CAN/ENG home guard active
- Various USA flags for selective service

---

## APPENDIX C: Balance Implications

### Current Reserve Distribution
- **Tier 0** (0 reserves): All nations start here
- **Tier 1** (10 reserves): ~200K manpower, 15K equipment
- **Tier 5** (50 reserves): ~600K manpower, 35K equipment
- **Tier 10** (100 reserves): ~2M manpower, 105K equipment

### Time Investment
- 90 days per 10 reserves = **900 days** (2.5 years) for full 100 reserves
- Factory penalty: -5% during recruitment
- Training penalty: +100% during recruitment

### Comparative Advantage
- **SOV**: Can get 100 from focuses (free, no time cost)
- **USA**: Reduced requirements with special flags
- **Others**: Must follow standard progression

This creates significant balance concerns for multiplayer and competitive gameplay.
