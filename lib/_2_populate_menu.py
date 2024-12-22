import validation as val

from menu_tree import MenuTree, Node
from rich import print
from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense
from datetime import datetime

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

    def print_expense_history(self, ref_node):
        unit = ref_node.data_ref
        df = unit.expenses()
        print(df)
              
        confirm = input(f"Print expense history for unit {str(unit.id)} to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/EXPENSES_AS_OF_{date_today}_FOR_{str(unit.id)}.csv"
            df.to_csv(path, index=False)

            self.menu.print_message(path)

    def get_expense_info(self, id):
        expense_info = {
            "descr": val.descr_validation,
            "amount": val.dollar_amt_validation,
            "exp_date": val.date_validation
        }

        new_expense = self.menu.new_itm_validation(expense_info)  
        new_expense["unit_id"] = id

        print(new_expense)

        return new_expense

    def save_expense_info(self, ref_node):
        id = ref_node.data_ref.id
        new_expense = self.get_expense_info(id)

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

        # view expense history

        view_expenses = Node(label="View Expense History")
        procedure = {"prompt": f"Showing expense history...",
                    "func": lambda: self.print_expense_history(select_unit),
                    }
        view_expenses.add_procedure(**procedure)

        # add expense
        
        add_expense = Node(label="Add new expense")
        procedure = {"prompt": f"Add expense",
                    "func": lambda: self.save_expense_info(select_unit)
                    }
        add_expense.add_procedure(**procedure)

        # edit units

        edit_unit = Node(label="Edit Unit")

        # attach nodes to parent elements

        select_unit.add_children([view_expenses, add_expense, edit_unit, self.go_back, self.to_main, self.exit_app])
        rentals.add_children([view_units, select_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    def print_selected_tenant(self, tenant_id, ref_node):
        selected_tenant = Tenant.find_by_id(tenant_id)
        print(selected_tenant)

        ref_node.data_ref = selected_tenant # store selected unit

    def print_payment_history(self, ref_node):
        tenant = ref_node.data_ref
        df = tenant.payments()
        print(df)
              
        confirm = input(f"Print payment history for {tenant.name} to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/PMTS_AS_OF_{date_today}_FOR_{tenant.name}.csv"
            df.to_csv(path, index=False)

            self.menu.print_message(path)

    def get_payment_info(self, id):
        payment_info = {
            "amount": val.descr_validation,
            "pmt_date": val.dollar_amt_validation,
            "method": val.date_validation,
            "pmt_type": val.date_validation
        }

        new_payment = self.menu.new_itm_validation(payment_info)  
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

            print("")
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
                    "func": lambda: self.print_payment_history(select_tenant),
                    }
        view_payments.add_procedure(**procedure)

        # add payment

        add_payment = Node(label="Add new payment")
        procedure = {"prompt": f"Add payment",
                    "func": lambda: self.save_payment_info(select_tenant)
                    }
        add_payment.add_procedure(**procedure)

        # edit tenant information
        
        edit_tenant = Node(label="Edit Tenant Information")
        
        # attach nodes to parent elements
        
        edit_tenant.add_children([self.go_back, self.to_main, self.exit_app])
        
        select_tenant.add_children([view_payments, add_payment, edit_tenant, self.go_back, self.to_main, self.exit_app])
        
        tenants.add_children([view_tenants, select_tenant, self.to_main, self.exit_app])
        
        self.main.add_child(tenants)

    # ///////////////////////////////////////////////////////////////
    # SET UP SUMMARY OPERATIONS

    def generate_transactions(self):
        return Payment.payment_summary()

    def print_transactions(self):
        df = self.generate_transactions()
        print(df)
              
        confirm = input(f"Print transactions to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/TRANSACTIONS_AS_OF_{date_today}.csv"
            df.to_csv(path, index=False)

            self.menu.print_message(path)

    def generate_summary_report(self):
        return Payment.payment_summary()

    def print_summary_report(self):
        df = self.generate_summary_report()
        print(df)
              
        confirm = input(f"Print income report? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/INCOME_SUMMARY_AS_OF_{date_today}.csv"
            df.to_csv(path, index=False)

            self.menu.print_message(path)

    def add_summary_ops(self):
        income = Node(label="Income")

        # print summary report

        income_summary = Node(label="Summary of Income")
        procedure = {"prompt": f"Printing summary of income...",
                    "func": self.print_summary_report,
                    }
        income_summary.add_procedure(**procedure)

        # print detailed income information

        income_detailed = Node(label="View All Transactions")
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