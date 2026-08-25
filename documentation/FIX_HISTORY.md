# Fix history - frozen 2026-08-23

The `Fix NN` numbering is retired: work is tracked by SUBJECT slug in `WORK.md`
(AGENTS.md, section 'Subjects and sessions'), and code comments carry `# [slug]` markers.
This table resolves every historical number to its commit and the subject that absorbed it
(mapping source: `tools/fix_slug_map.json`; commits: `tools/fix_registry.json`, frozen).
Known number collision: 28 was reused by two unrelated changes - the posture-verdict family
(offensive-posture) and the railway overseas fallback (railway-pathfinding); markers were
assigned per file. 54/55 follow the posture family.

| Fix | Commit | Subject | What it changed |
| --- | --- | --- | --- |
| 5 | `2bcf20d32` | railway-landwar | Fixes 5.7 |
| 11 | `lost: pre-convention (railway family). WHAT: always mark the best ...` | railway-pathfinding | pre-convention (railway family). WHAT: always mark the best port for upgrade, even when it |
| 14 | `lost: pre-convention (railway family). WHAT: handle claims on non-...` | railway-pathfinding | pre-convention (railway family). WHAT: handle claims on non-bordering countries - a landlo |
| 19 | `lost: pre-convention (railway family). WHAT: peace clears the rail...` | pc-queue | pre-convention (railway family). WHAT: peace clears the railway queue, with Fix 5 - `on_pe |
| 21 | `lost: pre-convention (railway family). WHAT: rail networks conside...` | railway-pathfinding | pre-convention (railway family). WHAT: rail networks consider ROOT-controlled provinces on |
| 22 | `lost: pre-convention (railway family). WHAT: run the overseas bran...` | railway-pathfinding | pre-convention (railway family). WHAT: run the overseas branch only when ROOT actually has |
| 23 | `lost: pre-convention (railway family). WHAT: pre-war pathfinding v...` | - | pre-convention (railway family). WHAT: pre-war pathfinding validation - a pre-war target s |
| 24 | `128cc7995` | railway-pathfinding | fix(ai): AIFC validity scope leak; rebuild lend-lease relief as per-archetype pull |
| 25 | `128cc7995` | railway-pathfinding | fix(ai): AIFC validity scope leak; rebuild lend-lease relief as per-archetype pull |
| 26 | `lost: pre-convention (railway family), 14 comment sites. WHAT: dis...` | railway-pathfinding | pre-convention (railway family), 14 comment sites. WHAT: distance-limited port search, rep |
| 27 | `128cc7995` | railway-pathfinding | fix(ai): AIFC validity scope leak; rebuild lend-lease relief as per-archetype pull |
| 28 | `4ffb8e442` | offensive-posture | Gate AI front execution on a weekly offensive posture verdict |
| 29 | `3c55b9d17` | railway-landwar | fix(ai): make land-war railway construction actually queue projects (Fix 29/29b) |
| 30 | `84528ae47` | railway-landwar | fix(ai): revive supply-line construction (Fix 30 - R9, campaign 66d6b53c) |
| 31 | `9778316f2` | aifc | fix(ai): AIFC sector validity never held - encoded id vs plain id (Fix 31, R1) |
| 32 | `76dde84ed` | amphibious-invasion | fix(ai): invasion penalty finally expires + Husky at intended size (Fix 32) |
| 33 | `4f2e00cbc` | amphibious-invasion | fix(ai): purge dead invasion-size code + revert Husky doubling (Fix 33) |
| 34 | `a3c2ef1a4` | pc-queue | fix(ai): let the PC stall sweep reach short queues + stop feeding hostile-state projects ( |
| 35 | `a03fc502b` | - | fix(ai): warbond ladder retries after dead-ending at fatigue 0 (Fix 35) |
| 36 | `b74f91889` | - | fix(ai): cap Nero-decree port demolition at 4 levels, floor 3 (Fix 36) |
| 37 | `506d670de` | uk-air-basing | fix(ai): unlock allied air-base funding in the PC system (Fixes 37-38) |
| 38 | `506d670de` | uk-air-basing | fix(ai): unlock allied air-base funding in the PC system (Fixes 37-38) |
| 39 | `d729372f9` | overextension-brake | feat(ai): industrial overextension brake with refinery substitution (Fix 39) |
| 40 | `5c85cd41a` | refineries | fix(ai): unlock the PC refinery strategies for import-strangled countries (Fix 40) |
| 41 | `f4ef2b059` | pc-queue | feat(ai): PC anti-starvation overtake lane + priority rebanding (Fix 41) |
| 42 | `1b08151df` | refineries | fix(ai): repair the refinery bid protocol (Fixes 42-44) |
| 43 | `5470cec6b` | aifc | @ feat(ai): capability-based AIFC and posture deactivation gates (Fix 43) |
| 44 | `1b08151df` | refineries | fix(ai): repair the refinery bid protocol (Fixes 42-44) |
| 45 | `60c7d8f3c` | refineries | fix(ai): retreat on the variant the bid opened (Fix 45) |
| 46 | `5d97e45d3` | uk-air-basing | fix(ai): fund UK air basing and un-share the air-base slot budget (Fixes 46-47) |
| 47 | `5d97e45d3` | equipment-selection | fix(ai): fund UK air basing and un-share the air-base slot budget (Fixes 46-47) |
| 48 | `88e516780` | equipment-selection | feat(ai): add efficiency-aware equipment selection (Fixes 46-50) |
| 49 | `88e516780` | equipment-selection | feat(ai): add efficiency-aware equipment selection (Fixes 46-50) |
| 50 | `88e516780` | equipment-selection | feat(ai): add efficiency-aware equipment selection (Fixes 46-50) |
| 51 | `a2744825d` | equipment-selection | fix(ai): move equipment selection to the production-line layer (Fix 51) |
| 52 | `fde1ede1e` | atlantic-naval | fix(ai): un-gate the Allied Atlantic escort plan for ENG and USA (Fix 52) |
| 53 | `e475eb8a5` | - | fix(ai): restore convoy-escort scoring and un-invert its threshold (Fix 53) |
| 54 | `bfd9d2659` | offensive-posture | fix(ai): target front execution by posture verdict, not enemy tag (Fix 54) |
| 55 | `209b27419` | offensive-posture | fix(ai): give the posture equipment gate hysteresis (Fix 55) + WA_TLM v6 |
| 56 | `a7a53aafd` | aifc | fix(ai): require an army before AIFC hands out a schwerpunkt (Fix 56) |
| 57 | `16cd27e87` | equipment-selection | fix(ai): block dead-end equipment research, cover the Comet (Fixes 57-58) |
| 58 | `16cd27e87` | equipment-selection | fix(ai): block dead-end equipment research, cover the Comet (Fixes 57-58) |
| 59 | `a73678785` | atlantic-naval | fix(ai): rebuild the Allied Atlantic naval plan (Fixes 59-63) |
| 60 | `a73678785` | atlantic-naval | fix(ai): rebuild the Allied Atlantic naval plan (Fixes 59-63) |
| 61 | `a73678785` | atlantic-naval | fix(ai): rebuild the Allied Atlantic naval plan (Fixes 59-63) |
| 62 | `a73678785` | atlantic-naval | fix(ai): rebuild the Allied Atlantic naval plan (Fixes 59-63) |
| 63 | `a73678785` | atlantic-naval | fix(ai): rebuild the Allied Atlantic naval plan (Fixes 59-63) |
| 64 | `97fb0059d` | equipment-selection | fix(ai): route SOV submarine output to cruiser submarines |
| 65 | `6625e65e5` | aifc | fix(ai): stop has_capitulated from locking allies out of AIFC and priority construction |
| 66 | `ce2cb53a0` | equipment-selection | feat(tlm): add probe families for R8, R43, R44 and R46 (v8-v11) |
| 67 | `lost: shipped 2026-08-14; the checklist item carried `<FILL AT COM...` | - | shipped 2026-08-14; the checklist item carried `<FILL AT COMMIT>` and it was never written |
| 68 | `6625e65e5` | aifc | fix(ai): stop has_capitulated from locking allies out of AIFC and priority construction |
| 69 | `lost: no commit message names it, but 7 comment sites do. WHAT: ha...` | equipment-selection | no commit message names it, but 7 comment sites do. WHAT: hard-gate the T-43 for the AI so |
| 70 | `496c4dae4` | equipment-selection | fix(ai): force the long-range La-5FN into existence, retire the legacy difficulty ideas |
| 71 | `lost: shipped 2026-08-14 with the same `<FILL AT COMMIT>` placehol...` | commonwealth-handoff | shipped 2026-08-14 with the same `<FILL AT COMMIT>` placeholder, never filled. WHAT: four  |
| 72 | `2937070f7` | pc-queue | fix(ai): re-price the PC shadow cost table, order UK air bases south-first, open logistics |
| 73 | `2937070f7` | pc-queue | fix(ai): re-price the PC shadow cost table, order UK air bases south-first, open logistics |
| 74 | `ce2cb53a0` | na-corridor | feat(tlm): add probe families for R8, R43, R44 and R46 (v8-v11) |
| 75 | `6625e65e5` | pc-queue | fix(ai): stop has_capitulated from locking allies out of AIFC and priority construction |
| 76 | `fc9fc5fab` | refineries | fix(ai): PC queue fairness (Fixes 77, 78) and proactive synth rubber (Fix 76) |
| 77 | `fc9fc5fab` | pc-queue | fix(ai): PC queue fairness (Fixes 77, 78) and proactive synth rubber (Fix 76) |
| 78 | `fc9fc5fab` | pc-queue | fix(ai): PC queue fairness (Fixes 77, 78) and proactive synth rubber (Fix 76) |
| 79 | `947750e42` | wa-tlm | feat(tlm): add the standing WA_TLM_pc_* family, v11 -> v15 |
| 80 | `8d3dd7afe` | refineries | fix(ai): let the synth-rubber pre-build reach the USA (Fix 80) |
| 81 | `7c4de2b53` | refineries | fix(ai): per-state refinery caps and HAR gate (Fix 81), strip stray BOMs |
| 82 | `1ff21fb22` | - | fix(ai): widen the Narvik landing of Weserübung to a 3-province pocket (Fix 82) |
| 83 | `26f704909` | landing-freeze | fix(ai): keep execute orders while a landing is still ahead on the ground (Fix 83) |
| 84 | `26f704909` | pc-queue | fix(ai): keep execute orders while a landing is still ahead on the ground (Fix 83) |
| 85 | `26f704909` | na-corridor | fix(ai): keep execute orders while a landing is still ahead on the ground (Fix 83) |
| 86 | `25bd2f132` | - | fix(ai): convoy escort reacts to any recent loss, not only sustained slaughter (Fix 86) |
| 87 | `cb1707f43` | uk-air-basing | feat(ai): UK air-basing throughput - second lane slot, headroom draw, nominal target (Fix  |
| 88 | `340294482` | pc-queue | feat(ai): breadth-first placement in the shared-slot construction queues (Fix 88) |
| 89 | `f737a32f8` | refineries | chore(ai): retire the proactive synthetic-rubber lane (Fixes 76/80; R48 superseded) |
| 90 | `ffd36bf0a` | refineries | fix(tools): registry follow-up for Fix 90b - can_afford deleted, type ids 24/25 registered |
| 91 | `f99d52d74` | convoys | fix(ai): Fix 91 - AI builds and shares convoys now that the free-convoy cheats are gone |
| 92 | `383f00398` | lend-lease-relief | fix(ai): Fix 92 - lend-lease surplus relief goes overland, per archetype (WA_TLM v18); cam |
| 93 | `93e6569d1` | raj-quit-india | fix(raj): Fix 93 - AI Raj suppresses Quit India on historical focus instead of going indep |
| 94 | `643872f0a` | amphibious-invasion | fix(ai): Fix 94 - Mulberry harbours get their D-Day call sites back |
| 95 | `45fdcb73d` | na-corridor | feat(ai): Fix 95 part 1 - PC building type 17 = supply_node |
| 96 | `01320e402` | med-axis-posture | feat(ai): Fix 96 - reactive Italian theatre (owner home defence + Axis ally guard), tag-fr |
| 97 | `1b437e397` | med-axis-posture | feat(ai): Fix 97 - East Africa is a theatre, tag-free (Allies commit when contested, Italy |
| 98 | `98896cf35` | med-axis-posture | feat(ai): Fix 98 - AI Italy attacks the Ethiopian mission's states on every aggressive rul |
| 99 | `63fbdfb7b` | med-axis-posture | feat(ai): Fix 99 - Axis Tunis bridge, tag-free (garrison a held Tunisian port when an enem |
| 100 | `2cf5f214f` | prospecting-coop | fix(ai): Fix 100 - a coal producer stops prospecting for allies it already supplies |
| 101 | `ed29adbe5` | prospecting-coop | fix(ai): Fix 101 - the other eight cooperative prospecting legs read ROOT's own sign |
| 102 | `lost: TWO claimants, and the implementing one is gone. `a5501e28b`...` | prospecting-coop | TWO claimants, and the implementing one is gone. `a5501e28b` "Fix 102 - the cooperative le |
| 103 | `f623c5d59` | na-corridor | fix(ai): Fix 103 - the overextension flag can release again, with a dwell against chatter |
| 104 | `7dc42fd75` | na-corridor | fix(pc): ally leg tests FUNDING, not authority (Fix 104) |
| 105 | `1bc0c8304` | overextension-brake | chore(ai): renumber my overextension fix 103 -> 105, the number was taken |
| 106 | `e447c3e47` | commonwealth-handoff | exp(ai): Allied minors back the coalition major - `support`, as an experiment (Fix 106) |
| 107 | `6f3c2432c` | na-corridor | feat(ai): Fix 107 - size the theatre corridor instead of building it flat |
| 108 | `4c0686a4f` | med-axis-posture | fix(ai): Fix 108 - a co-belligerent Ethiopia no longer kills Italy's North-African posture |
| 109 | `481bfa7ce` | med-axis-posture | feat(ai): Fix 109 - the whole eastern Adriatic shore sits behind the Otranto gate, not just Alb |
| 110 | `0cf3f60a7` | med-axis-posture | feat(ai): Fix 110 - Italy's southern-France reserve stands on the coast, not in the Massif Cent |
| 111 | `dea3b7467` | med-axis-posture | feat(ai): Fix 111 - Corsica gets a garrison of its own instead of borrowing the engine's |
| 112 | `5b13b8c50` | med-axis-posture | feat(ai): Fix 112 - Corsica's strategic region joins the mediterranean area |
| 113 | `cc5291eba` | na-corridor | feat(ai): Fix 113 - the North African corridor gets the invader's half |
| 114 | `685c36fb7` | na-corridor | feat(ai): Fix 114 - theatre air bases go to the contested edge first |
| 115 | `70e4549d3` | convoys | feat(ai): Fix 115 - only a coalition that crosses water runs a convoy arsenal |
| 116 | `66481b39a` | convoys | feat(ai): Fix 116 - the arsenal gate measures land access, not continents |
| 117 | `a04340a0d` | convoys | feat(ai): Fix 117 - the arsenal's coalition is the faction, not the war |
| 118 | `83c6d1983` | convoys | fix(ai): Fix 118 - a bare OVERLORD scope was voiding the arsenal gate entirely |
| 119 | `612dd9208` | med-axis-posture | fix(ai): Fix 119 - the Afrika Korps window: German armour toward Egypt until Barbarossa or a D-Day, Italian garrisons on the conquered ports |
| 120 | `bc90346af` | na-corridor | feat(ai): Fix 120 - theatre corridor connects before it consolidates (rail_connect band) |
| 121 | `bc90346af` | med-axis-posture | fix(ai): Fix 121 - the Afrika Korps expedition halved (Fix 119 retune, logistics saturation) |
| 122 | `bc90346af` | med-axis-posture | feat(ai): Fix 122 - Allied convoy raiding in the Mediterranean (29/269/327), major navies only |
| 123 | `bc90346af` | commonwealth-handoff | feat(ai): Fix 123 - the Pacific Commonwealth's home garrison is released while the Pacific is quiet |
| 124 | `bc90346af` | commonwealth-handoff | feat(ai): Fix 124 - East Africa delegated to the Indian army, Britain released for Egypt |
| 125 | `bc90346af` | commonwealth-handoff | fix(ai): Fix 125 - the Kuwait guard needs a threat to guard against |
| 126 | `bc90346af` | convoys | feat(ai): Fix 126 - a minor whose dockyards have nothing to build makes convoys for the coalition |
| 127 | `bc90346af` | commonwealth-handoff | feat(ai): Fix 127 - Allied tripwire on the Italian colonial frontiers before Italy declares |
| 128 | `bc90346af` | commonwealth-handoff | fix(ai): Fix 128 - RAJ reinforces El Alamein on its own verdict, without ENG standing down |
| 129 | `bc90346af` | commonwealth-handoff | fix(ai): Fix 129 - the Commonwealth dominions get the British screen / escort / light-cruiser designs |
| 130 | `bc90346af` | na-corridor | fix(ai): Fix 130 - inland corridor junction 13481, so Tobruk->5078 stops routing through an ENG-controlled state |
| 131 | `bc90346af` | med-axis-posture | feat(ai): Fix 131 - the Afrika Korps expedition no longer ends at Barbarossa |
| 132 | `bc90346af` | commonwealth-handoff | fix(ai): Fix 132 - occupying East Africa is not expelling the colonial power |
| 133 | `bc90346af` | med-axis-posture | fix(ai): Fix 133 - Italy defends the Tunis bridge on German ground, and at three times the size |
| 134 | `bc90346af` | commonwealth-handoff | fix(ai): Fix 134 - the Kuwait guard is sized against the force on the Gulf approach |
| 135 | `bc90346af` | na-corridor | refactor(ai): Fix 135 - one rail-route sizing model for the corridor and the land-war family, and the flat level 5 is gone |
| 136 | `ec6f63c62` | med-axis-posture | Mediterranean Fleet, shipped 2026-08-21. Two Faction-layer ALLIES blocks: `_med_fleet_alex |
| 137 | `0a11512e8` | med-axis-posture | fix(ai): Fix 137 - Afrika Korps front_unit_request 30 -> 40 |
| 27b | (comment-only number, no registry row) | railway-pathfinding | |
| 29b | (comment-only number, no registry row) | railway-landwar | |
| 53a | (comment-only number, no registry row) | atlantic-naval | |
| 53b | (comment-only number, no registry row) | atlantic-naval | |
| 87b | (comment-only number, no registry row) | uk-air-basing | |
| 90b | (comment-only number, no registry row) | refineries | |
