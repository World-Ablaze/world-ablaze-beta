----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Map Icons

NDefines_Graphics.NMapIcons.STATES_PRIORITY_VICTORY_POINTS = 4

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Graphics

NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW = 5.0                -- 5-- thickness in pixels
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_COUNTRY_CENTER_THICKNESS = 1.0             -- 2 -- The center gradient is linear 1/255 per pixel for this many pixels
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_COUNTRY_HIGH = 15.0              -- 25
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_STATE = 45.0                     -- 5
--NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_A = 2.0            -- 2
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_B = 15.0             -- 20
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_STRATEGIC_REGIONS = 50.0         -- 150
NDefines_Graphics.NGraphics.GRADIENT_BORDERS_OUTLINE_CUTOFF_STRATEGIC_REGIONS = 0.973   -- 0.98

NDefines_Graphics.NGraphics.COUNTRY_COLOR_SATURATION_MODIFIER = 0.7                     -- 0.6
NDefines_Graphics.NGraphics.COUNTRY_COLOR_BRIGHTNESS_MODIFIER = 0.92                    -- 0.8

--NDefines_Graphics.NGraphics.GRADIENT_BORDERS_CAMERA_DISTANCE_OVERRIDE_TERRAIN = 0.39    -- 0.39

NDefines_Graphics.NGraphics.COUNTRY_FLAG_SMALL_TEX_MAX_SIZE = 2048                      -- Tweak dependly on amount of countries. Must be power of 2. No more then 2048.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- CAMERA

NDefines_Graphics.NGraphics.CAMERA_ZOOM_SPEED = 50
NDefines_Graphics.NGraphics.CAMERA_ZOOM_KEY_SCALE = 0.02
NDefines_Graphics.NGraphics.CAMERA_ZOOM_SPEED_DISTANCE_MULT = 15.0

NDefines_Graphics.NGraphics.MAP_ICONS_STATE_GROUP_CAM_DISTANCE = 450.0                  -- camera distance at which the icons begin to group up

NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF = { 250, 300, 500 }      -- At what camera distance the VP name text disappears.

NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MIN = 200.0              -- Min range for victory point text
NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MAX = 800.0              -- Max range for victory point text
NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MIN = 250.0               -- Min range for victory point dot
NDefines_Graphics.NGraphics.VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MAX = 1000.0              -- Max range for victory point text

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Air

NDefines_Graphics.NAirGfx.BOMBERS_DIVISION_FACTOR = 180					                -- Number of effective bombers in a strategic region will be divided by this factor.
NDefines_Graphics.NAirGfx.MISSILES_DIVISION_FACTOR = 180				        	    -- Number of missiles shown in a strategic region will be divided by this factor.
NDefines_Graphics.NAirGfx.FIGHTERS_DIVISION_FACTOR = 180				        	    -- Number of missiles shown in a strategic region will be divided by this factor.
NDefines_Graphics.NAirGfx.SCOUT_PLANE_DIVISION_FACTOR = 180				                -- Number of missiles shown in a strategic region will be divided by this factor.