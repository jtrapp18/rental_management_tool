import validation as val
import sql_helper as sql

from menu_tree import MenuTree, Node
from rich import print
from pick import pick
from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense
from datetime import datetime

class PopulateMenu:

    def __init__(self):
        self.main = Node(option_label="Main Menu")
        self.menu = MenuTree(self.main)

        self.to_main = None
        self.go_back = None
        self.exit_app = None

    # ///////////////////////////////////////////////////////////////
    # BASIC OPERATIONS

    def add_basic_ops(self):

        # go to main menu

        self.to_main = Node(option_label="Go to Main Menu")
        procedure = {"prompt": "Entering main menu...",
                    "func": self.menu.to_main,
                    }
        self.to_main.add_procedure(**procedure)

        # go to previous menu

        self.go_back = Node(option_label="Previous Menu")
        procedure = {"prompt": "Going back one level...",
                    "func": self.go_back.go_back,
                    }
        self.go_back.add_procedure(**procedure)

        # exit application

        self.exit_app = Node(option_label="Exit App")
        procedure = {"prompt": "Exiting application...",
                    "func": self.menu.exit_app,
                    }
        self.exit_app.add_procedure(**procedure)

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    def print_selected_unit(self, ref_node):
        selected_unit, index = pick(Unit.get_all_instances(), "Choose Unit")

        print(selected_unit)

        ref_node.data_ref = selected_unit # store selected unit
        ref_node.title_label = f"Selected Unit: {selected_unit.id}"

    def print_expense_history(self, ref_node):
        unit = ref_node.data_ref
        df = unit.transactions()

        self.menu.print_to_csv(df, "EXPENSES", f"UNIT_{str(unit.id)}")

    def save_tenant_info(self, ref_node):
        new_tenant = self.menu.new_itm_validation(Tenant.VALIDATION_DICT)  
        new_tenant["unit_id"] = ref_node.data_ref.id

        print(new_tenant)

        confirm = input(f"Save tenant? (Y/N)")
        
        if confirm == "Y":
            tenant = Tenant(
                name=new_tenant["name"],
                email_address=new_tenant["email_address"],
                phone_number=new_tenant["phone_number"],
                move_in_date=new_tenant["move_in_date"],
                unit_id=int(new_tenant["unit_id"])             
            )
            tenant.save()
        else:
            print("Did not save to database")

    def save_expense_info(self, ref_node):
        new_expense = self.menu.new_itm_validation(Expense.VALIDATION_DICT)  
        new_expense["unit_id"] = ref_node.data_ref.id

        print(new_expense)

        confirm = input(f"Save expense? (Y/N)")
        
        if confirm == "Y":
            expense = Expense(
                descr=new_expense["descr"],
                amount=float(new_expense["amount"]),
                exp_date=new_expense["exp_date"],
                unit_id=int(new_expense["unit_id"]),                
            )
            expense.save()
        else:
            print("Did not save to database")

    def add_unit_ops(self):

        rentals = Node(option_label="Rental Units")

        # view units

        view_units = Node(option_label="View All")
        procedure = {"prompt": "View all units",
                    "func": lambda: print(Unit.get_dataframe())
                    }
        view_units.add_procedure(**procedure)

        select_unit = Node(option_label="Select Unit")
        procedure = {"prompt": f"Choose a unit from the following options: \n{Unit.get_dataframe()}",
                    "func": lambda: self.print_selected_unit(select_unit)
                    }
        select_unit.add_procedure(**procedure)

        # view expense history

        view_expenses = Node(option_label="View Expense History")
        procedure = {"prompt": f"Showing expense history...",
                    "func": lambda: self.print_expense_history(select_unit),
                    }
        view_expenses.add_procedure(**procedure)

        # add expense
        
        add_expense = Node(option_label="Add Expense")
        procedure = {"prompt": f"Add expense",
                    "func": lambda: self.save_expense_info(select_unit)
                    }
        add_expense.add_procedure(**procedure)

        # attach nodes to parent elements

        select_unit.add_children([view_expenses, add_expense, self.go_back, self.to_main, self.exit_app])
        rentals.add_children([view_units, select_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    def print_selected_tenant(self, ref_node):
        selected_tenant, index = pick(Tenant.get_all_instances(), "Choose Tenant")

        print(selected_tenant)

        ref_node.data_ref = selected_tenant # store selected unit
        ref_node.title_label = f"Selected Tenant: {selected_tenant.name}"

    def print_payment_history(self, ref_node):
        tenant = ref_node.data_ref
        df = tenant.payments()

        self.menu.print_to_csv(df, "PMTS", tenant.name.upper())

    def save_payment_info(self, ref_node):
        new_payment = self.menu.new_itm_validation(Payment.VALIDATION_DICT)  
        new_payment["tenant_id"] = ref_node.data_ref.id

        print(new_payment)

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

            print("")
        else:
            print("Did not save to database")

    def add_tenant_ops(self):
        tenants = Node(option_label="Tenants")

        # view tenants

        view_tenants = Node(option_label="View All")
        procedure = {"prompt": "View all tenants",
                    "func": lambda: print(Tenant.get_dataframe())
                    }
        view_tenants.add_procedure(**procedure)

        # select tenant

        select_tenant = Node(option_label="Select Tenant")
        procedure = {"prompt": f"Choose a tenant from the following options: \n{Tenant.get_dataframe()}",
                    "func": lambda: self.print_selected_tenant(select_tenant),
                    }
        select_tenant.add_procedure(**procedure)

        # view payment history

        view_payments = Node(option_label="View Payments History")
        procedure = {"prompt": f"Showing payment history...",
                    "func": lambda: self.print_payment_history(select_tenant),
                    }
        view_payments.add_procedure(**procedure)

        # add payment

        add_payment = Node(option_label="Add Payment")
        procedure = {"prompt": f"Add payment",
                    "func": lambda: self.save_payment_info(select_tenant)
                    }
        add_payment.add_procedure(**procedure)

        # edit tenant information
        
        edit_tenant = Node(option_label="Edit Tenant Information")
        
        # attach nodes to parent elements
        
        edit_tenant.add_children([self.go_back, self.to_main, self.exit_app])
        
        select_tenant.add_children([view_payments, add_payment, edit_tenant, self.go_back, self.to_main, self.exit_app])
        
        tenants.add_children([view_tenants, select_tenant, self.to_main, self.exit_app])
        
        self.main.add_child(tenants)

    # ///////////////////////////////////////////////////////////////
    # SET UP SUMMARY OPERATIONS

    def generate_transactions(self):
        return sql.get_all_transactions()

    def print_transactions(self):
        df = self.generate_transactions()
        print(df)

        self.menu.print_to_csv(df, "TRANSACTIONS", "ALL_UNITS")

    def generate_summary_report(self):
        return Payment.payment_summary()

    def print_summary_report(self):
        df = self.generate_summary_report()
        self.menu.print_to_csv(df, "INCOME_SUMMARY", "ALL_UNITS")

    def add_summary_ops(self):
        income = Node(option_label="Income")

        # print summary report

        income_summary = Node(option_label="Summary of Income")
        procedure = {"prompt": f"Printing summary of income...",
                    "func": self.print_summary_report,
                    }
        income_summary.add_procedure(**procedure)

        # print detailed income information

        income_detailed = Node(option_label="View All Transactions")
        procedure = {"prompt": f"Printing transactions...",
                    "func": self.print_transactions,
                    }
        income_detailed.add_procedure(**procedure)

        # attach nodes to parent elements

        income.add_children([income_summary, income_detailed, self.to_main, self.exit_app])
        self.main.add_child(income)

def populate_menu():
    rental_mgmt = PopulateMenu() # create feedback loop by populating tree

    rental_mgmt.add_basic_ops()
    rental_mgmt.add_unit_ops()
    rental_mgmt.add_tenant_ops()
    rental_mgmt.add_summary_ops()
    rental_mgmt.main.add_child(rental_mgmt.exit_app)

    menu = rental_mgmt.menu

    menu.display_welcome()

    return menu