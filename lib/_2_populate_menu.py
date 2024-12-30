import validation as val
import sql_helper as sql
import pandas as pd

from menu_tree import MenuTree, Node
from rich import print
from rich.console import Console
from pick import pick
from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense
from datetime import datetime

class PopulateMenu:
    '''
    A class to populate a menu tree for rental management application

    Attributes
    ---------
    main: Node instance
        - main menu node for application
    menu: MenuTree instance
        - current tree instance which uses main as the root node
    to_main: Node instance
        - node which takes user to main menu when selected
    go_back: Node instance
        - node which takes user to previous menu when selected
    exit_app: Node instance
        - node which exits user from application when selected

    Methods
    ---------
    - add_basic_ops: creates reusable menu items (main menu, previous menu, exit)
    - store_selected_instance: adds reference to selected instance within specified node
    - show_user_selections: displays user selections for adding or updating an instance
    - new_itm_validation: creates and validates new object to be used to create a new instance
    - update_itm_validation: updates an existing instance after validating user inputs
    - print_to_csv: prints data to csv file
    - print_transaction_history: displays unit transactions and optionally prints results to csv
    - save_tenant_info: allows user to create new Tenant instance and optionally saves to DB
    - save_expense_info: allows user to create new Expense instance and optionally saves to DB
    - add_unit_ops: creates and links nodes related to unit operations
    - store_selected_tenant: adds reference to selected Tenant instance within specified node
    - update_selected_tenant: updates an existing Tenant instance and saves changes to DB
    - print_payment_history: displays tenant payment history and optionally prints to csv
    - save_payment_info: allows user to create a new Payment instance and optionally saves to DB
    - add_tenant_ops: creates and links nodes related to tenant operations
    - print_transactions: displays transactions made and allows user to print to csv
    - print_summary_report: displays summary of transactions made and allows user to print to csv
    - output_revenue_report: generates revenue report and prints to pdf
    - add_summary_ops: creates and links nodes related to summary operations
    '''
    def __init__(self):
        '''
        Constructs the necessary attributes for the PopulateMenu object.
        '''
        self.main = Node(option_label="Main Menu")
        self.menu = MenuTree(self.main)

        self.to_main = None
        self.go_back = None
        self.exit_app = None

    # ///////////////////////////////////////////////////////////////
    # BASIC OPERATIONS

    def add_basic_ops(self):
        '''
        creates reusable menu items (main menu, previous menu, exit)

        Procedures
        ---------
        - creates main menu node and adds functionality
        - creates previous menu node and adds functionality
        - creates exit application node and adds functionality
        '''
        # go to main menu

        self.to_main = Node(option_label="Go to Main Menu")
        self.to_main.add_procedure(self.menu.to_main)

        # go to previous menu

        self.go_back = Node(option_label="Previous Menu")
        self.go_back.add_procedure(lambda: Node.last_node.parent)

        # exit application

        self.exit_app = Node(option_label="Exit App")
        self.exit_app.add_procedure(self.menu.exit_app)

    def store_selected_instance(self, cls, ref_node):
        '''
        adds reference to selected instance within specified node
        '''
        selected_inst, index = pick(cls.get_all_instances(), "Choose Unit")

        ref_node.data_ref = selected_inst # store selected unit
        ref_node.title_label = f"Selected: {selected_inst}"

    # ///////////////////////////////////////////////////////////////
    # REUSABLE CLI FUNCTIONALITY
    
    def show_user_selections(self, val_func, key):
        '''
        displays user selections for adding or updating an instance

        Parameters
        ---------
        val_func: dict
            - dictionary which stores validation functions for various class attributes
        key: str
            - name of current class attribute to add or update

        Returns
        ---------
        value: object
            - value selected or entered by user to be used for the new or updated class attribute 
        '''
        constraints = val_func.constraints

        def user_selection(constraints, key):
            '''
            returns pick or input object for user selection or input
            '''
            if isinstance(constraints, list):
                user_input, index = pick(constraints, f"Select {key} from the following options")
            else:
                user_input = input(f"Enter {key} ({constraints}): ")
            return user_input
        
        user_input = user_selection(constraints, key)

        if user_input == 'exit' or user_input =='e':
            return 'exit'

        while True:
            try:
                user_input = float(user_input) if key=="amount" else user_input
                value = val_func(user_input)
                return value
            except:
                self.invalid_option()
                user_input = user_selection(constraints, key)
    
    def new_itm_validation(self, val_dict):
        '''
        creates and validates new object to be used to create a new instance

        Parameters
        ---------
        val_func: dict
            - dictionary which stores validation functions for various class attributes

        Returns
        ---------
        new_obj: dict
            - dictionary containing information needed to create a new class instance
        '''
        new_obj = {}
        
        for key, val_func in val_dict.items():
            value = self.show_user_selections(val_func, key)

            if value == 'exit':
                return
            
            new_obj[key] = value

        return new_obj

    def update_itm_validation(self, inst, val_dict):
        '''
        updates an existing instance after validating user's desired changes

        Parameters
        ---------
        inst: class instance (e.g. Tenant)
            - instance to be updated by user
        val_func: dict
            - dictionary which stores validation functions for various class attributes

        Procedures
        ---------
        - updates selected instance with user-selected or user-entered values
        '''
        attributes = [f"{key}: {getattr(inst, key, None)}" for key in val_dict]
        itm_to_update, index = pick(attributes+['SUBMIT CHANGES'], "Choose item to update")

        if itm_to_update == 'SUBMIT CHANGES':
            return
        
        key = itm_to_update.split(":")[0].strip()
        val_func = val_dict[key]

        value = self.show_user_selections(val_func, key)
        
        if value == 'exit':
            return
        
        setattr(inst, key, value)

        self.update_itm_validation(inst, val_dict)
    
    def print_to_csv(self, df, report_type, report_for):
        '''
        prints data to csv file

        Parameters
        ---------
        df: Pandas DataFrame
            - data to print to csv
        report_type: str
            - used in the filename of the report
        report_for: str
            - used in the filename to specify report filters (e.g. tenant name)
        '''
        print(df)
              
        confirm = input(f"Print output to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/{report_type}_AS_OF_{date_today}_FOR_{report_for}.csv"
            df.to_csv(path, index=False)

            self.menu.print_message(path)

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    def print_transaction_history(self, ref_node):
        '''
        displays unit transactions and optionally prints results to csv

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        unit = ref_node.data_ref
        df = unit.transactions()

        self.print_to_csv(df, "TRANSACTIONS", f"UNIT_{str(unit.id)}")

    def save_tenant_info(self, ref_node):
        '''
        allows user to create new Tenant instance and optionally saves to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        new_tenant = self.new_itm_validation(Tenant.VALIDATION_DICT)  

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
        '''
        allows user to create new Expense instance and optionally saves to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        new_expense = self.new_itm_validation(Expense.VALIDATION_DICT)

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
        '''
        creates and links nodes related to unit operations

        Procedures
        ---------
        - creates rental node with multiple children nodes
        - adds rental node as a child of the main menu node
        '''
        rentals = Node(option_label="Rental Units")

        # select unit

        select_unit = Node(option_label="Select Unit")
        select_unit.add_procedure(lambda: self.store_selected_instance(Unit, select_unit))

        # view transaction history

        view_transactions = Node(option_label="View Transaction History")
        view_transactions.add_procedure(lambda: self.print_transaction_history(select_unit))

        # add expense
        
        add_expense = Node(option_label="Add Expense")
        add_expense.add_procedure(lambda: self.save_expense_info(select_unit))

        # attach nodes to parent elements

        select_unit.add_children([view_transactions, add_expense, self.go_back, self.to_main, self.exit_app])
        rentals.add_children([select_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP TENANT OPERATIONS

    def store_selected_tenant(self, ref_node):
        '''
        adds reference to selected Tenant instance within specified node

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
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
        '''
        updates an existing Tenant instance and saves changes to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        tenant = ref_node.data_ref
        print('Original:')
        print(tenant)        
        self.update_itm_validation(inst=tenant, val_dict=Tenant.VALIDATION_DICT)

        print("Updated:")
        print(tenant)

        confirm = input(f"Save changes? (Y/N)")

        if confirm == "Y":
            tenant.update()

            print("")
        else:
            print("Changes not saved")

    def print_payment_history(self, ref_node):
        '''
        displays tenant payment history and optionally prints to csv

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        tenant = ref_node.data_ref
        df = tenant.get_rollforward()

        self.print_to_csv(df, "PMTS", tenant.name.upper())

    def save_payment_info(self, ref_node):
        '''
        allows user to create a new Payment instance and optionally saves to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        tenant = ref_node.data_ref

        new_payment = self.new_itm_validation(Payment.VALIDATION_DICT)  

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
        '''
        creates and links nodes related to tenant operations

        Procedures
        ---------
        - creates tenants node with multiple children nodes
        - adds tenants node as a child of the main menu node
        '''
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

    def print_transactions(self):
        '''
        displays transactions made and allows user to print to csv
        '''
        df = sql.get_all_transactions()
        print(df)

        self.print_to_csv(df, "TRANSACTIONS", "ALL_UNITS")

    def print_summary_report(self):
        '''
        displays summary of transactions made and allows user to print to csv
        '''
        df = sql.get_all_transactions()
        print(df)

        self.print_to_csv(df, "INCOME_SUMMARY", "ALL_UNITS")

    def output_revenue_report(self):
        '''
        generates revenue report and prints to pdf
        '''
        from report import generate_income_report

        df = sql.get_all_transactions()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year

        years = df['Year'].unique()

        year, index = pick(years, "Choose Year")
        generate_income_report(year)

    def add_summary_ops(self):
        '''
        creates and links nodes related to summary operations

        Procedures
        ---------
        - creates income node with multiple children nodes
        - adds income node as a child of the main menu node
        '''
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
    '''
    creates an instance of PopulateMenu and runs methods to create tree

    Returns
    ---------
    menu: MenuTree instance
        - instance of MenuTree class pre-populated with rental management CLI nodes
    '''
    rental_mgmt = PopulateMenu() # create feedback loop by populating tree

    rental_mgmt.add_basic_ops()
    rental_mgmt.add_unit_ops()
    rental_mgmt.add_tenant_ops()
    rental_mgmt.add_summary_ops()
    rental_mgmt.main.add_child(rental_mgmt.exit_app)

    menu = rental_mgmt.menu

    menu.display_welcome()

    return menu