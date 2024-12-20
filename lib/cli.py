import cli_ops as ops

# ///////////////////////////////////////////////////////////////
# MENU OBJECTS

unit_menu = {"title": "Main Menu", 
             "options": [
                 {"label": "Units", "func": lambda: print(1)}, 
                 {"label": "Add a pet", "func": lambda: print(2)}, 
                 {"label": "Exit app", "func": lambda: print(3)}
                 ]}

tenant_menu = {"title": "Main Menu", 
             "options": [
                 {"label": "Units", "func": lambda: print(1)}, 
                 {"label": "Add a pet", "func": lambda: print(2)}, 
                 {"label": "Exit app", "func": lambda: print(3)}
                 ]}

payment_menu = {"title": "Main Menu", 
             "options": [
                 {"label": "Units", "func": lambda: print(1)}, 
                 {"label": "Add a pet", "func": lambda: print(2)}, 
                 {"label": "Exit app", "func": lambda: print(3)}
                 ]}

main_menu = {"title": "Main Menu", 
             "options": [
                 {"label": "Units", "func": lambda: ops.formatted_menu(unit_menu)}, 
                 {"label": "Add a pet", "func": lambda: ops.formatted_menu(tenant_menu)}, 
                 {"label": "Exit app", "func": lambda: ops.formatted_menu(payment_menu)}
                 ]}

# ///////////////////////////////////////////////////////////////
# INTERFACE MAIN

if __name__ == "__main__":
    ops.display_welcome()  # this could be abstracted into a main() fn called here
    while True:
        ops.formatted_menu(main_menu)

        option_id = ops.get_user_option()
        selected_option = main_menu["options"][option_id]
        selected_option["func"]() # invoke callback function

        ops.exit_app()