from menu_tree import MenuTree, Node
from unit import Unit
from tenant import Tenant
from payment import Payment

class PopulateMenu:

    def __init__(self):
        self.main = Node(label="Main Menu")
        self.menu = MenuTree(self.main)

        self.to_main = None
        self.go_back = None
        self.exit_app = None

    # ///////////////////////////////////////////////////////////////
    # BASIC OPERATIONS

    def add_basic_ops(self):

        # go to main menu

        self.to_main = Node(label="Back to main menu")
        procedure = {"prompt": "Entering main menu...",
                    "func": self.menu.to_main,
                    }
        self.to_main.add_procedure(**procedure)

        # go to previous menu

        self.go_back = Node(label="Back to previous menu")
        procedure = {"prompt": "Going back one level...",
                    "func": self.go_back.go_back,
                    }
        self.go_back.add_procedure(**procedure)

        # exit application

        self.exit_app = Node(label="Exit App")
        procedure = {"prompt": "Exiting application...",
                    "func": self.menu.exit_app,
                    }
        self.exit_app.add_procedure(**procedure)

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    def print_selected_unit(self, unit_id, ref_node):
        selected_unit = Unit.find_by_id(unit_id)
        print(selected_unit)

        ref_node.data_ref = selected_unit # store selected unit

    def add_unit_ops(self):

        rentals = Node(label="Rental Units")

        # view units

        view_units = Node(label="View All")
        procedure = {"prompt": "View all units",
                    "func": lambda: print(Unit.get_dataframe())
                    }
        view_units.add_procedure(**procedure)

        select_unit = Node(label="Select Unit")
        procedure = {"prompt": f"Choose a unit from the following options: \n{Unit.get_dataframe()}",
                    "func": lambda x: self.print_selected_unit(x, select_unit),
                    "input_req": True
                    }
        select_unit.add_procedure(**procedure)

        # edit units

        edit_unit = Node(label="Edit Unit")

        select_unit.add_children([edit_unit, self.go_back, self.to_main, self.exit_app])

        # attach nodes to parent elements

        rentals.add_children([view_units, select_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    def print_selected_tenant(self, tenant_id, ref_node):
        selected_tenant = Tenant.find_by_id(tenant_id)
        print(selected_tenant)

        ref_node.data_ref = selected_tenant # store selected unit

    def get_payment_info(self, id):
        new_payment = {}

        for item in ["amount", "pmt_date", "method", "pmt_type"]:
            value = input(f"Enter {item}")

            new_payment[item] = value

        new_payment["tenant_id"] = id

        print(new_payment)

        return new_payment

    def save_payment_info(self, ref_node):
        id = ref_node.data_ref.id
        new_payment = self.get_payment_info(id)

        confirm = input(f"Save payment? (Y/N)")
        
        if confirm == "Y":
            payment = Payment(
                amount=float(new_payment["amount"]),
                pmt_date=new_payment["pmt_date"],
                method=new_payment["method"],
                tenant_id=int(new_payment["tenant_id"]),                
                pmt_type=new_payment["pmt_type"],
            )
            payment.save()
            payment.print_receipt()
        else:
            print("Did not save to database")

    def add_tenant_ops(self):
        tenants = Node(label="Tenants")

        # view tenants

        view_tenants = Node(label="View All")
        procedure = {"prompt": "View all tenants",
                    "func": lambda: print(Tenant.get_dataframe())
                    }
        view_tenants.add_procedure(**procedure)

        # select tenant

        select_tenant = Node(label="Select Tenant")
        procedure = {"prompt": f"Choose a tenant from the following options: \n{Tenant.get_dataframe()}",
                    "func": lambda x: self.print_selected_tenant(x, select_tenant),
                    "input_req": True
                    }
        select_tenant.add_procedure(**procedure)

        # view payment history

        view_payments = Node(label="View Payments History")
        procedure = {"prompt": f"Showing payment history...",
                    "func": lambda: print(select_tenant.data_ref.payments()),
                    }
        view_payments.add_procedure(**procedure)

        # print payment history

        print_payments = Node(label="Print Payment History")
        procedure = {"prompt": f"Printing payment history...",
                    "func": lambda: select_tenant.data_ref.print_payments(),
                    }
        print_payments.add_procedure(**procedure)

        # add payment
        add_payment = Node(label="Add new payment")
        procedure = {"prompt": f"Add payment",
                    "func": lambda: self.save_payment_info(select_tenant)
                    }
        add_payment.add_procedure(**procedure)

        # edit tenant information
        
        edit_tenant = Node(label="Edit Tenant Information")
        
        # attach nodes to parent elements
        
        view_payments.add_children([print_payments, self.go_back, self.to_main, self.exit_app])
        edit_tenant.add_children([self.go_back, self.to_main, self.exit_app])
        
        select_tenant.add_children([view_payments, add_payment, edit_tenant, self.go_back, self.to_main, self.exit_app])
        
        tenants.add_children([view_tenants, select_tenant, self.to_main, self.exit_app])
        
        self.main.add_child(tenants)

    # ///////////////////////////////////////////////////////////////
    # SET UP PAYMENT OPERATIONS

    def add_payment_ops(self):
        payments = Node(label="Payments")

        # income summary
        income_summary = Node(label="Summary of Income")
        procedure = {"prompt": f"Printing summary of income...",
                    "func": lambda: print(Payment.payment_summary()),
                    }
        income_summary.add_procedure(**procedure)

        # attach nodes to parent elements

        payments.add_children([income_summary, self.to_main, self.exit_app])
        self.main.add_child(payments)

def populate_menu():
    rental_mgmt = PopulateMenu() # create feedback loop by populating tree

    rental_mgmt.add_basic_ops()
    rental_mgmt.add_unit_ops()
    rental_mgmt.add_tenant_ops()
    rental_mgmt.add_payment_ops()
    rental_mgmt.main.add_child(rental_mgmt.exit_app)

    menu = rental_mgmt.menu

    menu.display_welcome()

    return menu