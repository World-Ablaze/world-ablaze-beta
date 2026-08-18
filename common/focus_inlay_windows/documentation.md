<!-- WA-SYNC: vendored copy of the engine's own focus inlay windows documentation.
WA-SYNC: source   = <HOI4 install>/common/focus_inlay_windows/documentation.md
WA-SYNC: edition  = 1.19.2.0 install (the file declares no edition)
WA-SYNC: game     = 1.19.2.0
WA-SYNC: synced   = 2026-08-18
WA-SYNC: Do not hand-edit. Refresh from the install and run `python tools/check_engine_docs.py`.
WA-SYNC: Cite sections by NAME (`documentation.md` section `<section title>`), never by line number:
WA-SYNC: a line number is a silent-drift mechanism, a section name is not.
WA-SYNC: The previous copy stated inlays support no interaction. They now support `scripted_buttons`
WA-SYNC: (`available` + `click_effect`, country scope) and `scripted_progressbars`.
-->

# Focus inlay windows
Focus inlay windows are generic inlay components that can be added
to the focus tree. Currently, they support showing information
and adding buttons with on click effects.

## Define inlay window syntax
An inlay window is defined using the following syntax
```
inlay_window_id = {
    window_name = gui_component_name
    internal = yes/no # If true, then the inlay window is only visible to the country itself (defaults no) 
    visible = visibility_trigger # when not visible, no evaluations will be done
    scripted_images = { # list of images that should have dynamic sprites
        icon_name = { # Name of the icon (must be a subcomponent of "gui_component_name") or button
            # List of possible gfx:es for the icon, first that
            # evaluates to true is selected (each update)

            # Each entry consists of a gfx_name (the gfx that will be used if the trigger is true); and a trigger or "yes"
            # If a trigger is provided, then it will be evaluated with the country scope of the focus tree.
            # If "yes" is set, then it will always be used.
            # Note: "yes" is commonly the last entry in the list
            # that acts as a default case.
            gfx_name = <selection_trigger or yes>
        }
    }
    scripted_buttons = { # List of scriptable buttons
        button_name = { # Name of a button. The same name can be defined in scripted_images to select gfx. If the name does not exist in scripted_iamges, it will use the default gfx set in the .gui file
            available = { # Trigger effect if the button should be clickable or not
            }
            click_effect = { # The effect that should be executed on click. Country scope
            }
        }
    }
    scripted_progressbars = { # list of progressbars that should fill up based on a variable
        icon_name = { # Name of the progressbar (must be an icon that is a a subcomponent of "gui_component_name" or a button, with a "progressbartype" as its spriteType)
            progress = <variable_name>
        }
    }
}
```

## Include inlay window in focus tree
An inlay window can be included in a focus tree using the following syntax. Note that any number of inlay windows can be defined for every focus tree.

```
inlay_window = {
    id = inlay_window_id
    position = { x = XXX y = YYY } # same syntax and scale as continuous focus position
}
```