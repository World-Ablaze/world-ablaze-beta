----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Game


NDefines.NGame.END_DATE = "1952.1.1.1"
NDefines.NGame.DECISION_ALERT_TIMEOUT_DAYS = 7										-- Days left when player will be alerted about timing out events or decisions
NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 300										-- Days of client lag for decrease of gamespeed
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 100												-- Days of client lag for pause of gamespeed.
NDefines.NGame.EVENT_TIMEOUT_DEFAULT = 7											-- Default days before an event times out if not scripted
NDefines.NGame.GAME_SPEED_SECONDS = { 0.5, 0.2, 0.14, 0.06, 0.0 }					-- Game speed

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Diplomacy


NDefines.NDiplomacy.REVOKE_GUARANTEE_COST = 100
NDefines.NDiplomacy.GUARANTEE_COST = 10												-- Scale with the number of already guaranteed countries.

NDefines.NDiplomacy.LICENSE_ACCEPTANCE_OPINION_FACTOR = 0.1							-- Opinion modifier for acceptance of license production requests.
NDefines.NDiplomacy.LICENSE_ACCEPTANCE_PUPPET_BASE = 200							-- Acceptance modifier for puppets requesting production licenses.
NDefines.NDiplomacy.LICENSE_ACCEPTANCE_TECH_DIFFERENCE = 5 							-- Acceptance modifier for each year of technology difference.
NDefines.NDiplomacy.LICENSE_ACCEPTANCE_TECH_DIFFERENCE_BASE = 10    				-- Acceptance base for tech difference
NDefines.NDiplomacy.LICENSE_ACCEPTANCE_SAME_FACTION = 150							-- Acceptance modifier for being in the same faction

NDefines.NDiplomacy.JOIN_FACTION_LIMIT_CHANGE_AT_WAR = 0.75							-- if in defensive war this or your modifier is counted as limit to join factions (so if you have 80% join limit this now means you can join at 50%)

NDefines.NDiplomacy.VOLUNTEERS_PER_TARGET_PROVINCE = 0.005							-- Each province owned by the target country contributes this amount of volunteers to the limit.
NDefines.NDiplomacy.VOLUNTEERS_PER_COUNTRY_ARMY = 0.05								-- Each army unit owned by the source country contributes this amount of volunteers to the limit.

NDefines.NDiplomacy.TROOP_FEAR = 0 													-- Impact on troops on borders when deciding how willing a nation is to trade
NDefines.NDiplomacy.FLEET_FEAR = 0													-- Impact on troops on borders when deciding how willing a nation is to trade
NDefines.NDiplomacy.BASE_SEND_ATTACHE_COST = 50										-- Political power cost to send attache

NDefines.NDiplomacy.EMBARGO_THREAT_THRESHOLD = 100									-- Target-generated threat threshold to allow embargo (affected by modifiers)

NDefines.NDiplomacy.LL_TO_OVERLORD_AUTONOMY_DAILY_BASE = 0.0						-- If puppet lend leases equipment to overlord of at least same tech level as they have, they gain autonomy
NDefines.NDiplomacy.LL_TO_OVERLORD_AUTONOMY_DAILY_FACTOR = 0.0						-- If puppet lend leases equipment to overlord of at least same tech level as they have, they gain autonomy
NDefines.NDiplomacy.LL_TO_PUPPET_AUTONOMY_DAILY_BASE = 0.0							-- If overlord lend leases equipment to puppet of higher tech level as they have, puppet losses autonomy
NDefines.NDiplomacy.LL_TO_PUPPET_AUTONOMY_DAILY_FACTOR = 0.0						-- If overlord lend leases equipment to puppet of higher tech level as they have, puppet losses autonomy

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Politics


NDefines.NPolitics.ARMY_LEADER_COST = 2												-- cost for recruiting new leaders, 'this value' * number_of_existing_leaders_of_type
NDefines.NPolitics.NAVY_LEADER_COST = 2												-- command power cost for recruiting new leaders, 'this value' * number_of_existing_leaders_of_type
NDefines.NPolitics.ARMY_LEADER_MAX_COST = 80										-- max cost BEFORE modifiers
NDefines.NPolitics.NAVY_LEADER_MAX_COST = 80										-- max cost BEFORE modifiers


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Trade


NDefines.NTrade.BASE_TRADE_FACTOR = 55												-- This is the base trade factor
NDefines.NTrade.RELATION_TRADE_FACTOR = 2											-- Trade factor is modified by Opinion value times this
NDefines.NTrade.DISTANCE_TRADE_FACTOR = -0.005										-- Trade factor is modified by distance times this
NDefines.NTrade.PARTY_SUPPORT_TRADE_FACTOR = 0										-- Trade factor bonus at the other side having 100 % party popularity for my party
NDefines.NTrade.ANTI_MONOPOLY_TRADE_FACTOR = 0										-- This is added to the factor value when anti-monopoly threshold is exceeded


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Characters


NDefines.NCharacter.OFFICER_CORP_ADVISOR_ENTRIES_IN_MENU = { "high_command", "theorist", "army_theorist", "navy_theorist", "air_theorist", "army_chief", "air_chief", "navy_chief" }
--NDefines.NCharacter.DEFAULT_PP_COST_FOR_POLITICAL_ADVISOR = 100
NDefines.NCharacter.ADVISOR_PROMOTION_COST = 5										-- Cost to promote someone to advisor
NDefines.NCharacter.SPECIALIST_ADVISOR_MIN_RANK = 3
NDefines.NCharacter.EXPERT_ADVISOR_MIN_RANK = 5
NDefines.NCharacter.GENIUS_ADVISOR_MIN_RANK = 7

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Country



NDefines.NCountry.SUPPLY_FROM_DAMAGED_INFRA = 0.01              					-- damaged infrastructure counts as this in supply calcs
NDefines.NCountry.SUPPLY_PATH_MAX_DISTANCE = 15		    							-- When supply route reach more than X nodes the manpower+equipment delivery speed reach 100% penalty.

NDefines.NCountry.INVASION_REPORT_EXPERATION_DAYS = 30								-- Invasion experation days
NDefines.NCountry.SUPPLY_CONVOY_FACTOR = 0.15										-- How many convoys each supply needs
NDefines.NCountry.CONVOY_RANGE_FACTOR = 1.1                     				    -- how much range affects convoy need
NDefines.NCountry.FUEL_LEASE_CONVOY_RATIO = 0.00005									-- num convoys needed per fuel land lease

NDefines.NCountry.SUPPLY_PORT_LEVEL_THROUGHPUT = 3			    					-- supply throughput per level of naval base
NDefines.NCountry.EVENT_PROCESS_OFFSET = 7											-- Events are checked every X day per country or state (1 is ideal, but CPU heavy)

NDefines.NCountry.AIR_SUPPLY_CONVERSION_SCALE = 0.01								-- Conversion scale for planes to air supply
NDefines.NCountry.AIR_SUPPLY_DROP_EXPIRATION_HOURS = 24								-- Air drop length after being dropped

NDefines.NCountry.REINFORCEMENT_EQUIPMENT_DELIVERY_SPEED = 0.1						-- Modifier for army equipment reinforcement speed

NDefines.NCountry.RESISTANCE_STRENGTH_FROM_VP = 0.0015								-- How much strength ticking speed gives each VP score

NDefines.NCountry.POLITICAL_POWER_CAP = 5000.0

NDefines.NCountry.MAJOR_MIN_FACTORIES = 70											-- need at least these many factories to become a major

NDefines.NCountry.BASE_FUEL_GAIN_PER_OIL = 1.1										-- base amount of fuel gained hourly per excess oil
NDefines.NCountry.STARTING_FUEL_RATIO = 0.8											-- starting fuel ratio compared to max fuel for countries

NDefines.NCountry.GIE_CAPITULATION_WARSCORE_LEGITIMACY_FACTOR = 4.0 				--Multiplies accumulated warscore with this factor for part of starting legitimacy.
NDefines.NCountry.GIE_EXILE_AIR_START_EXPERIENCE = 300	 							--Starting experience for exile airwings
NDefines.NCountry.GIE_ESCAPING_DIVISIONS_XP_BOOST = 50.0
NDefines.NCountry.GIE_ESCAPING_DIVISIONS_EQUIPMENT_RATIO = 0.8 						-- Base equipment ratio on escaped troops.
NDefines.NCountry.GIE_ESCAPING_DIVISIONS_AMOUNT_RATIO = 0.005 						-- Ratio on amount of divisions that escapes. Scales with starting legitimacy

NDefines.NCountry.VICTORY_POINTS_IMPORTANCE_FACTOR = 50.0							-- State victory points importance factor for AI and calculations
NDefines.NCountry.ATTACHE_XP_SHARE = 0.15											-- Country received xp from attaches

NDefines.NCountry.SURRENDER_LIMIT_REDUCTION_PER_COLLABORATION = 0.1 				--each percent of collaboration will lower surrender limit by this percentage
NDefines.NCountry.NUM_DAYS_TO_FULLY_DELETE_STOCKPILED_EQUIPMENT = 365				-- time in days to fully delete equipments from stockpile. when you delete an equipment, they go to a temporary hidden pool which still can be seized

NDefines.NCountry.SPECIAL_FORCES_CAP_BASE = 0.02									-- Max ammount of special forces battalions is total number of non-special forces battalions multiplied by this and modified by a country modifier
NDefines.NCountry.SPECIAL_FORCES_CAP_MIN = 10										-- You can have a minimum of this many special forces battalions, regardless of the number of non-special forces battalions you have, this can also be modified by a country modifier

NDefines.NCountry.BASE_MOBILIZATION_SPEED = 0.01									-- Base speed of manpower mobilization  #in 1/1000 of 1 %

NDefines.NCountry.WAR_SUPPORT_TENSION_IMPACT = 0									-- Total impact of world tension
NDefines.NCountry.STATE_VALUE_NON_CORE_STATE_FRACTION = 1.0							-- If a state is not a core we assume we will get 50% of the factory slots

NDefines.NCountry.BOMBING_WAR_SUPPORT_PENALTY_SCALE = -0.00015 						-- Scaling of bomber damage to war support impact, will be added weekly as a war support penalty
NDefines.NCountry.MAX_BOMBING_WEEKLY_WAR_SUPPORT_PENALTY = -0.005					-- Max penalty that will gained per week from bomber's damage
NDefines.NCountry.BOMBING_WEEKLY_WAR_SUPPORT_PENALTY_DECAY = 0.002					-- Weekly decay of bomber damage war support penalty
NDefines.NCountry.MAX_BOMBING_WAR_SUPPORT_IMPACT = -0.2								-- Max total penalty from bomber's damage

NDefines.NCountry.CONVOYS_BEING_RAIDED_WAR_SUPPORT_PENALTY_SCALE = -0.01			-- Scaling of trade convoy raided to war support impact, will be added weekly as a war support penalty
NDefines.NCountry.MAX_CONVOYS_BEING_RAIDED_WEEKLY_WAR_SUPPORT_PENALTY = -0.01		-- Max penalty that will gained per week from trade convoy raided
NDefines.NCountry.CONVOYS_BEING_RAIDED_WEEKLY_WAR_SUPPORT_PENALTY_DECAY = 0.025	-- Weekly decay of trade convoy raided war support penalty
NDefines.NCountry.MAX_CONVOYS_BEING_RAIDED_WAR_SUPPORT_IMPACT = -0.3				-- Max total penalty from trade convoy raided

NDefines.NCountry.MIN_FOCUSES_FOR_CONTINUOUS = 60									-- Focuses needed to unlock continuous focuses

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Buildings


NDefines.NBuildings.NAVALBASE_REPAIR_MULT = 0.1										-- Each level of navalbase building repairs X strength. The value is spread on all ships needed reparation. Fe Navalbase lvl 5 x 0.5 str repair = 2.5 str repaired over 10 ships, so each ship repair hourly 0.25 str.
NDefines.NBuildings.BASE_FACTORY_REPAIR = 0.3										-- Default repair rate before factories are taken into account
NDefines.NBuildings.BASE_FACTORY_REPAIR_FACTOR = 2.0								-- Factory speed modifier when repairing.

NDefines.NBuildings.DESTRUCTION_COOLDOWN_IN_WAR = 180								-- Number of days cooldown between removal of buildings in war times

NDefines.NBuildings.ANTI_AIR_SUPERIORITY_MULT = 2.0									-- How much air superiority reduction to the enemy does our AA guns? Normally each building level = -1 reduction. With this a 5.0 multiplier.
NDefines.NBuildings.MAX_BUILDING_LEVELS = 40										-- Max levels a building can have.
NDefines.NBuildings.MAX_SHARED_SLOTS = 50											-- Max slots shared by factories
NDefines.NBuildings.SABOTAGE_FACTORY_DAMAGE = 50.0									-- How much damage takes a factory building in sabotage when state is occupied. Damage is mult by (1 + resistance strength), i.e. up to 2 x base value.

NDefines.NBuildings.AIRBASE_CAPACITY_MULT = 100										-- Each level of airbase building multiplied by this, gives capacity (max operational value). Value is int. 1 for each airplane.

NDefines.NBuildings.OWNER_CHANGE_EXTRA_SHARED_SLOTS_FACTOR = 1

NDefines.NBuildings.INFRASTRUCTURE_RESOURCE_BONUS = 0.1								-- multiplactive resource bonus for each level of (non damaged) infrastructure
NDefines.NBuildings.SUPPLY_ROUTE_RESOURCE_BONUS = 0.1  								-- multiplicative resource bonus for having a railway/naval connection to the capital

NDefines.NBuildings.MAX_BUILDING_LEVELS = 45  										-- Max levels a building can have.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Production

NDefines.NProduction.BASE_FACTORY_SPEED = 2.5 										-- Base factory speed multiplier (how much hoi3 style IC each factory gives).
NDefines.NProduction.BASE_FACTORY_SPEED_MIL = 2.5 									-- Base factory speed multiplier (how much hoi3 style IC each factory gives).
NDefines.NProduction.BASE_FACTORY_SPEED_NAV = 4.2					 				-- Base factory speed multiplier (how much hoi3 style IC each factory gives).

NDefines.NProduction.LICENSE_EQUIPMENT_BASE_SPEED = -0.25							-- base MIC speed modifier for licensed equipment
NDefines.NProduction.LICENSE_EQUIPMENT_SPEED_NOT_FACTION = -0.25					-- MIC speed modifier for licensed equipment for not being in faction
NDefines.NProduction.LICENSE_EQUIPMENT_TECH_SPEED_PER_YEAR = 0						-- MIC speed modifier for licensed equipment for each year of difference between actual and latest equipment
NDefines.NProduction.LICENSE_EQUIPMENT_TECH_SPEED_MAX_YEARS = 1						-- Maximum years for MIC speed modifier

NDefines.NProduction.CAPITULATE_STOCKPILES_RATIO = 0.7 								-- How much equipment from deployed divisions will be transferred on capitulation

NDefines.NProduction.MAX_EQUIPMENT_RESOURCES_NEED = 6 								-- Max number of different strategic resources an equipment can be dependent on.

NDefines.NProduction.BASE_FACTORY_EFFICIENCY_GAIN = 0.5								-- Base efficiency factor.
NDefines.NProduction.BASE_FACTORY_MAX_EFFICIENCY_FACTOR = 40 						-- Base max efficiency for factories expressed in %.
NDefines.NProduction.BASE_FACTORY_START_EFFICIENCY_FACTOR = 1						-- Base start efficiency for factories expressed in %.

NDefines.NProduction.BASE_FACTORY_EFFICIENCY_VARIANT_CHANGE_FACTOR = 80				-- Base factor for changing production variants in %.
NDefines.NProduction.BASE_FACTORY_EFFICIENCY_PARENT_CHANGE_FACTOR = 80				-- Base factor for changing production parent<->children in %.
NDefines.NProduction.BASE_FACTORY_EFFICIENCY_FAMILY_CHANGE_FACTOR = 70				-- Base factor for changing production with same family in %.
NDefines.NProduction.BASE_FACTORY_EFFICIENCY_ARCHETYPE_CHANGE_FACTOR = 20 			-- Base factor for changing production with same archetype in %.

NDefines.NProduction.EQUIPMENT_MODULE_ADD_XP_COST = 5.0								-- XP cost for adding a new equipment module in an empty slot when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_REPLACE_XP_COST = 5.0							-- XP cost for replacing one equipment module with an unrelated module when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_CONVERT_XP_COST = 3.0							-- XP cost for converting one equipment module to a related module when creating an equipment variant.
NDefines.NProduction.EQUIPMENT_MODULE_REMOVE_XP_COST = 2.0							-- XP cost for removing an equipment module and leaving the slot empty when creating an equipment variant.

NDefines.NProduction.LICENSE_IC_COST_YEAR_INCREASE = 0.25							-- IC cost equipment for every year of equipment after 1936

NDefines.NProduction.CONVERSION_SPEED_BONUS = 3.0									-- Modifier to the production speed when converting equipment
NDefines.NProduction.MIN_NAVAL_EQUIPMENT_CONVERSION_IC_COST_FACTOR = 0.2			-- Fraction of the hull industry cost which is always included in the refitting cost.
NDefines.NProduction.MIN_LAND_EQUIPMENT_CONVERSION_IC_COST_FACTOR = 0.9				-- Fraction of the chassis industry cost which is always included in the conversion cost.
NDefines.NProduction.MIN_NAVAL_EQUIPMENT_CONVERSION_RESOURCE_COST_FACTOR = 0.2		-- Minimum fraction of a naval equipment's strategic resource cost that any conversion will cost.
NDefines.NProduction.MIN_LAND_EQUIPMENT_CONVERSION_RESOURCE_COST_FACTOR = 0			-- Minimum fraction of a land equipment's strategic resource cost that any conversion will cost.

NDefines.NProduction.MIN_FIELD_TO_TRAINING_MANPOWER_RATIO = 0.15
NDefines.NProduction.MIN_POSSIBLE_TRAINING_MANPOWER = 30000							-- How many deployment lines minimum can be training

NDefines.NProduction.MAX_CIV_FACTORIES_PER_LINE = 20								-- Max number of factories that can be assigned a single production line.
NDefines.NProduction.BASE_LICENSE_IC_COST = 0										-- Base IC cost for lended license

NDefines.NProduction.DEFAULT_MAX_NAV_FACTORIES_PER_LINE = 10
NDefines.NProduction.CAPITAL_SHIP_MAX_NAV_FACTORIES_PER_LINE = 5
NDefines.NProduction.CONVOY_MAX_NAV_FACTORIES_PER_LINE = 15

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Operations

NDefines.NOperatives.AGENCY_CREATION_FACTORIES = 20									-- Number of factories used to create an intelligence agency
NDefines.NOperatives.MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES = 5					-- max operative slots gained from upgrades
NDefines.NOperatives.CONTROL_TRADE_MAX_INFLUENCE = 50.0								-- The maximum amount of trade influence that can be gained through the control trade mission
NDefines.NOperatives.BOOST_IDEOLOGY_MAX_DRIFT_BY_OPERATIVE = 0.10					-- the maximum drift an operative can cause, a negative value means no maximum
--NDefines.NOperatives.OPERATIVE_BASE_BOOST_IDEOLOGY = 0.02							-- Base amount of daily ideology drift provoked by an operative
NDefines.NOperatives.MIN_NATIONAL_COVERAGE_FOR_BOOST_IDEOLOGY = 0.01				-- Minimum network coverage required to start the mission (the code ensures that a network exists at all)
--NDefines.NOperatives.BOOST_IDEOLOGY_DEFENSE_FACTOR = 0.8							-- multiplied to the target's defense to get the amount of drift to remove from each operative's drift

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Resistance

NDefines.NResistance.GARRISON_MANPOWER_LOST_BY_ATTACK = 0.01 						-- Ratio of manpower lost by garrison at each attack on garrison (this number will be reduced by the hardness of garrison template)
NDefines.NResistance.MIN_DAMAGE_TO_GARRISONS_MODIFIER = 0.05						-- modifier that applies to losses from resistance attack to garrisons at most can be reduced to this amount

NDefines.NResistance.FOREIGN_MANPOWER_MIN_THRESHOLD = 500000000			 			-- The minimum number of Manpower that AI will accept to give at once, in order to avoid many weird little transfer.

NDefines.NResistance.RESISTANCE_ACTIVITY_CHANCE_AT_MAX_RESISTANCE = 0.200			-- sabotage

NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_OCCUPIED_CAPITULATED = 15.0 		-- resistance target modifier when the enemy is capitulated

NDefines.NResistance.RESISTANCE_TARGET_MODIFIER_STATE_VP = {						-- resistance target modifier pairs for vp. first entry is total vp in state and second entry is amount of target modifier that applies for that threshold
	0,   0.0, -- 0 - 5
	5,   10.0, -- 5 - 20
	20,  20.0, -- 20 - 50
	50,  30.0, -- 50 - ...
}


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Railways


NDefines.NRailwayGun.RAILWAY_GUN_RANGE = 15											-- The range of railway guns in pixels
NDefines.NRailwayGun.ATTACK_TO_FORTS_MODIFIER_FACTOR = 1.0							-- Forts modifier is calculated by multiplying railway gun attack value with this and dividing by 100
NDefines.NRailwayGun.ATTACK_TO_ENTRENCHMENT_MODIFIER_FACTOR = 1.39					-- Entrenchment modifier is calculated by multiplying railway gun attack value with this and dividing by 100
NDefines.NRailwayGun.ATTACK_TO_BOMBARDMENT_MODIFIER_FACTOR = 0						-- Bombardment modifier is calculated by multiplying railway gun attack value with this and dividing by 100


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Technology


NDefines.NTechnology.BASE_TECH_COST = 85											-- Base cost for a tech. multiplied with tech cost and ahead of time penalties
NDefines.NTechnology.BASE_YEAR_AHEAD_PENALTY_FACTOR = 4								-- Base year ahead penalty
NDefines.NTechnology.LICENSE_PRODUCTION_TECH_BONUS = 0								-- License production tech bonus

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Military
NDefines.NMilitary.FIELD_MARSHAL_DIVISIONS_CAP = 12									-- how many divisions a field marshall is limited to. 0 = inf, < 0 = blocked
NDefines.NMilitary.CORPS_COMMANDER_DIVISIONS_CAP = 12								-- how many divisions a corps commander is limited to. 0 = inf, < 0 = blocked
NDefines.NMilitary.FIELD_MARSHAL_ARMIES_CAP = 10									-- how many armies a field marshall is limited to. 0 = inf, < 0 = blocked
NDefines.NMilitary.GARRISON_ORDER_ARMY_CAP_FACTOR = 1.0								-- armies gets increased cap when they are garrisoned

NDefines.NMilitary.PROMOTE_LEADER_CP_COST = 20.0									-- cost of promoting a leader

NDefines.NMilitary.COMBAT_SUPPLY_LACK_ATTACKER_ATTACK = -0.20    					-- attack combat penalty for attacker if out of supply
NDefines.NMilitary.COMBAT_SUPPLY_LACK_ATTACKER_DEFEND = -0.40     					-- defend combat penalty for attacker if out of supply
NDefines.NMilitary.COMBAT_SUPPLY_LACK_DEFENDER_ATTACK = -0.40     					-- attack combat penalty for defender if out of supply
NDefines.NMilitary.COMBAT_SUPPLY_LACK_DEFENDER_DEFEND = -0.20     					-- defend combat penalty for defender if out of supply

NDefines.NMilitary.BASE_COMBAT_WIDTH = 90											-- base combat width
NDefines.NMilitary.ADDITIONAL_COMBAT_WIDTH = 30										-- more opened up by support attack

--NDefines.NMilitary.PLAN_COHESION_WEIGHTS = { 1.0, 20.0, 40.0 } 					-- for each cohesion setting, how keen on relocating from distance should we be? (default 1.0), higher weight = shorter max distance

NDefines.NMilitary.MIN_SUPPLY_CONSUMPTION = 0.01									-- minimum value of supply consumption that a unit can get

NDefines.NMilitary.EQUIPMENT_COMBAT_LOSS_FACTOR = 1.0	 	   						-- % of equipment lost to strength ratio in combat, so some % is returned if below 1

--NDefines.NMilitary.LAND_AIR_COMBAT_MAX_PLANES_PER_ENEMY_WIDTH = 1 				-- how many CAS/TAC can enter a combat depending on enemy width there

NDefines.NMilitary.PLANNING_DECAY = 0.001
NDefines.NMilitary.PLAYER_ORDER_PLANNING_DECAY = 0.03								-- Amount of planning lost due to player manual order
NDefines.NMilitary.PLANNING_GAIN = 0.01
NDefines.NMilitary.PLANNING_MAX = 0.1                           					-- can get more from techs
NDefines.NMilitary.DIG_IN_FACTOR = 0.01						   						-- bonus factor for each dug-in level

NDefines.NMilitary.FRONT_MIN_PATH_TO_REDEPLOY = 12									-- If a units path is at least this long to reach its front location, it will strategically redeploy.

NDefines.NMilitary.ZERO_ORG_MOVEMENT_MODIFIER = -0.25								-- speed impact at 0 org.

NDefines.NMilitary.ACCLIMATIZATION_SPEED_GAIN = 0.05								-- A variable used to balance the overall speed of gaining the acclimatization

NDefines.NMilitary.BASE_DIVISION_BRIGADE_GROUP_COST = 20							--Base cost to unlock a regiment slot,
NDefines.NMilitary.BASE_DIVISION_BRIGADE_CHANGE_COST = 5							--Base cost to change a regiment column.
NDefines.NMilitary.BASE_DIVISION_SUPPORT_SLOT_COST = 1 								--Base cost to unlock a support slot

NDefines.NMilitary.MAX_DIVISION_BRIGADE_HEIGHT = 4									-- Max height of regiments in division designer.
NDefines.NMilitary.MAX_DIVISION_SUPPORT_WIDTH = 2									-- Max width of support in division designer.
NDefines.NMilitary.MAX_DIVISION_SUPPORT_HEIGHT = 5									-- Max height of support in division designer.

NDefines.NMilitary.UNIT_LEADER_ASSIGN_TRAIT_COST = 5								-- cost to assign a new trait to a unit leader
NDefines.NMilitary.ARMY_STRATEGIC_DEPLOYMENT_FUEL_MULT = 0.0						-- fuel consumption ratio while doing strategic deployment
NDefines.NMilitary.STRATEGIC_SPEED_INFRA_BASE = 3.0
NDefines.NMilitary.STRATEGIC_SPEED_INFRA_MAX = 5.0
NDefines.NMilitary.STRATEGIC_SPEED_RAIL_BASE = 15.0
NDefines.NMilitary.STRATEGIC_SPEED_RAIL_MAX = 25.0
--NDefines.NMilitary.PLAN_EXECUTE_CAREFUL_LIMIT = 10								-- When looking for an attach target, this score limit is required in the battle plan to consider province for attack
--NDefines.NMilitary.PLAN_EXECUTE_CAREFUL_MAX_FORT = 9								-- If execution mode is set to careful, units will not attack provinces with fort levels greater than or equal to this

NDefines.NMilitary.BATALION_CHANGED_EXPERIENCE_DROP = 0.75							-- Division experience drop if unit has different batalion

NDefines.NMilitary.MAX_ARMY_EXPERIENCE = 5000										--Max army experience a country can store
NDefines.NMilitary.MAX_NAVY_EXPERIENCE = 5000										--Max navy experience a country can store
NDefines.NMilitary.MAX_AIR_EXPERIENCE = 5000										--Max air experience a country can store

NDefines.NMilitary.UNIT_EXPERIENCE_PER_COMBAT_HOUR = 0.00060
NDefines.NMilitary.FIELD_EXPERIENCE_SCALE = 0.0015
NDefines.NMilitary.FIELD_EXPERIENCE_MAX_PER_DAY = 1									-- Most xp you can gain per day

NDefines.NMilitary.ARMOR_VS_AVERAGE = 0.4			                				-- how to weight in highest armor & pen vs the division average

NDefines.NMilitary.LAND_COMBAT_STR_ARMOR_DEFLECTION_FACTOR = 0.5					-- damage reduction if armor outclassing enemy
NDefines.NMilitary.LAND_COMBAT_ORG_ARMOR_DEFLECTION_FACTOR = 0.5					-- damage reduction if armor outclassing enemy

NDefines.NMilitary.PIERCING_THRESHOLDS = {											-- Our piercing / their armor must be this value to deal damage fraction equal to the index in the array below [higher number = higher penetration]. If armor is 0, 1.00 will be returned.
	1.25,
	1.1,
	1.0,
	0.9,
	0.75,
	0.00, --there isn't much point setting this higher than 0
}
NDefines.NMilitary.PIERCING_THRESHOLD_DAMAGE_VALUES = {								-- 0 armor will always receive maximum damage (so add overmatching at your own peril). the system expects at least 2 values, with no upper limit.
	1.00,
	0.90,
	0.80,
	0.70,
	0.60,
	0.50,
}

NDefines.NMilitary.LAND_EQUIPMENT_BASE_COST = 4										-- Cost in XP to upgrade a piece of equipment one level is base + ( total levels * ramp )
NDefines.NMilitary.LAND_EQUIPMENT_RAMP_COST = 2
NDefines.NMilitary.NAVAL_EQUIPMENT_BASE_COST = 4
NDefines.NMilitary.NAVAL_EQUIPMENT_RAMP_COST = 2
NDefines.NMilitary.AIR_EQUIPMENT_BASE_COST = 4
NDefines.NMilitary.AIR_EQUIPMENT_RAMP_COST = 2

NDefines.NMilitary.PLAN_SPREAD_ATTACK_WEIGHT = 3									-- The higher the value, the less it should crowd provinces with multiple attacks.

NDefines.NMilitary.NON_CORE_SUPPLY_SPEED = -0.7				    					-- we are not running on our own VP supply so need to steal stuff along the way
NDefines.NMilitary.LAND_COMBAT_COLLATERAL_FACTOR = 0.003							-- Factor to scale collateral damage to infra and forts with.

NDefines.NMilitary.ATTRITION_DAMAGE_ORG = 0.08					   					-- damage from attrition to Organisation
NDefines.NMilitary.MAX_OUT_OF_SUPPLY_DAYS = 7 				   						-- how many days of shitty supply until max penalty achieved
NDefines.NMilitary.OUT_OF_SUPPLY_ATTRITION = 2.0                					-- max attrition when out of supply
NDefines.NMilitary.OUT_OF_SUPPLY_MORALE = 0                  						-- max org regain reduction from supply
NDefines.NMilitary.OUT_OF_SUPPLY_SPEED = -0.4                   					-- max speed reduction from supply
NDefines.NMilitary.COMBAT_SUPPLY_LACK_IMPACT = -0.6									-- combat penalty if out of supply

NDefines.NMilitary.INFRA_ORG_IMPACT = 0.25											-- scale factor of infra on org regain.

NDefines.NMilitary.STRATEGIC_REDEPLOY_ORG_RATIO = 0.1								-- Ratio of max org while strategic redeployment

NDefines.NMilitary.PARACHUTE_COMPLETE_ORG = 0.6									    -- Organisation value (in %) after unit being dropped, regardless if failed, disrupted, or successful.
NDefines.NMilitary.PARACHUTE_ORG_REGAIN_PENALTY_DURATION = 24						-- penalty in org regain after being parachuted. Value is in hours.

NDefines.NMilitary.SLOWEST_SPEED = 3

NDefines.NMilitary.NUKE_MIN_DAMAGE_PERCENT = 0.7									-- Minimum damage from nukes as a percentage of current strength/organisation
NDefines.NMilitary.NUKE_MAX_DAMAGE_PERCENT = 0.95									-- Minimum damage from nukes as a percentage of current strength/organisation

NDefines.NMilitary.USE_MULTIPLICATIVE_ORG_LOSS_WHEN_MOVING = false
NDefines.NMilitary.HOURLY_ORG_MOVEMENT_IMPACT = -0.5								-- how much org is lost every hour while moving an army.
NDefines.NMilitary.ORG_LOSS_FACTOR_ON_CONQUER = 0.25              					-- percentage of (max) org loss on takign enemy province

NDefines.NMilitary.LEND_LEASE_FIELD_EXPERIENCE_SCALE = 0.000						-- Experience scale for lend leased equipment used in combat.
NDefines.NMilitary.SUPPLY_GRACE = 168												-- troops always carry 10 days of food and supply (HARDCODED, DO NOT CHANGE)
NDefines.NMilitary.SUPPLY_GRACE_MAX_REDUCE_PER_HOUR = 1         					-- supply grace is not decreased instantly when it is buffed temporarily and buff is removed

NDefines.NMilitary.ATTRITION_EQUIPMENT_LOSS_CHANCE = 0.03							-- Chance for loosing equipment when suffer attrition. Scaled up the stronger attrition is. Then scaled down by equipment reliability.
NDefines.NMilitary.ATTRITION_EQUIPMENT_PER_TYPE_LOSS_CHANCE = 0.1 					-- Chance for loosing equipment when suffer attrition. Scaled up the stronger attrition is. Then scaled down by equipment reliability.

NDefines.NMilitary.ARMY_EXP_BASE_LEVEL = 10

NDefines.NMilitary.TRAINING_MAX_LEVEL = 15
NDefines.NMilitary.DEPLOY_TRAINING_MAX_LEVEL = 10
NDefines.NMilitary.UNIT_EXP_LEVELS = { 0.10,	0.12,	0.13,	0.14,	0.15,	0.16,	0.17,	0.18,	0.19,	0.2,	0.25,	0.3,	0.35,	0.4,	0.45,	0.5,	0.55,	0.6,	0.65,	0.7,	0.75,	0.8,	0.85,	0.9,	0.95 }		-- Experience needed to progress to the next level
NDefines.NMilitary.EXPERIENCE_COMBAT_FACTOR = 0.03
NDefines.NMilitary.TRAINING_EXPERIENCE_SCALE = 30.0
NDefines.NMilitary.TRAINING_ATTRITION = 0.12
NDefines.NMilitary.TRAINING_MIN_STRENGTH = 0.95										-- if strength is less than this, the unit will pause training until it's been reinforced
NDefines.NMilitary.UNIT_EXPERIENCE_SCALE = 0.3

NDefines.NMilitary.RIVER_CROSSING_PENALTY = -0.3                					-- small river crossing
NDefines.NMilitary.RIVER_CROSSING_PENALTY_LARGE = -0.6								-- large river crossing
NDefines.NMilitary.RIVER_CROSSING_SPEED_PENALTY = -0.25								-- small river crossing
NDefines.NMilitary.RIVER_CROSSING_SPEED_PENALTY_LARGE = -0.5						-- large river crossing

NDefines.NMilitary.RETREAT_SPEED_FACTOR = 1.5              						    -- speed bonus when retreating
NDefines.NMilitary.BASE_FORT_PENALTY = -0.18						 				-- fort penalty

NDefines.NMilitary.ENEMY_AIR_SUPERIORITY_IMPACT = -0.4      						-- effect on defense due to enemy air superiorty
--NDefines.NMilitary.ENEMY_AIR_SUPERIORITY_SPEED_IMPACT = -0.5				   		-- effect on speed due to enemy air superiority

NDefines.NMilitary.COMBAT_MOVEMENT_SPEED = 0.8										-- speed reduction base modifier in combat

NDefines.NMilitary.TRAINING_ORG = 0

NDefines.NMilitary.FUEL_CAPACITY_DEFAULT_HOURS = 240               					-- default capacity if not specified
NDefines.NMilitary.ARMY_COMBAT_FUEL_MULT = 0										-- fuel consumption ratio in combat (plus ARMY_MOVEMENT_FUEL_MULT if you are also moving. ie offensive combat)

NDefines.NMilitary.BASE_CAPTURE_EQUIPMENT_RATIO = 0.04								-- after a successful land combat, ratio of the equipments that are being captured/salvaged from enemy's lost equipment
--NDefines.NMilitary.REINFORCE_CHANCE = 0.1                	   						-- base chance to join combat from back line when empty

NDefines.NMilitary.NON_CORE_SUPPLY_AIR_SPEED = -0.4			   						-- we are not running on our own VP supply so need to steal stuff along the way, a bit less due to air supply

NDefines.NMilitary.LAND_AIR_COMBAT_STR_DAMAGE_MODIFIER = 0.015    					-- air global strength damage modifier from CAS
NDefines.NMilitary.LAND_AIR_COMBAT_ORG_DAMAGE_MODIFIER = 0.025    					-- air global org damage modifier from CAS

NDefines.NMilitary.UNIT_LEADER_INITIAL_TRAIT_SLOT = { 								-- trait slot for 0 level leader
	1.0, -- field marshal
	1.0, -- corps commander
	1.0, -- navy general
	0.0, -- operative
}
NDefines.NMilitary.UNIT_LEADER_TRAIT_SLOT_PER_LEVEL = { 							-- num extra traits on each level
	1.0, -- field marshal
	1.0, -- corps commander
	1.0, -- navy general
	1.0, -- operative
}
NDefines.NMilitary.UNIT_LEADER_USE_NONLINEAR_XP_GAIN = false     				    -- Whether unit leader XP gain is scaled by 1/<nr_of_traits>
NDefines.NMilitary.DIVISIONAL_COMMANDER_TRAIT_XP_REQUIREMENT = 500.0				--Get a trait if any valid options & xp gained >= this
NDefines.NMilitary.FIELD_OFFICER_PROMOTION_PENALTY = 0								--Amount of division experience lost when promoting a commander (reduced by modifiers)
--NDefines.NMilitary.GENERATE_AI_DIV_COMMAND_HISTORY_ENTRIES = false				--Should we generate history entries for the AI (may cause savegame bloat)
NDefines.NMilitary.NUM_DAYS_FOR_OPERATION_ENTRY = 30								--Number of days that a unit must have been on a particular active order instance to receive a history entry.


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Air


NDefines.NAir.LEND_LEASED_EQUIPMENT_EXPERIENCE_GAIN = 0.0							-- Value used for equipment

--NDefines.NAir.AIR_WING_XP_LEVELS = { 36, 72, 108, 144, 180, 216, 252, 288, 324, 360, 396, 432, 468, 504, 540, 576, 612, 648, 684, 720, 756, 792, 828, 864, 900 }		--Experience needed to progress to the next level

NDefines.NAir.CAPACITY_PENALTY = 2													-- scales penalty of having overcrowded bases.
NDefines.NAir.AIR_WING_MAX_SIZE = 200 												-- Max amount of airplanes in wing
NDefines.NAir.MISSION_EFFICIENCY_MULT_AT_LACK_OF_FUEL = 0.05		 				-- multiplier for mission efficiency when a base lacks fuel

NDefines.NAir.FIELD_EXPERIENCE_SCALE = 0.0002
NDefines.NAir.CLOSE_AIR_SUPPORT_EXPERIENCE_SCALE = 0.0005							-- How much the experinence gained by CAS is scaled

NDefines.NAir.AIR_WING_MAX_STATS_ATTACK = 10000										-- Max stats
NDefines.NAir.AIR_WING_MAX_STATS_DEFENCE = 10000
NDefines.NAir.AIR_WING_MAX_STATS_AGILITY = 10000
NDefines.NAir.AIR_WING_MAX_STATS_SPEED = 5000
NDefines.NAir.AIR_WING_MAX_STATS_BOMBING = 50000
NDefines.NAir.COMBAT_DAMAGE_SCALE = 0.75											-- Higher value = more shot down planes
NDefines.NAir.DETECT_CHANCE_FROM_RADARS = 0.75	 									-- How much the radars in area affects detection chance.

NDefines.NAir.AIR_WING_XP_LOSS_WHEN_KILLED = 240									--if a plane dies, the game assumes that a pilot with this amount of xp died and recalcs average.
NDefines.NAir.AIR_WING_XP_AIR_VS_AIR_COMBAT_GAIN = 1.0 								--Wings in combat gain extra XP

NDefines.NAir.COMBAT_BETTER_AGILITY_DAMAGE_REDUCTION = 1.60							-- How much the better agility (then opponent's) can reduce their damage to us.
NDefines.NAir.BIGGEST_AGILITY_FACTOR_DIFF = 3.0										-- biggest factor difference in agility for doing damage (caps to this)

NDefines.NAir.DISRUPTION_FACTOR = 0.5												-- multiplier on disruption damage to scale its effects on planes
NDefines.NAir.DISRUPTION_FACTOR_CARRIER = 1.0										-- multiplier on disruption damage to scale its effects on carrier vs carrier planes
NDefines.NAir.CARRIER_HOURS_DELAY_AFTER_EACH_COMBAT = 0								-- how often carrier planes do battle inside naval combat
NDefines.NAir.ACE_EARN_CHANCE_BASE = 0.005											-- Base chance % for ace pilot to be created. Happens only when successfully kill airplane/ship or damage the buildings.

NDefines.NAir.ACCIDENT_CHANCE_BASE = 0.25											-- Base chance % (0 - 100) for accident to happen. Reduced with higher reliability stat.
NDefines.NAir.ACCIDENT_CHANCE_BALANCE_MULT = 0.5									-- Multiplier for balancing how often the air accident really happens. The higher mult, the more often.
NDefines.NAir.ACCIDENT_EFFECT_MULT = 0.0005											-- Multiplier for balancing the effect of accidents

--NDefines.NAir.EFFICIENCY_REGION_CHANGE_DAILY_GAIN_DEFAULT = 0.1						-- Default how much efficiency to regain per day. Gain applied hourly.
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRUCK_DAMAGE_FACTOR = 0.02
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_FACTOR = 0.008
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_TRAIN_DAMAGE_DISRUPTION_MITIGATION = 3.0 	-- Multiply Train Damage by (Smooth / (Smooth + (Disruption * Mitigation)))
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_RAILWAY_DAMAGE_SPILL_FACTOR = 0.002 		-- Portion of train damage to additionally deal to railways
NDefines.NAir.AIR_WING_ATTACK_LOGISTICS_INFRA_DAMAGE_SPILL_FACTOR = 0.0 			-- Portion of truck damage to additionally deal to infrastructure

NDefines.NAir.CAS_NIGHT_ATTACK_FACTOR = 0.1						                    -- CAS damaged get multiplied by this in land combats at night
NDefines.NAir.ANTI_AIR_MAXIMUM_DAMAGE_REDUCTION_FACTOR = 0.50 						-- Maximum damage reduction factor applied to incoming air attacks against units with AA.
NDefines.NAir.AA_INDUSTRY_AIR_DAMAGE_FACTOR = -0.036									-- 5x levels = 60% defense from bombing

NDefines.NAir.BOMBING_TARGETING_RANDOM_FACTOR = 0.8									-- % of picking the wrong target
NDefines.NAir.AIR_WING_BOMB_DAMAGE_FACTOR = 3										-- Used to balance the damage done while bombing.
NDefines.NAir.BOMBING_PROV_BUILD_PRIO_SCALE = 2										-- Scale of the selected priority for provincial buildings
NDefines.NAir.BOMBING_STATE_BUILD_PRIO_SCALE = 2									-- Scale of the selected priority for state buildings
NDefines.NAir.ANTI_AIR_PLANE_DAMAGE_FACTOR = 0.3									-- Anti Air Gun Damage factor

NDefines.NAir.MISSION_COMMAND_POWER_COSTS = {  										-- command power cost per plane to create a mission
	0.0, -- AIR_SUPERIORITY
	0.0, -- CAS
	0.0, -- INTERCEPTION
	0.0, -- STRATEGIC_BOMBER
	0.0, -- NAVAL_BOMBER
	0.0, -- DROP_NUKE
	0.0, -- PARADROP
	0.0, -- NAVAL_KAMIKAZE
	0.0, -- PORT_STRIKE
	0.0, -- ATTACK_LOGISTICS
	0.1, -- AIR_SUPPLY
	0.0, -- TRAINING
	0.0, -- NAVAL_MINES_PLANTING
	0.0, -- NAVAL_MINES_SWEEPING
	0.0, -- RECON
	0.0, -- NAVAL_PATROL
}

NDefines.NAir.NAVAL_STRIKE_CARRIER_MULTIPLIER = 10.0							    -- damage bonus when planes are in naval combat where their carrier is present (and can thus sortie faster and more effectively)

NDefines.NAir.NAVAL_STRIKE_DAMAGE_TO_STR = 2.0										-- Balancing value to convert damage ( naval_strike_attack * hits ) to Strength reduction.
NDefines.NAir.NAVAL_STRIKE_DAMAGE_TO_ORG = 0.5										-- Balancing value to convert damage ( naval_strike_attack * hits ) to Organisation reduction.

NDefines.NAir.AIR_WING_COUNTRY_XP_FROM_TRAINING_FACTOR = 0.03						-- Factor on country Air XP gained from wing training
NDefines.NAir.INTERCEPTION_DISTANCE_SCALE = 100 									-- At this many pixels of path length, full interception efficiency is applied to air missions. Lerp from 0.
NDefines.NAir.INTERCEPTION_DAMAGE_SCALE = 1											-- Multiply the interception damage with this value. Works as a cap when interception distance is at maximum.



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Navy

NDefines.NNavy.NAVAL_COMBAT_AIR_SUB_DETECTION_MAX = 2
NDefines.NNavy.NAVAL_COMBAT_AIR_PLANE_COUNT_TO_SUB_DETECTION = 0.2					-- Factor applied to the number of active plane in a naval combat to deduce their contribution to sub detection

NDefines.NNavy.SUB_DETECTION_CHANCE_BASE = 1										-- to start spotting a submarine, a dice is rolled and checked if it succeeds this percentage. if not, that enemy sub force won't be spotted on this tick
NDefines.NNavy.SUB_DETECTION_CHANCE_BASE_SPOTTING_EFFECT = 0.5						-- effect of base spotting for initial spotting of pure submarine forces. this along with next value is added together and rolled against a random to start spotting
NDefines.NNavy.SUB_DETECTION_CHANCE_SPOTTING_SPEED_EFFECT = 1.0						-- effect of spotting speed for initial spotting of pure submarine forces. this along with prev value is added together and rolled against a random to start spotting
NDefines.NNavy.SUB_DETECTION_CHANCE_BASE_SPOTTING_POW_EFFECT = 1.5					-- effect of spotting speed will be powered by this for initial spotting of pure submarine forces. this along with prev value is added together and rolled against a random to start spotting

--NDefines.NNavy.NAVAL_COMBAT_AIR_SUB_DETECTION_EXTERNAL_FACTOR = 0.5					-- Factor applied to the stats of external air planes

NDefines.NNavy.DEPTH_CHARGE_STAT_FOR_SHIP_TO_BE_SUB_HUNTER = 12						-- amount of depth charge required for a ship to be considred a sub hunter and so good for convoy escort

NDefines.NNavy.NAVAL_INVASION_PREPARE_HOURS = 336									-- base hours needed to prepare an invasion

NDefines.NNavy.SHIP_TO_FLEET_ANTI_AIR_RATIO	= 0.05									-- total sum of fleet's anti air will be multiplied with this ratio and added to calculations anti-air of individual ships while air damage reduction
NDefines.NNavy.ANTI_AIR_POW_ON_INCOMING_AIR_DAMAGE = 0.2							-- received air damage is calculated using following: 1 - ( (ship_anti_air + fleet_anti_air * SHIP_TO_FLEET_ANTI_AIR_RATIO )^ANTI_AIR_POW_ON_INCOMING_AIR_DAMAGE ) * ANTI_AIR_MULT_ON_INCOMING_AIR_DAMAGE
NDefines.NNavy.ANTI_AIR_MULT_ON_INCOMING_AIR_DAMAGE	= 0.15
NDefines.NNavy.ANTI_AIR_TARGETING = 1.0               		                        -- how good ships are at hitting aircraft

NDefines.NNavy.REPAIR_AND_RETURN_PRIO_LOW = 0.2										-- % of total Strength. When below, navy will go to home base to repair.
NDefines.NNavy.REPAIR_AND_RETURN_PRIO_MEDIUM = 0.5									-- % of total Strength. When below, navy will go to home base to repair.
NDefines.NNavy.REPAIR_AND_RETURN_PRIO_HIGH = 0.8									-- % of total Strength. When below, navy will go to home base to repair.

NDefines.NNavy.REPAIR_AND_RETURN_PRIO_LOW_COMBAT = 0.2								-- % of total Strength. When below, navy will go to home base to repair (in combat).
NDefines.NNavy.REPAIR_AND_RETURN_PRIO_MEDIUM_COMBAT = 0.3							-- % of total Strength. When below, navy will go to home base to repair (in combat).
NDefines.NNavy.REPAIR_AND_RETURN_PRIO_HIGH_COMBAT = 0.6								-- % of total Strength. When below, navy will go to home base to repair (in combat).

NDefines.NNavy.REPAIR_AND_RETURN_AMOUNT_SHIPS_LOW = 0.2								-- % of total damaged ships, that will be sent for repair-and-return in one call.
NDefines.NNavy.REPAIR_AND_RETURN_AMOUNT_SHIPS_MEDIUM = 0.4							-- % of total damaged ships, that will be sent for repair-and-return in one call.
NDefines.NNavy.REPAIR_AND_RETURN_AMOUNT_SHIPS_HIGH = 0.7							-- % of total damaged ships, that will be sent for repair-and-return in one call.

NDefines.NNavy.REPAIR_AND_RETURN_UNIT_DYING_STR = 0.15								-- Str below this point is considering a single ship "dying", and a high priority to send to repair.

NDefines.NNavy.MIN_HIT_PROFILE_MULT = 0.25											-- largest hit profile penalty to hitting

NDefines.NNavy.COMBAT_EVASION_TO_HIT_CHANCE_TORPEDO_MULT = 1.0						-- the above evasion hit chance is multiplied by 400% if shooting with torpedoes. Torpedoes are slow, so evasion matters more.
NDefines.NNavy.COMBAT_TORPEDO_CRITICAL_CHANCE = 0.9									-- chance for critical hit from torpedo.
NDefines.NNavy.COMBAT_TORPEDO_CRITICAL_DAMAGE_MULT = 6.0							-- multiplier to damage when got critical hit from torpedo. (Critical hits are devastating as usualy torpedo_attack are pretty high base values).
NDefines.NNavy.HIT_PROFILE_SPEED_FACTOR = 1.2										-- factors speed value when determining it profile (Vis * HIT_PROFILE_MULT * Ship Hit Profile Mult)

NDefines.NNavy.MIN_REPAIR_FOR_JOINING_COMBATS = { 									-- strikeforces/patrol forces will not join combats if they are not repaired enough
	0.0,	-- do not repair
	0.5,	-- low
	0.7,	-- medium
	0.8,	-- high
}

--NDefines.NNavy.ORG_COST_WHILE_MOVING_IN_MISSION_ZONE = { -- org cost while moving in mission zone
--	0.3, -- HOLD
--	0.3, -- PATROL
--	0, -- STRIKE FORCE
--	0.3, -- CONVOY RAIDING
--	0.3, -- CONVOY ESCORT
--	0.3, -- MINES PLANTING
--	0.3, -- MINES SWEEPING
--	0.3, -- TRAIN
--	0.4, -- RESERVE_FLEET
--	0.3, -- NAVAL_INVASION_SUPPORT
--}

NDefines.NNavy.BASE_SPOTTING = 1													-- base spotting percentage for navy
NDefines.NNavy.BASE_SPOTTING_FROM_RADAR = 10										-- base spotting percentage that comes from full radar coverage
NDefines.NNavy.BASE_SPOTTING_FROM_AIR_SUPERIORITY = 30								-- base spotting percentage that comes from air superiority
NDefines.NNavy.BASE_SPOTTING_FROM_ACTIVE_NAVY = 20									-- base spotting percentage that comes from ships in area
NDefines.NNavy.BASE_SPOTTING_ACTIVE_NAVY_MULT = 0.1									-- multiplier for your navies base spotting percentage
NDefines.NNavy.BASE_SPOTTING_FROM_DECRYPTION = 20									-- base spotting percentage that comes from decryption, can go negative (enemy decryption is subtracted)

NDefines.NNavy.BASE_GUN_COOLDOWNS = { 												-- number of hours for a gun to be ready after shooting
		1.0,	-- big guns
		3.0,	-- torpedoes
		1.0,	-- small guns
	}

NDefines.NNavy.RELATIVE_SURFACE_DETECTION_TO_POSITIONING_FACTOR	= 0.01				-- multiples the surface detection difference between two sides. the side with higher detection will get a bonus of this value
NDefines.NNavy.MAX_POSITIONING_BONUS_FROM_SURFACE_DETECTION	= 0.0 					-- will clamp the bonus that you get from detection

NDefines.NNavy.HIGHER_SHIP_RATIO_POSITIONING_PENALTY_FACTOR	= 0.48 					-- if one side has more ships than the other, that side will get this penalty for each +100% ship ratio it has
NDefines.NNavy.MAX_POSITIONING_PENALTY_FROM_HIGHER_SHIP_RATIO = 3.0  				-- maximum penalty to get from larger fleets

NDefines.NNavy.HIGHER_CARRIER_RATIO_POSITIONING_PENALTY_FACTOR = 0.2  				-- penalty if other side has stronger carrier air force
NDefines.NNavy.MAX_CARRIER_RATIO_POSITIONING_PENALTY_FACTOR = 0.2  					-- max penalty from stronger carrier air force

NDefines.NNavy.POSITIONING_PENALTY_FOR_SHIPS_JOINED_COMBAT_AFTER_IT_STARTS = 0.001 	-- each ship that joins the combat will have this penalty to be added into positioning
NDefines.NNavy.MAX_POSITIONING_PENALTY_FOR_NEWLY_JOINED_SHIPS = 0.025  				-- the accumulated penalty from new ships will be clamped to this value
NDefines.NNavy.POSITIONING_PENALTY_HOURLY_DECAY_FOR_NEWLY_JOINED_SHIPS = 0.05		-- the accumulated penalty from new ships will decay hourly by this value

NDefines.NNavy.DAMAGE_PENALTY_ON_MINIMUM_POSITIONING = 0.5							-- damage penalty at 0% positioning
NDefines.NNavy.SCREENING_EFFICIENCY_PENALTY_ON_MINIMUM_POSITIONING = 0.25  			-- screening efficiency (screen to capital ratio) at 0% positioning
NDefines.NNavy.AA_EFFICIENCY_PENALTY_ON_MINIMUM_POSITIONING = 0  					-- AA penalty at 0% positioning
NDefines.NNavy.SUBMARINE_REVEAL_ON_MINIMUM_POSITIONING = 10.0  						-- submarine reveal change on 0% positioning

NDefines.NNavy.SHORE_BOMBARDMENT_CAP = 0.30
NDefines.NNavy.HEAVY_GUN_ATTACK_TO_SHORE_BOMBARDMENT = 0.025  						-- heavy gun attack value is divided by this value * 100 and added to shore bombardment modifier
NDefines.NNavy.LIGHT_GUN_ATTACK_TO_SHORE_BOMBARDMENT = 0.0005						    -- light gun attack value is divided by this value * 100 and added to shore bombardment modifier


NDefines.NNavy.AGGRESSION_HEAVY_GUN_EFFICIENCY_ON_LIGHT_SHIPS = 0.1					-- ratio for scoring for different gun types against light ships
NDefines.NNavy.AGGRESSION_LIGHT_GUN_EFFICIENCY_ON_HEAVY_SHIPS = 0.05				-- ratio for scoring for different gun types against light ships
--NDefines.NNavy.COMBAT_ARMOR_PIERCING_DAMAGE_REDUCTION = -0.25						-- All damage reduction % when target armor is >= then shooter armor piercing.

NDefines.NNavy.TRAINING_EXPERIENCE_FACTOR = 0.25									-- Amount of exp each ship gain every 24h while training (before modifiers)
NDefines.NNavy.FIELD_EXPERIENCE_SCALE = 0.3

NDefines.NNavy.UNIT_EXPERIENCE_PER_COMBAT_HOUR = 5
NDefines.NNavy.UNIT_EXPERIENCE_SCALE = 1
NDefines.NNavy.EXPERIENCE_FACTOR_CONVOY_ATTACK = 0.24
NDefines.NNavy.EXPERIENCE_FACTOR_NON_CARRIER_GAIN = 0.24							-- Xp gain by non-carrier ships in the combat
NDefines.NNavy.EXPERIENCE_FACTOR_CARRIER_GAIN = 0.24								-- Xp gain by carrier ships in the combat

NDefines.NNavy.NAVAL_SUPREMACY_CAN_INVADE = 0.5										-- required naval supremacy to perform invasions on an area

NDefines.NNavy.AGGRESSION_SETTINGS_VALUES = { 										-- ships will use this values while deciding to attack enemies
		0,		-- do not engage
		0.95,	-- low
		1.0,	-- medium
		2.0,	-- high
		10000,	-- I am death incarnate!
	}

NDefines.NNavy.MISSION_SUPREMACY_RATIOS = { 										-- supremacy multipliers for different mission types
        0.0, -- HOLD
        1.0, -- PATROL
        0.18, -- STRIKE FORCE
        0.5, -- CONVOY RAIDING
        0.5, -- CONVOY ESCORT
        0.3, -- MINES PLANTING
        0.3, -- MINES SWEEPING
        0.0, -- TRAIN
        0.0, -- RESERVE_FLEET
        0.4, -- NAVAL_INVASION_SUPPORT
    }

NDefines.NNavy.CONVOY_EFFICIENCY_LOSS_MODIFIER = 1.1								-- How much efficiency drops when losing convoys. If modifier is 0.5, then losing 100% of convoys in short period, the efficiency will drop by 50%.
NDefines.NNavy.CONVOY_EFFICIENCY_REGAIN_AFTER_DAYS = 1								-- Convoy starts regaining it's efficiency after X days without any convoys being sink.
NDefines.NNavy.CONVOY_EFFICIENCY_REGAIN_BASE_SPEED = 0.04							-- How much efficiency regains every day.
NDefines.NNavy.CONVOY_EFFICIENCY_MIN_VALUE = 0.05									-- To avoid complete 0% efficiency, set the lower limit.

NDefines.NNavy.NAVAL_TRANSFER_DAMAGE_REDUCTION = 0.0625								-- its hard to specifically balance 1-tick naval strikes vs unit transports so here is a factor for it

NDefines.NNavy.ESCAPE_SPEED_SUB_BASE = 0.4											-- subs get faster escape speed. gets replaced by hidden version below if hidden
NDefines.NNavy.ESCAPE_SPEED_HIDDEN_SUB = 1.0										-- hidden subs get faster escape speed
NDefines.NNavy.SPEED_TO_ESCAPE_SPEED = 0.95											-- ratio to converstion from ship speed to escape speed (divided by hundred)
NDefines.NNavy.BASE_ESCAPE_SPEED = 1.0												-- daily base escape speed (gained as percentagE)

NDefines.NNavy.SUBMARINE_BASE_TORPEDO_REVEAL_CHANCE = 0.5							-- Chance of a submarine being revealed when it fires. 1.0 is 100%. this chance is then multiplied with modifier created by comparing firer's visibiility and target's detection

NDefines.NNavy.OUT_OF_FUEL_SPEED_FACTOR = -0.75
NDefines.NNavy.OUT_OF_FUEL_RANGE_FACTOR = -0.75
NDefines.NNavy.OUT_OF_FUEL_ATTACK_FACTOR = -0.9
NDefines.NNavy.OUT_OF_FUEL_TORPEDO_FACTOR = -0.9

NDefines.NNavy.SCREEN_RATIO_FOR_FULL_SCREENING_FOR_CAPITALS = 4.0					-- this screen ratio to num capital/carriers is needed for full screening beyond screen line
NDefines.NNavy.CAPITAL_RATIO_FOR_FULL_SCREENING_FOR_CARRIERS = 1.0					-- this capital ratio to num carriers is needed for full screening beyond screen line
NDefines.NNavy.BASE_CARRIER_SORTIE_EFFICIENCY = 0.7									-- factor of planes that can sortie by default from a carrier

NDefines.NNavy.TRAINING_DAILY_COUNTRY_EXP_FACTOR = 0.0003							-- Factor used to scale the Daily Country Navy XP gain
NDefines.NNavy.TRAINING_MAX_DAILY_COUNTRY_EXP = 0.15								-- Maximum navy XP daily gain
NDefines.NNavy.CARRIER_STACK_PENALTY = 10											-- The most efficient is 4 carriers in combat. 5+ brings the penalty to the amount of wings in battle.
NDefines.NNavy.CARRIER_STACK_PENALTY_EFFECT = 0.6									-- Each carrier above the optimal amount decreases the amount of airplanes being able to takeoff by such %.

--NDefines.NNavy.SUPREMACY_PER_SHIP_PER_MANPOWER = 0.15								-- supremacy of a ship is calculated using its IC, manpower and a base define
--NDefines.NNavy.SUPREMACY_PER_SHIP_PER_IC = 0.1
--NDefines.NNavy.SUPREMACY_PER_SHIP_BASE = 25.0

NDefines.NNavy.DEPTH_CHARGES_HIT_CHANCE_MULT = 2

NDefines.NNavy.MISSION_FUEL_COSTS = {  -- fuel cost for each mission
		0, -- HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
		0.8, -- PATROL
		1.0, -- STRIKE FORCE (does not cost fuel at base, and uses IN_COMBAT_FUEL_COST in combat. this is just for the movement in between)
		0.8, -- CONVOY RAIDING
		0.6, -- CONVOY ESCORT
		1.0, -- MINES PLANTING
		1.0, -- MINES SWEEPING
		0.4, -- TRAIN
		0.0, -- RESERVE_FLEET (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
		1.0, -- NAVAL_INVASION_SUPPORT (does not cost fuel at base, only costs while doing bombardment and escorting units)
	}

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- SUPPLY

NDefines.NSupply.NUM_RAILWAYS_TRAIN_FACTOR = 0.1									-- the train usage is scaled by railway distance between the supply node and the capital multiplied by this factor
NDefines.NSupply.SUPPLY_HUB_FULL_MOTORIZATION_TRUCK_COST = 500
NDefines.NSupply.CAPITAL_SUPPLY_CIVILIAN_FACTORIES = 0.3 							-- supply from one civilian factory
NDefines.NSupply.CAPITAL_SUPPLY_MILITARY_FACTORIES = 0.6 							-- supply from one military factory
NDefines.NSupply.AVAILABLE_MANPOWER_STATE_SUPPLY = 0.18								--Factor for state supply from max manpower (population)
NDefines.NSupply.NON_CORE_MANPOWER_STATE_SUPPLY = 0.05								--Factor for population sttate supply when controlled by an occupier (NO TAKE FOOD)

NDefines.NSupply.NAVAL_BASE_FLOW = 0.0 												-- max output/input of a naval node is limited by this base value + additional ratio for each level
NDefines.NSupply.NAVAL_FLOW_PER_LEVEL = 5.0 										-- max output/input of a naval node is limited by previous base value + this define per its level

NDefines.NSupply.RIVER_RAILWAY_LEVEL = 1											-- rivers will transfer in between nodes as if they were this level

---

NDefines.NSupply.FLOATING_HARBOR_BASE_SUPPLY = 30.0 								-- supply given by a floating harbor
NDefines.NSupply.FLOATING_HARBOR_BASE_DURATION = 60 								-- duration of a full hp floating harbor

NDefines.NSupply.NODE_INITIAL_SUPPLY_FLOW = 5.0										-- Base range of supply hubs
NDefines.NSupply.SUPPLY_HUB_FULL_MOTORIZATION_BONUS = 10.0							-- The range bonus added to a fully motorized hub. This supply is added on top of the XXX_INITIAL_SUPPLY_FLOW defined above.
NDefines.NSupply.SUPPLY_HUB_MOTORIZATION_MARGINAL_EFFECT_DECAY = 0					-- For each additional level of motorization on a hub (i.e. contry with set motoriazation) reduce max bonus for next level by this amount
NDefines.NSupply.NODE_STARTING_PENALTY_PER_PROVINCE = 0.75

NDefines.NSupply.RAILWAY_BASE_FLOW = 5.0											-- how much base flow railway gives when a node connected to its capital/a naval node by a railway
NDefines.NSupply.RAILWAY_FLOW_PER_LEVEL = 10.0 										-- how much additional flow a railway level gives
NDefines.NSupply.RAILWAY_FLOW_PENALTY_PER_DAMAGED = 8.0 							-- penalty to flow per damaged railway

---

NDefines.NSupply.SUPPLY_PATH_MAX_DISTANCE = 45										-- max time it can take
NDefines.NSupply.RAILWAY_DISTANCE_FACTOR_FOR_REINFORCEMENT_SPEED = 0.05 			-- time factor for total railway distance


NDefines.NSupply.RAILWAY_CONVERSION_COOLDOWN = 15 									-- railways will be put on cooldown when they are captured by enemy and will not be usable during the cooldown
NDefines.NSupply.RAILWAY_CONVERSION_COOLDOWN_CORE = 5
NDefines.NSupply.RAILWAY_CONVERSION_COOLDOWN_CIVILWAR = 0

NDefines.NSupply.SUPPLY_THRESHOLD_FOR_ARMY_ATTRITION = 0.4 							-- armies will only get attrition below this supply
NDefines.NSupply.STORED_SUPPLY_CONSUMPTION_RATE_FACTOR = 1						    -- Multiplies consumption rate of stored supply (more/less easement)

-- armies slowly gains and buffers supply above >100% up to their supply grace if they have efficent supply flow
-- otherwuse they will lose up to 100% supply every day depending on how bad supply flow is
NDefines.NSupply.ARMY_SUPPLY_RATIO_STARTING_GAIN = 0.0
NDefines.NSupply.ARMY_SUPPLY_RATIO_SPEED_GAIN_PER_HOUR = 0.01
NDefines.NSupply.ARMY_MAX_SUPPLY_RATIO_GAIN_PER_HOUR = 0.33

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- AI


----------- SUPPLY

--NDefines.NAI.SUPPLY_CRISIS_LIMIT = 1.0											-- If a unit is standing in an area with

----------- LEND LEASE

NDefines.NAI.BASE_RELUCTANCE = 10 													-- Base reluctance applied to all diplomatic offers

NDefines.NAI.MAX_THREAT_FOR_FIRST_YEAR_CIVILIAN_MODE = 20 							-- above this threshold, ai will leave first year civilian factory mode which bumps it civilian factory scores while building

NDefines.NAI.DIPLOMACY_LEND_LEASE_MONTHS_TO_CANCEL = 6								-- AI will not cancel a lend lease offer until this time has passed
NDefines.NAI.LENDLEASE_FRACTION_OF_PRODUCTION = 0.5									-- Base fraction AI would send as lendlease
NDefines.NAI.LENDLEASE_FRACTION_OF_STOCKPILE = 0.75									-- Base fraction AI would send as lendlease

NDefines.NAI.MINIMUM_EQUIPMENT_TO_ASK_LEND_LEASE = -100								-- AI will accept to lend lease this equipment only if our stockpile is less than that.
NDefines.NAI.MINIMUM_CONVOY_TO_ASK_LEND_LEASE = 200									-- AI will accept to lend lease convoys only if our stockpile is less than that (special case because convoy stockpile can't be negative).
NDefines.NAI.MINIMUM_FUEL_DAYS_TO_ASK_LEND_LEASE = 60								-- AI will accept to lend lease fuel only if the player have less fuel than this number multiply by his max daily consumption.
NDefines.NAI.MINIMUM_FUEL_DAYS_TO_ACCEPT_LEND_LEASE = 60					 		-- AI will accept to lend lease fuel only if they have more fuel than this number multiply by their max daily consumption. Note that for a GiE asking to its host, we divide this number by 2.

----------- NAVY

NDefines.NAI.MISSING_CONVOYS_BOOST_FACTOR = 44.0									-- The more convoys a country is missing, the more resources it diverts to cover this.

NDefines.NAI.MAX_DISTANCE_NALAV_INVASION = 180.0									-- AI is extremely unwilling to plan naval invasions above this naval distance limit.
NDefines.NAI.MAX_UNIT_RATIO_FOR_INVASIONS = 0.35									-- countries won't use armies more than this ratio of total units for invasions
NDefines.NAI.MAX_INVASION_FRONT_SCORE = 2400										-- max score for naval invasion front scores
NDefines.NAI.MIN_FRONT_SCORE_FOR_AFTER_INVASION_AREAS = 1800						-- min score for army fronts that are created on recently invaded regions
NDefines.NAI.INVASION_DISTANCE_RANDOMNESS = 3										-- This higher the value, the more unpredictable the invasions. Compares to actual map distance in pixels.
NDefines.NAI.INVASION_COASTAL_PROVS_PER_ORDER = 28									-- AI will consider one extra invasion per number of provinces stated here (num orders = total coast / this)
NDefines.NAI.NAVAL_INVADED_AREA_PRIO_DURATION = 270									-- after successful invasion, AI will prio the enemy area for this number of days
NDefines.NAI.NAVAL_INVADED_AREA_PRIO_MULT = 2.0										-- fronts that belongs to recent invasions gets more prio
NDefines.NAI.MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS = 30		-- if you conquer this amount of provinces after a naval invasion, it will lose its prio status and will act as a regular front
NDefines.NAI.MAX_INVASION_SIZE = 18													-- max invasion group size

NDefines.NAI.CONVOY_ESCORT_MUL_FROM_NO_CONVOYS = 0 									-- score multiplier when no convoys are around
NDefines.NAI.CONVOY_ESCORT_SCORE_FROM_CONVOYS = 1             				        -- score for each convoy you have in area
NDefines.NAI.REGION_CONVOY_DANGER_DAILY_DECAY = 5									-- When convoys are sunk it generates threat in the region which the AI uses to prio nalval missions

NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_MINE_LAYING = 0.15							-- maximum ratio of screens forces to be used in mine laying
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING = 0.05 						-- maximum ratio of screens forces to be used in mine sweeping
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MIN = 0.1						-- minimum ratio of all screen-ships forces to be used in convoy defense (increases up to max as AI loses convoys).
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MAX = 0.5 					-- maximum ratio of all screen-ships forces to be used in convoy defense (increases up to max as AI loses convoys).
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MAX_CONVOY_THREAT = 500 		-- AI will increase screen assignment for escort missions as threat increases

NDefines.NAI.CARRIER_TASKFORCE_MAX_CARRIER_COUNT = 4 								-- optimum carrier count for carrier taskforces
NDefines.NAI.CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT = 10 								-- optimum capital count for capital taskforces
NDefines.NAI.SCREEN_TASKFORCE_MAX_SHIP_COUNT = 5									-- optimum screen count for screen taskforces
NDefines.NAI.SCREENS_TO_CAPITAL_RATIO = 4.0											-- screens to capital/carrier count in carrier & capital taskforces

NDefines.NAI.MAX_CARRIER_OVERFILL = 1.0												-- Carriers will be overfilled to this amount if there are doctrines to justify it
NDefines.NAI.MIN_CAPITALS_FOR_CARRIER_TASKFORCE = 6									-- carrier fleets will at least have this amount of capitals
NDefines.NAI.CAPITALS_TO_CARRIER_RATIO = 4.0										-- capital to carrier count in carrier taskfoces

NDefines.NAI.MAX_PATROL_TO_STRIKE_FORCE_RATIO = 5.0									-- maximum patrol/strike force ratio

--NDefines.NAI.NAVAL_MISSION_AGGRESSIVE_PATROL_DIVISOR = 3							-- Divides patrol score when not defending
NDefines.NAI.NAVAL_MISSION_PATROL_NEAR_OWNED = 1000									-- Extra patrol mission score near owned provinces

NDefines.NAI.NAVAL_DOCKYARDS_SHIP_FACTOR = 2										-- The extent to which number of dockyards play into amount of sips a nation wants
NDefines.NAI.NAVY_PREFERED_MAX_SIZE = 75											-- AI will generally attempt to merge fleets into this size, but as a soft limit.
NDefines.NAI.SUB_TASKFORCE_MAX_SHIP_COUNT = 5 										-- optimum sub count for sub taskforces
NDefines.NAI.PRODUCTION_MAX_PROGRESS_TO_SWITCH_NAVAL = 0							-- AI will not replace ships being built by newer types if progress is above this

NDefines.NAI.REGION_THREAT_LEVEL_TO_BLOCK_REGION = 25 * 1000						-- How much threat must be generated in region ( by REGION_THREAT_PER_SUNK_CONVOY ) so the AI will decide to mark the region as avoid


NDefines.NAI.NAVAL_MISSION_MINES_PLANTING_NEAR_OWNED = 80000
NDefines.NAI.NAVAL_MISSION_MINES_SWEEPING_NEAR_OWNED = 100000	 					-- How likely the AI will do the sweeping missions. The value is scaled by the amount of mines to sweep.

------------------------------------------------- AIR

NDefines.NAI.AIR_WING_REINFORCEMENT_LIMIT = 100

NDefines.NAI.MINES_SWEEPING_PLANES_PER_MAX_MINES = 1 								-- Amount of air wings request for mines sweeping when there is max amount of mines planted by enemy in certain region
NDefines.NAI.MINES_PLANTING_PLANES_PER_MAX_DESIRE = 1								-- Amount of air wings request for mines planting when there is max desire for it.

NDefines.NAI.NAVAL_COMBAT_AIR_IMPORTANCE = 500.0
NDefines.NAI.NAVAL_AIR_SUPERIORITY_IMPORTANCE = 1.0                             	-- Strategic importance of air superiority ( amount of enemy planes in area )
NDefines.NAI.NAVAL_MIN_EXCORT_WINGS = 5												-- Min amount of airwings requested to excort operations
NDefines.NAI.NAVAL_IMPORTANCE_SCALE = 10.0
NDefines.NAI.MAX_FUEL_CONSUMPTION_RATIO_FOR_AIR_TRAINING = 0.9						-- ai will use at most this ratio of affordable fuel for air training
NDefines.NAI.NAVAL_FIGHTERS_PER_PLANE = 1.0                                         -- Amounts of air superiority planes requested per enemy plane
NDefines.NAI.NAVAL_STRIKE_PLANES_PER_SHIP = 40										-- Amount of bombers requested per enemy ship
NDefines.NAI.NAVAL_SHIP_IN_PORT_AIR_IMPORTANCE = 20.0                             	-- Naval ship in the port air importance
NDefines.NAI.PORT_STRIKE_PLANES_PER_SHIP = 20										-- Amount of bombers request per enemy ship in the port

NDefines.NAI.FORTIFIED_RATIO_TO_CONSIDER_A_FRONT_FORTIFIED = 0.25 					-- ai will consider a front fortified if this ratio of provinces has fort

NDefines.NAI.AGGRESSIVENESS_CHECK_PARTLY_FORTIFIED = 2.0							-- if front strength balance is at or above this value versus a party fortified enemy, we do a balanced attack
NDefines.NAI.AGGRESSIVENESS_CHECK_PARTLY_FORTIFIED_WEAK_POINTS = 0.75				-- if front strength balance is at or above this value versus a party fortified enemy, we rush attack weak points; below this value, we are careful
NDefines.NAI.AGGRESSIVENESS_CHECK_FULLY_FORTIFIED = 10								-- if front strength balance is at or above this value versus a fully fortified enemy with no weak points, we do a balanced attack instead being careful
NDefines.NAI.AGGRESSIVENESS_CHECK_FULLY_FORTIFIED_POCKET = 6						-- if front strength balance is at or above this value versus a fully fortified enemy in a pocket, we do a balanced attack instead being careful

NDefines.NAI.LAND_DEFENSE_AIR_SUPERIORITY_IMPORTANCE = 0.8							-- Strategic importance of air superiority ( amount of enemy planes in area )
NDefines.NAI.LAND_DEFENSE_CIVIL_FACTORY_IMPORTANCE = 150							-- Strategic importance of civil factories
NDefines.NAI.LAND_DEFENSE_MILITARY_FACTORY_IMPORTANCE = 200							-- Strategic importance of military factories
NDefines.NAI.LAND_DEFENSE_FIGHERS_PER_PLANE = 0.1									-- Amount of air superiority planes requested per enemy plane
NDefines.NAI.LAND_DEFENSE_FIGHERS_PER_PLANE = 2.0									-- Amount of air superiority planes requested per enemy plane
NDefines.NAI.LAND_DEFENSE_INTERSEPTORS_PER_BOMBERS = 2.0							-- Amount of air interceptor planes requested per enemy bomber
NDefines.NAI.LAND_DEFENSE_INTERSEPTORS_PER_PLANE = 0								-- Amount of air interceptor planes requested per enemy plane (non bomber)
NDefines.NAI.LAND_DEFENSE_SUPPLY_HUB_IMPORTANCE = 80								-- Strategic importance of supply hubs
NDefines.NAI.LAND_DEFENSE_AA_IMPORTANCE_FACTOR = 1.0								-- Factor of AA influence on strategic importance ( 0.0 - 1.0 )
NDefines.NAI.LAND_DEFENSE_INFRA_IMPORTANCE_FACTOR = 70								-- Factor of infrastructure influence on strategic importance ( 0.0 - 1.0 )

NDefines.NAI.LAND_COMBAT_AIR_SUPERIORITY_IMPORTANCE = 2.0 							-- Strategic importance of air superiority ( amount of enemy planes in area )
NDefines.NAI.LAND_COMBAT_OUR_ARMIES_AIR_IMPORTANCE = 12 							-- Strategic importance of our armies
NDefines.NAI.LAND_COMBAT_OUR_COMBATS_AIR_IMPORTANCE = 55							-- Strategic importance of our armies in the combats
NDefines.NAI.LAND_COMBAT_IMPORTANCE_SCALE = 5 										-- Lend combat total importance scale (every land combat score get's multiplied by it)
NDefines.NAI.LAND_COMBAT_FIGHTERS_PER_PLANE = 1.1										-- Amount of air superiority planes requested per enemy plane
NDefines.NAI.LAND_COMBAT_CAS_PER_ENEMY_ARMY = 10									-- Amount of CAS planes requested per enemy army
NDefines.NAI.LAND_COMBAT_ANTI_LOGISTICS_PER_ENEMY_ARMY = 0     						-- Amount of CAS planes requested per enemy army for anti-logistics
NDefines.NAI.LAND_COMBAT_CAS_PER_COMBAT = 150										-- Amount of CAS requested per combat
NDefines.NAI.LAND_COMBAT_BOMBERS_PER_LAND_FORT_LEVEL = 30							-- Amount of bomber planes requested per enemy land fort level
NDefines.NAI.LAND_COMBAT_MIN_EXCORT_WINGS = 3										-- Min amount of airwings requested to excort operations
NDefines.NAI.LAND_COMBAT_INTERCEPT_PER_PLANE = 0.4									-- Amount of interception planes requested per enemy plane

NDefines.NAI.NAVAL_COMBAT_TRANSFER_AIR_IMPORTANCE = 500.0							-- Naval combat involving enemy land units

NDefines.NAI.STR_BOMB_AIR_SUPERIORITY_IMPORTANCE = 2.0								-- Strategic importance of air superiority ( amount of enemy planes in area )

NDefines.NAI.STR_BOMB_MIN_ENEMY_FIGHTERS_IN_AREA = 2800								-- If amount of enemy fighters is higher than this mission won't perform
NDefines.NAI.STR_BOMB_FIGHTERS_PER_PLANE = 1.5										-- Amount of air superiority planes requested per enemy plane
NDefines.NAI.STR_BOMB_MIN_EXCORT_PLANES = 1200										-- Min amount of planes requested to excort operations

------------------------------------------------- END

NDefines.NAI.MAX_REQUEST_EXPEDITIONARIES_ARMY_RATIO = 0.1							-- AI will not accept expeditionary requests if its expeditions are above this ratio

NDefines.NAI.REFIT_SHIP_RELUCTANCE = 7												-- How often to consider refitting to new equipment variants for ships in the field
NDefines.NAI.REFIT_SHIP_PERCENTAGE_OF_FORCES = 1.0									-- How big part of the navy that should be considered for refitting

NDefines.NAI.MAX_FACTORY_TO_SPARE_FOR_MISSION_FUEL_TRADE_IN_PEACE = 0.1 			-- amount of factories to spend on oil trade in case of fuel need for missions in peace time
NDefines.NAI.MAX_FACTORY_TO_SPARE_FOR_CRITICAL_MISSION_FUEL_TRADE_IN_PEACE = 0.2 	-- amount of factories to spend on oil trade in case of fuel need for prio missions in peace time
NDefines.NAI.MAX_FACTORY_TO_TRADE_FOR_FUEL_IN_PEACE = 0.5
NDefines.NAI.FUEL_CONSUMPTION_MULT_FOR_FUEL_SAVING_MODE = 4.0						-- fuel consumptions will be limited by this ratio in fuel saving mode
NDefines.NAI.FUEL_CONSUMPTION_MULT_REGULAR_FUEL_MODE = 4.0							-- fuel consumptions will be limited by this ratio in regular fuel mode
NDefines.NAI.FUEL_CONSUMPTION_MULT_AGRESSIVE_FUEL_MODE = 10.0						-- fuel consumptions will be limited by this ratio in aggressive fuel usage mode
NDefines.NAI.WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_ARMY_MAX_CONSUMPTION = 60	  		-- AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer
NDefines.NAI.WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_AIR_MAX_CONSUMPTION = 60  			-- AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer
NDefines.NAI.WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_NAVY_MAX_CONSUMPTION = 60 	 		-- AI will try to buffer at least this amount of days on max consumption, will trade if necesarry and will go into fuel saving mode/aggresive mode using this buffer
NDefines.NAI.MIN_WANTED_MAX_FUEL = 5									   			-- minimum value for wanted fuel buffers for AI (in thousands)

--NDefines.NAI.NUM_SILOS_PER_CIVILIAN_FACTORIES = 0.0025								-- ai will try to build a silo per this ratio of civ factories
--NDefines.NAI.NUM_SILOS_PER_MILITARY_FACTORIES = 0.024								-- ai will try to build a silo per this ratio of mil factories
--NDefines.NAI.NUM_SILOS_PER_DOCKYARDS = 0.02											-- ai will try to build a silo per this ratio of dockyards

NDefines.NAI.MAX_THREAT_FOR_FIRST_YEAR_CIVILIAN_MODE = 10 							-- above this threshold, ai will leave first year civilian factory mode which bumps it civilian factory scores while building

NDefines.NAI.MAX_FUEL_CONSUMPTION_RATIO_FOR_NAVY_TRAINING = 0.2						-- ai will use at most this ratio of affordable fuel for naval training
NDefines.NAI.MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING = 0.8						-- ai will not train a taskforce if fully trained ships are above this ratio

NDefines.NAI.MAX_UNITS_FACTOR_FRONT_ORDER = 3.0										-- Factor for max number of units to assign to area front orders
NDefines.NAI.DESIRED_UNITS_FACTOR_FRONT_ORDER = 3.0									-- Factor for desired number of units to assign to area front orders
NDefines.NAI.MIN_UNITS_FACTOR_FRONT_ORDER = 2.0										-- Factor for min number of units to assign to area front orders

NDefines.NAI.MAX_UNITS_FACTOR_INVASION_ORDER = 1.4									-- Factor for max number of units to assign to naval invasion orders
NDefines.NAI.DESIRED_UNITS_FACTOR_INVASION_ORDER = 1.4								-- Factor for desired number of units to assign to naval invasion orders
NDefines.NAI.MIN_UNITS_FACTOR_INVASION_ORDER = 1.2									-- Factor for min number of units to assign to naval invasion orders

NDefines.NAI.HOUR_BAD_COMBAT_REEVALUATE = 6 										-- if we are in combat for this amount and it goes shitty then try skipping it

--NDefines.NAI.MIN_FRONT_SIZE_TO_CONSIDER_STANDARD_COHESION = 5000					-- How long should fronts be before we consider switching to standard cohesion (under this, standard cohesion fronts will switch back to relaxed)

NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_LOW = 0.85									-- Minimum org % for a unit to actively attack an enemy unit when executing a plan
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_LOW = 0.85								-- Minimum strength for a unit to actively attack an enemy unit when executing a plan

NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_MED = 0.75									-- (LOW,MED,HIGH) corresponds to the plan execution agressiveness level.
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_MED = 0.8

NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_HIGH = 0.2
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_HIGH = 0.7

NDefines.NAI.PLAN_ACTIVATION_SUPERIORITY_AGGRO = 10.0         					    -- How aggressive a country is in activating a plan based on how superiour their force is.

--NDefines.NAI.PLAN_VALUE_BONUS_FOR_MOVING_UNITS = 0.5								-- AI plans gets a bonus when units are not moving and ready to fight
NDefines.NAI.MIN_INVASION_PLAN_VALUE_TO_EXECUTE = 0.05								-- ai will only activate invasions if it is above this

NDefines.NAI.PLAN_FRONT_SECTION_MAX_LENGTH = 5										-- When a front is longer than this it will be split in two sections for the AI
NDefines.NAI.PLAN_FRONT_SECTION_MIN_LENGTH = 2										-- When two front sections together are this short they will be merged for the AI

NDefines.NAI.PLAN_FACTION_STRONG_TO_EXECUTE = 0.65									-- % or more of units in an order to consider executing the plan
NDefines.NAI.ORG_UNIT_STRONG = 0.8													-- Organization % for unit to be considered strong
NDefines.NAI.STR_UNIT_STRONG = 0.95													-- Strength (equipment) % for unit to be considered strong

NDefines.NAI.PLAN_FACTION_NORMAL_TO_EXECUTE = 0.65									-- % or more of units in an order to consider executing the plan
NDefines.NAI.ORG_UNIT_NORMAL = 0.5													-- Organization % for unit to be considered normal
NDefines.NAI.STR_UNIT_NORMAL = 0.7													-- Strength (equipment) % for unit to be considered normal

NDefines.NAI.PLAN_FACTION_WEAK_TO_ABORT = 0.3										-- % or more of units in an order to consider executing the plan
NDefines.NAI.ORG_UNIT_WEAK = 0.3													-- Organization % for unit to be considered weak
NDefines.NAI.STR_UNIT_WEAK = 0.5													-- Strength (equipment) % for unit to be considered weak

NDefines.NAI.PLAN_AVG_PREPARATION_TO_EXECUTE = 0.5									-- % or more average plan preparation before executing
NDefines.NAI.AI_FRONT_MOVEMENT_FACTOR_FOR_READY = 0.5			               		-- If less than this fraction of units on a front is moving  AI sees it as ready for action

NDefines.NAI.ORDER_ASSIGNMENT_DISTANCE_FACTOR = 10.0								-- When the AI assigns units to orders, it attempts to calculate the distance.
NDefines.NAI.RELUCTANCE_TO_CHANGE_FRONT_FACTOR = 0.9								-- Factor for how reluctant the AI is to change a units order group.
NDefines.NAI.REVISITED_PROV_PENALTY_FACTOR = 1.8									-- When the AI picks units for a front, it tries to spread out a bit which units it grabs.

NDefines.NAI.FRONT_EVAL_UNIT_ACCURACY = 0.95										-- scale how stupid ai will act on fronts. 0 is potato
NDefines.NAI.GARRISON_FRACTION = 0.05												-- How large part of a front should always be holding the line rather than advancing at the enemy

NDefines.NAI.FRONT_TERRAIN_DEFENSE_FACTOR = 1.0										-- Multiplier applied to unit defense modifier for terrain on front province multiplied by terrain importance
NDefines.NAI.FRONT_TERRAIN_ATTACK_FACTOR = 2.0										-- Multiplier applied to unit attack modifier for terrain on enemy front province multiplied by terrain importance
NDefines.NAI.FALLBACK_LOSING_FACTOR = 0.0 					              		   	-- The lower this number  the longer the AI will hold the line before sending them to the fallback line
NDefines.NAI.PLAN_MIN_SIZE_FOR_FALLBACK = 50000										-- A country with less provinces than this will not draw fallback plans  but rather station their troops along the front
NDefines.NAI.UNIT_ASSIGNMENT_TERRAIN_IMPORTANCE = 0.05								-- Terrain score for units are multiplied by this when the AI is deciding which front they should be assigned to

NDefines.NAI.MICRO_POCKET_SIZE = 6													-- Pockets with a size equal to or lower than this will be mocroed by the AI, for efficiency.
NDefines.NAI.POCKET_DISTANCE_MAX = 10000											-- shortest square distance we bother about chasing pockets

NDefines.NAI.VP_LEVEL_IMPORTANCE_HIGH = 20											-- Victory points with values higher than or equal to this are considered to be of high importance.
NDefines.NAI.VP_LEVEL_IMPORTANCE_MEDIUM = 5											-- Victory points with values higher than or equal to this are considered to be of medium importance.
NDefines.NAI.VP_LEVEL_IMPORTANCE_LOW = 1											-- Victory points with values higher than or equal to this are considered to be of low importance.

NDefines.NAI.START_TRAINING_EQUIPMENT_LEVEL = 0.9									-- ai will not start to train if equipment drops below this level
NDefines.NAI.STOP_TRAINING_EQUIPMENT_LEVEL = 0.85            						-- ai will not train if equipment drops below this level
NDefines.NAI.DEPLOY_MIN_TRAINING_SURRENDER_FACTOR = 1.0								-- Required percentage of training (1.0 = 100%) for AI to deploy unit in wartime while surrender progress is higher than 0
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_SURRENDER_FACTOR = 1.0							-- Required percentage of equipment (1.0 = 100%) for AI to deploy unit in wartime while surrender progress is higher than 0
NDefines.NAI.DEPLOY_MIN_TRAINING_PEACE_FACTOR = 1.0									-- Required percentage of training (1.0 = 100%) for AI to deploy unit in peacetime
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_PEACE_FACTOR = 1.0								-- Required percentage of equipment (1.0 = 100%) for AI to deploy unit in peacetime
NDefines.NAI.DEPLOY_MIN_TRAINING_WAR_FACTOR = 1.0									-- Required percentage of training (1.0 = 100%) for AI to deploy unit in wartime
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_WAR_FACTOR = 1.0									-- Required percentage of equipment (1.0 = 100%) for AI to deploy unit in wartime

NDefines.NAI.UPGRADE_DIVISION_RELUCTANCE = 7										-- How often to consider upgrading to new templates for units in the field
NDefines.NAI.UPGRADE_PERCENTAGE_OF_FORCES = 1.0										-- How big part of the army that should be considered for upgrading

NDefines.NAI.UPGRADES_DEFICIT_LIMIT_DAYS = 30	                    				-- Ai will avoid upgrading units in the field to new templates if it takes longer than this to fullfill their equipment need

NDefines.NAI.MAX_AVAILABLE_MANPOWER_RATIO_TO_BUFFER_WARTIME = 0.4					-- deployment will try to buffer a ratio of manpower (for reinforcements) during war time
NDefines.NAI.MAX_AVAILABLE_MANPOWER_RATIO_TO_BUFFER_PEACETIME = 0.01				-- deployment will try to buffer a ratio of manpower (for reinforcements) during peace time

--NDefines.NAI.DESPERATE_AI_MIN_UNIT_ASSIGN_TO_ESCAPE = 2								-- AI will assign at least this amount of units to break from desperate situations

--NDefines.NAI.DESPERATE_AI_WEAK_UNIT_STR_LIMIT = 0.1									-- ai will increase number of units assigned to break from desperate situations when units are start falling lower than this str limit
--NDefines.NAI.DESPERATE_AI_MIN_ORG_BEFORE_ATTACK = 0.9								-- ai will wait for this much org to attack an enemy prov in desperate situations
--NDefines.NAI.DESPERATE_AI_MIN_ORG_BEFORE_MOVE = 0.25								-- ai will wait for this much org to move in desperate situations
NDefines.NAI.DESPERATE_ATTACK_WITHOUT_ORG_WHEN_NO_ORG_GAIN = 1000					-- if ai can't regain enough org to attack in this many hours, it will go truly desperate and attack anyway (still has to wait for move org)

NDefines.NAI.TRADEABLE_FACTORIES_FRACTION = 1.0	 									-- Will at most trade away this fraction of factories.

NDefines.NAI.PRODUCTION_EQUIPMENT_SURPLUS_FACTOR = 0.3								-- Base value for how much of currently used equipment the AI will at least strive to have in stock
NDefines.NAI.PRODUCTION_LINE_SWITCH_SURPLUS_NEEDED_MODIFIER = 0
NDefines.NAI.PRODUCTION_CARRIER_PLANE_BUFFER_RATIO = 5								-- in additional to total deck size of carriers, we want at least this ratio to buffer it
NDefines.NAI.PRODUCTION_CARRIER_PLANE_PRODUCTION_BOOST_TO_BUFFER = 4.0 				-- production of carrier planes will go up by this ratio if we lack buffers

NDefines.NAI.MAX_SUPPLY_DIVISOR = 0.75												-- To make sure the AI does not overdeploy divisions. Higher number means more supply per unit.
NDefines.NAI.FRONT_UNITS_CAP_FACTOR = 10.0											-- A factor applied to total front size and supply use. Primarily effects small fronts

NDefines.NAI.RESEARCH_BONUS_FACTOR = 4.0
NDefines.NAI.MAX_AHEAD_RESEARCH_PENALTY = 2	            							-- max ahead of tiem penalty ai will pick ever
NDefines.NAI.RESEARCH_AHEAD_OF_TIME_FACTOR = 10.0									-- To which extent AI should care about ahead of time penalties to research

NDefines.NAI.MINIMUM_GOOD_TRADE_RATIO_PER_CIV = 0.5   							-- for each civ factory we have mul with this we are allowed to trade under % of resource on a trade
--NDefines.NAI.EXPORT_RESOURCE_TRADE_NEED_IMPORTANCE = 1.0							-- how important is each lost resource to overexport for trade law selection
NDefines.NAI.RESOURCE_WANT_PER_MISSING_BALANCE = 10.0								-- negative balance increases the desire on a resource
NDefines.NAI.RESOURCE_WANT_PER_CONSUMED = 0.2										-- if resource is being used in production, increase the desire

NDefines.NAI.DIPLOMACY_SEND_MAX_FACTION = 0.85										-- Country should not send away more units than this as expeditionaries
NDefines.NAI.DIPLOMACY_IMPROVE_RELATION_COST_FACTOR = 1000.0						-- Desire to boost relations subtracts the cost multiplied by this

NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROLLED = 0									-- AI needs to control more than this number of states before considering giving any away
NDefines.NAI.GIVE_STATE_CONTROL_MIN_CONTROL_DIFF = 1								-- The difference in number of controlled states compared to war participation needs to be bigger than this for the AI to consider giving a state to a country

NDefines.NAI.DESIRE_USE_XP_TO_UPDATE_LAND_TEMPLATE = 0    							-- How quickly is desire to update/create templates accumulated?
NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_LAND_DOCTRINE = 100.0    						-- How quickly is desire to unlock land doctrines accumulated?
NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_NAVAL_DOCTRINE = 2.0   						-- How quickly is desire to unlock naval doctrines accumulated?
NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_AIR_DOCTRINE = 100.0     						-- How quickly is desire to unlock air doctrines accumulated?
NDefines.NAI.DESIRE_USE_XP_TO_UPGRADE_AIR_EQUIPMENT = 0.5   						-- How quickly is desire to update/create air equipment variants accumulated?

NDefines.NAI.XP_RATIO_REQUIRED_TO_RESEARCH_WITH_XP = 1.0							-- AI will at least need this amount of xp compared to cost of a tech to reserch it with XP

NDefines.NAI.MAX_THREAT_FOR_FIRST_YEAR_CIVILIAN_MODE = 40							-- above this threshold, ai will leave first year civilian factory mode which bumps it civilian factory scores while building

--	NDefines_Graphics.NGraphics.

NDefines_Graphics.NGraphics.DRAW_FOW_CUTOFF = 0
NDefines_Graphics.NGraphics.DRAW_FOW_FADE_LENGTH = 0