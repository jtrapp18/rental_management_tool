import cli_ops as ops

# ///////////////////////////////////////////////////////////////
# SET UP TREE

def my_menu_tree():
    main = ops.Node(label="Main Menu")
    menu = ops.MenuTree(main)

    # re-usable nodes
    to_main = ops.Node(label="Back to main menu")
    procedure = {"prompt": "Entering main menu...",
                "func": menu.to_main,
                }
    to_main.add_procedure(**procedure)

    exit_app = ops.Node(label="Exit App")
    procedure = {"prompt": "Exiting application...",
                "func": menu.exit_app,
                }
    exit_app.add_procedure(**procedure)

    rentals = ops.Node(label="Rental Units")
    tenants = ops.Node(label="Tenants")
    payments = ops.Node(label="Payments")

    main.add_children([rentals, tenants, payments, exit_app])

    view_units = ops.Node(label="View All")
    edit_unit = ops.Node(label="Edit Unit Information")

    procedure = {"prompt": "Choose a unit",
                "func": lambda x: print(f"view_units procedure run with input {x}"),
                "input_req": True,
                "lowerBound": 1,
                "upperBound": 2
                }
    view_units.add_procedure(**procedure)

    rentals.add_children([view_units, edit_unit, to_main, exit_app])

    return menu