import validation as val
import sql_helper as sql
import pandas as pd

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
        self.to_main.add_procedure(self.menu.to_main)

        # go to previous menu

        self.go_back = Node(option_label="Previous Menu")
        self.go_back.add_procedure(lambda: Node.last_node.parent)

        # exit application

        self.exit_app = Node(option_label="Exit App")
        self.exit_app.add_procedure(self.menu.exit_app)

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    def store_selected_unit(self, ref_node):
        selected_unit, index = pick(Unit.get_all_instances(), "Choose Unit")

        ref_node.data_ref = selected_unit # store selected unit
        ref_node.title_label = f"Selected Unit: {selected_unit}"

    def print_expense_history(self, ref_node):
        unit = ref_node.data_ref
        df = unit.transactions()

        self.menu.print_to_csv(df, "EXPENSES", f"UNIT_{str(unit.id)}")

    def save_tenant_info(self, ref_node):
        new_tenant = self.menu.new_itm_validation(Tenant.VALIDATION_DICT)  

        if not new_tenant:
            return
    
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

        if not new_expense:
            return

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

        # select unit

        select_unit = Node(option_label="Select Unit")
        select_unit.add_procedure(lambda: self.store_selected_unit(select_unit))

        # view expense history

        view_expenses = Node(option_label="View Expense History")
        view_expenses.add_procedure(lambda: self.print_expense_history(select_unit))

        # add expense
        
        add_expense = Node(option_label="Add Expense")
        add_expense.add_procedure(lambda: self.save_expense_info(select_unit))

        # attach nodes to parent elements

        select_unit.add_children([view_expenses, add_expense, self.go_back, self.to_main, self.exit_app])
        rentals.add_children([select_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    def store_selected_tenant(self, ref_node):
        tenants = Tenant.get_all_instances()

        filter, index = pick([True, False], "Filter by Active Only?")
        tenant_list = []
        
        if filter:
            for tenant in tenants:
                if tenant.move_out_date is None:
                    tenant_list.append(tenant)
                elif datetime.strptime(tenant.move_out_date, '%Y-%m-%d') > datetime.now():
                    tenant_list.append(tenant)
        else:
            tenant_list = tenants

        selected_tenant, index = pick(tenant_list, "Choose Tenant")

        ref_node.data_ref = selected_tenant # store selected unit
        ref_node.title_label = f"Selected Tenant: {selected_tenant}"

    def update_selected_tenant(self, ref_node):
        tenant = ref_node.data_ref
        print('Original:')
        print(tenant)        
        self.menu.update_itm_validation(inst=tenant, val_dict=Tenant.VALIDATION_DICT)

        print("Updated:")
        print(tenant)

        confirm = input(f"Save changes? (Y/N)")

        if confirm == "Y":
            tenant.update()

            print("")
        else:
            print("Changes not saved")

    def print_payment_history(self, ref_node):
        tenant = ref_node.data_ref
        df = tenant.get_rollforward()

        self.menu.print_to_csv(df, "PMTS", tenant.name.upper())

    def save_payment_info(self, ref_node):
        tenant = ref_node.data_ref

        new_payment = self.menu.new_itm_validation(Payment.VALIDATION_DICT)  

        if not new_payment:
            return
        
        new_payment["tenant_id"] = tenant.id

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

        # select tenant

        select_tenant = Node(option_label="Select Tenant")
        select_tenant.add_procedure(lambda: self.store_selected_tenant(select_tenant))

        # view payment history

        view_payments = Node(option_label="View Payments History")
        view_payments.add_procedure(lambda: self.print_payment_history(select_tenant))

        # add payment

        add_payment = Node(option_label="Add Payment")
        add_payment.add_procedure(lambda: self.save_payment_info(select_tenant))

        # edit tenant information
        
        edit_tenant = Node(option_label="Edit Tenant Information")
        edit_tenant.add_procedure(lambda: self.update_selected_tenant(select_tenant))
        
        # attach nodes to parent elements
        
        select_tenant.add_children([view_payments, add_payment, edit_tenant, self.go_back, self.to_main, self.exit_app])
        
        tenants.add_children([select_tenant, self.to_main, self.exit_app])
        
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
        return sql.get_all_transactions()

    def print_summary_report(self):
        df = self.generate_summary_report()
        self.menu.print_to_csv(df, "INCOME_SUMMARY", "ALL_UNITS")

    def output_revenue_report(self):
        from report import generate_income_report

        df = self.generate_transactions()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year

        years = df['Year'].unique()

        year, index = pick(years, "Choose Year")
        generate_income_report(year)

    def add_summary_ops(self):
        income = Node(option_label="Revenue")

        # print summary report

        income_summary = Node(option_label="Summary of Income")
        income_summary.add_procedure(self.print_summary_report)

        # print detailed income information

        income_detailed = Node(option_label="View All Transactions")
        income_detailed.add_procedure(self.print_transactions)

        # output pdf revenue report

        revenue_report = Node(option_label="Generate Revenue Report")
        revenue_report.add_procedure(self.output_revenue_report)

        # attach nodes to parent elements

        income.add_children([income_summary, income_detailed, revenue_report, self.to_main, self.exit_app])
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