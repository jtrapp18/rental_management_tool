from menu_tree import MenuTree, Node
from unit import Unit
from tenant import Tenant
from payment import Payment

def my_menu_tree():
    main = Node(label="Main Menu")
    menu = MenuTree(main)

    # ///////////////////////////////////////////////////////////////
    # BASIC OPERATIONS

    to_main = Node(label="Back to main menu")
    procedure = {"prompt": "Entering main menu...",
                "func": menu.to_main,
                }
    to_main.add_procedure(**procedure)

    go_back = Node(label="Back to previous menu")
    procedure = {"prompt": "Going back one level...",
                "func": go_back.go_back,
                }
    go_back.add_procedure(**procedure)

    exit_app = Node(label="Exit App")
    procedure = {"prompt": "Exiting application...",
                "func": menu.exit_app,
                }
    exit_app.add_procedure(**procedure)

    # ///////////////////////////////////////////////////////////////
    # SET UP MAIN MENU

    rentals = Node(label="Rental Units")
    tenants = Node(label="Tenants")
    payments = Node(label="Payments")

    main.add_children([rentals, tenants, payments, exit_app])

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    view_units = Node(label="View All")
    procedure = {"prompt": "View all units",
                "func": lambda: print(Unit.get_dataframe())
                }
    view_units.add_procedure(**procedure)

    select_unit = Node(label="Select Unit")
    procedure = {"prompt": f"Choose a unit from the following options: \n{Unit.get_dataframe()}",
                "func": lambda x: print(Unit.find_by_id(x)),
                "input_req": True
                }
    select_unit.add_procedure(**procedure)

    edit_unit = Node(label="Edit Unit")

    select_unit.add_children([edit_unit, go_back, to_main, exit_app])

    rentals.add_children([view_units, select_unit, to_main, exit_app])

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    view_tenants = Node(label="View All")
    procedure = {"prompt": "View all tenants",
                "func": lambda: print(Tenant.get_dataframe())
                }
    view_tenants.add_procedure(**procedure)

    select_tenant = Node(label="Select Tenant")
    procedure = {"prompt": f"Choose a tenant from the following options: \n{Tenant.get_dataframe()}",
                "func": lambda x: print(Tenant.find_by_id(x)),
                "input_req": True
                }
    select_tenant.add_procedure(**procedure)

    view_payments = Node(label="View Payments History")
    # this one is not appropriately going to the child... it is going up a level
    procedure = {"prompt": f"Showing payment history...",
                "func": lambda: print(Tenant.find_by_id(select_tenant.last_input).payments()),
                }
    view_payments.add_procedure(**procedure)

    print_payments = Node(label="Print Payment History")
    procedure = {"prompt": f"Printing payment history...",
                "func": lambda: print(Tenant.find_by_id(select_tenant.last_input).print_payments()),
                }
    print_payments.add_procedure(**procedure)
    
    view_payments.add_children([print_payments, go_back, to_main, exit_app])

    edit_tenant = Node(label="Edit Tenant")
    edit_tenant.add_children([go_back, to_main, exit_app])

    select_tenant.add_children([view_payments, edit_tenant, go_back, to_main, exit_app])

    tenants.add_children([view_tenants, select_tenant, to_main, exit_app])

    # ///////////////////////////////////////////////////////////////
    # SET UP PAYMENT OPERATIONS

    # view_units = Node(label="View All")
    # edit_unit = Node(label="Edit Unit Information")

    # procedure = {"prompt": "Choose a unit",
    #             "func": lambda x: print(f"view_units procedure run with input {x}"),
    #             "input_req": True,
    #             "lowerBound": 1,
    #             "upperBound": 2
    #             }
    # view_units.add_procedure(**procedure)

    payments.add_children([to_main, exit_app])

    return menu