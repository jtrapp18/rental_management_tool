
import pandas as pd
import art
from lib import MenuTree, Node
from rich import print
from pick import pick
from datetime import datetime

# project modules
from lib.helper import ascii
from lib.helper import validation as val
from lib.helper import sql_helper as sql
from lib import Unit
from lib import Tenant
from lib import Payment
from lib import Expense

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
    select_tenant: Node instance
        - node which allows user to select tenant
    select_unit: Node instance
        - node which allows user to select unit
    add_tenant: Node instance
        - node which allows user to add a new tenant

    Methods
    ---------
    - add_basic_ops: creates reusable menu items (main menu, previous menu, exit)
    - store_selected_instance: adds reference to selected instance within specified node
    - show_user_selections: displays user selections for adding or updating an instance
    - new_itm_validation: creates and validates new object to be used to create a new instance
    - finalize_add: saves new instance and prints confirmation message
    - update_itm_validation: updates an existing instance after validating user inputs
    - finalize_update: updates instance based on user selections and prints confirmation message
    - update_selected_instance: updates an existing class instance and saves changes to DB
    - finalize_delete: deletes instance and prints confirmation message
    - delete_selected_instance: deletes an existing class instance and saves changes to DB
    - print_to_csv: prints data to csv file
    - filter_on_dates: filters dataframe by user-specified start and end dates
    - print_transaction_history: displays unit transactions and optionally prints results to csv
    - print_transaction_summary: displays summary of transactions made and allows user to print to csv    
    - run_func_if_confirm: confirms if a specific procedure should be run then runs that procedure
    - store_selected_tenant: adds reference to selected Tenant instance within specified node
    - print_payment_history: displays tenant payment history and optionally prints to csv
    - save_payment_info: allows user to create a new Payment instance and optionally saves to DB
    - add_tenant_ops: creates and links nodes related to tenant operations
    - save_unit_info: allows user to create new Unit instance and optionally saves to DB
    - save_tenant_info: allows user to create new Tenant instance and optionally saves to DB
    - save_expense_info: allows user to create new Expense instance and optionally saves to DB
    - add_unit_ops: creates and links nodes related to unit operations
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

        self.select_tenant = None
        self.select_unit = None

        self.add_tenant = None

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

        self.to_main = Node(option_label="Main Menu")
        self.to_main.add_procedure(self.menu.to_main)

        # go to previous menu

        self.go_back = Node(option_label="Previous Menu")
        self.go_back.add_procedure(lambda: Node.last_node.parent)

        # exit application

        self.exit_app = Node(option_label="Exit App")
        self.exit_app.add_procedure(self.menu.exit_app)

    def update_title_labels(self, inst, ref_node):
        '''
        updates labels in cli based on selected instance

        Parameters
        ---------
        inst: class instance (e.g. Tenant)
            - instance to use for labeling
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        ref_node.data_ref = inst # store selected unit
        ref_node.title_label = f"Options for: {inst}"

        for child in ref_node.children:
            child.title_label = f"Options for: {inst}"

    def store_selected_instance(self, cls, ref_node, parent_ref=None, options=None):
        '''
        adds reference to selected instance within specified node

        Parameters
        ---------
        cls: class
            - class to choose instance from
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        parent_ref (optional): Node instance
            - node which stores the reference to the parent of the user-selected instance
        options (optional):
            - list of user options to choose from (defaults to all class instances)
        '''
        if not options:
            options = cls.get_all_instances()
        
        if parent_ref:
            if parent_ref.data_ref:
                parent = parent_ref.data_ref
                parent_name = parent.__class__.__name__.lower()
                options = [inst for inst in options if getattr(inst, f"{parent_name}_id")==parent.id]

        selected_inst, index = pick(options, f"Select {cls.__name__} from options below")

        self.update_title_labels(selected_inst, ref_node)

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
        'exit': str
            - returns 'exit' if user chooses to cancel input
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

        if user_input.lower() == 'exit' or user_input.lower() =='e':
            return 'exit'

        while True:
            try:
                func_name = val_func.__name__
                user_input = float(user_input) if func_name=="dollar_amt_validation" else user_input
                value = val_func(user_input)

                # show selected value if using pick functionality
                if isinstance(constraints, list):
                    print(f'Enter {key}: {value}')

                return value
            except:
                self.menu.invalid_option()
                user_input = user_selection(constraints, key)

                if user_input == 'exit' or user_input =='e':
                    return 'exit'
    
    def new_itm_validation(self, cls, parent=None):
        '''
        creates and validates new object to be used to create a new instance

        Parameters
        ---------
        cls: class
            - class to use for new instance
        parent (optional): class instance
            - instance of parent class to link new item with

        Returns
        ---------
        new_obj: dict
            - dictionary containing information needed to create a new class instance
        '''
        new_obj = {}
        img_dict = {
            Unit: ascii.house(),
            Payment: ascii.money(),
            Expense: ascii.money()
        }
        
        self.menu.print_page_header(f"Add {cls.__name__}", f"Add information for new {cls.__name__} record below")
        print(img_dict.get(cls, ""))

        if parent:
            parent_name = parent.__class__.__name__
            print(f"For: [magenta]{parent}[/magenta]")

        self.menu.print_cancellation_directions()
        print("")

        val_dict = cls.VALIDATION_DICT
        
        for key, val_func in val_dict.items():
            value = self.show_user_selections(val_func, key)

            if value == 'exit':
                return
            
            new_obj[key] = value

        if parent:
            new_obj[f"{parent_name.lower()}_id"] = parent.id

        print("")
        print(f"[bright_green]New {cls.__name__} Details:[/bright_green]")
        print(new_obj)
        print("")

        confirm = input(f"Save {cls.__name__}? (Y/N) ")
        
        if confirm.lower() == "y":
            return new_obj
        
    def finalize_add(self, inst):
        '''
        saves new instance and prints confirmation message

        Parameters
        ---------
        inst: class instance
            - newly added instance
        '''
        inst.save()
        
        print("")
        print(f"The following record was successfully added:")
        print(f"[green]{inst}[/green]")
        self.menu.print_continue_message()

    def update_itm_validation(self, inst):
        '''
        updates an existing instance after validating user's desired changes

        Parameters
        ---------
        inst: class instance (e.g. Tenant)
            - instance to be updated by user

        Procedures
        ---------
        - updates selected instance with user-selected or user-entered values
        '''
        cls = inst.__class__
        val_dict = cls.VALIDATION_DICT
        attributes = [f"{key}: {getattr(inst, key, None)}" for key in val_dict]
        itm_to_update, index = pick(attributes+['<SUBMIT CHANGES>'], 
                                    f"Select Attribute of {cls.__name__} to Update")

        if itm_to_update == '<SUBMIT CHANGES>':
            return
        
        key = itm_to_update.split(":")[0].strip()
        val_func = val_dict[key]

        value = self.show_user_selections(val_func, key)
        
        if value == 'exit':
            return
        
        setattr(inst, key, value)

        self.update_itm_validation(inst)

    def finalize_update(self, ref_node):
        '''
        updates instance based on user selections and prints confirmation message

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        inst = ref_node.data_ref
        inst.update()

        self.update_title_labels(inst, ref_node)
        
        print("")
        print(f"The following record was successfully saved:")
        print(f"[green]{inst}[/green]")
        self.menu.print_continue_message()

    def update_selected_instance(self, ref_node):
        '''
        updates an existing class instance and saves changes to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        inst = ref_node.data_ref
        class_name = inst.__class__.__name__

        self.menu.print_page_header(f"Update {class_name}", inst)
        self.menu.print_cancellation_directions()
        print("")

        self.update_itm_validation(inst=inst)
        print("")

        print(f"Updated: [yellow]{inst}[/yellow]")
        print("")

        self.run_func_if_confirm('Save changes?', lambda: self.finalize_update(ref_node))

    def finalize_delete(self, ref_node):
        '''
        deletes instance and prints confirmation message

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        inst = ref_node.data_ref
        inst.delete()

        ref_node.data_ref = None

        print("")
        print(f"The following record was successfully deleted:")
        print(f"[red]{inst}[/red]")
        self.menu.print_continue_message()

    def delete_selected_instance(self, ref_node):
        '''
        deletes an existing class instance and saves changes to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        inst = ref_node.data_ref
        class_name = inst.__class__.__name__

        self.menu.print_page_header(f"Delete {class_name} Record", inst)
        self.run_func_if_confirm('Confirm delete?', lambda: self.finalize_delete(ref_node))

        return Node.last_node.parent

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
        date_today = datetime.now().strftime('%Y-%m-%d')

        print(art.text2art(f"{report_type}", font='tarty4'))
        print("")
        print(f"[yellow]For {report_for} as of {date_today}[/yellow]")
        print("")
        print(df)
        print("")

        filename = f"{report_type}_AS_OF_{date_today}_FOR_{report_for}".replace(' ', '_').upper()
        path = f"./outputs/{filename}.csv"

        funcs_to_run = [
            lambda: df.to_csv(path),
            lambda: self.menu.print_output_message(path)
        ]
        self.run_func_if_confirm('Print data to CSV in outputs folder?', 
                                 funcs_to_run)
        
    def filter_on_dates(self, df):
        '''
        filters dataframe by user-specified start and end dates

        Parameters
        ---------
        df: Pandas DataFrame
            - data to filter

        Returns
        ---------
        df_filtered: Pandas DataFrame
            - data filtered based on user choices
        '''
        df_filtered = df.copy()

        self.menu.print_page_header('Enter Date Range', 'Enter date range to filter data')
        self.menu.print_cancellation_directions()
        self.menu.print_directions('Click enter to bypass date filters')
        print("")

        user_choices = {
            'start date': None,
            'end date': None
        }

        for key in ['start date', 'end date']:
            value = self.show_user_selections(val.optional_date_validation, key)

            if value == 'exit':
                return
            
            user_choices[key] = value

        if user_choices['start date'] is not None:
            df_filtered = df_filtered[df_filtered['Date'] >= user_choices['start date']]
        if user_choices['end date'] is not None:
            df_filtered = df_filtered[df_filtered['Date'] <= user_choices['end date']]

        if user_choices['start date'] and user_choices['end date']:
            print("")
            print(f"Date filter applied: [bold green]{user_choices['start date']} to {user_choices['end date']}[/bold green]")
        elif user_choices['end date'] and not user_choices['start date']:
            print("")
            print(f"Date filter applied: [bold green]before or on {user_choices['end date']}[/bold green]")
        elif user_choices['start date'] and not user_choices['end date']:
            print("")
            print(f"Date filter applied: [bold green]on or after {user_choices['start date']}[/bold green]")

        return df_filtered
    
    def print_transaction_history(self, ref_node=None):
        '''
        displays unit transactions and optionally prints results to csv

        Parameters
        ---------
        ref_node (optional): Node instance
            - node which stores the reference to the user-selected instance
        '''
        if ref_node:
            unit = ref_node.data_ref
            unit_id = unit.id
            label = f"Unit {str(unit.id)}"
        else:
            unit_id = None
            label = "all units"

        df = sql.get_all_transactions(unit_id)
        df_filtered = self.filter_on_dates(df)

        self.print_to_csv(df_filtered, "Transactions", label)

    def print_transaction_summary(self, ref_node=None):
        '''
        displays summary of transactions made and allows user to print to 
        
        Parameters
        ---------
        ref_node (optional): Node instance
            - node which stores the reference to the user-selected instance
        '''
        if ref_node:
            unit = ref_node.data_ref
            unit_id = unit.id
            label = f"Unit {str(unit.id)}"
        else:
            unit_id = None
            label = "all units"

        df = sql.get_transaction_summary(unit_id)
        self.print_to_csv(df, "Income Summary", label)

    def run_func_if_confirm(self, prompt, func):
        '''
        confirms if a specific procedure should be run then runs that procedure
        
        Parameters
        ---------
        prompt: str
            - 
        func: callable object or list of callable objects
            - function to run if user confirms
        '''
        confirm = input(f"{prompt} (Y/N) ")

        if confirm.lower() == "y":
            if isinstance(func, list):
                for f in func:
                    f()
            else:
                func()
            print("")

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
        filter, index = pick([True, False], "Filter on Active Tenants Only?")
        tenant_list = []
        tenants = Tenant.get_all_instances()

        if filter:
            for tenant in tenants:
                if tenant.move_out_date is None:
                    tenant_list.append(tenant)
                elif datetime.strptime(tenant.move_out_date, '%Y-%m-%d') > datetime.now():
                    tenant_list.append(tenant)
        else:
            tenant_list = tenants

        self.store_selected_instance(Tenant, ref_node, self.select_unit, options=tenant_list)
        
    def payment_rollforward(self, ref_node):
        '''
        displays tenant payment history and optionally prints to csv

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        tenant = ref_node.data_ref
        df = tenant.get_rollforward()

        self.print_to_csv(df, "PAYMENTS", tenant.name.upper())

    def save_payment_info(self, ref_node):
        '''
        allows user to create a new Payment instance and optionally saves to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        tenant = ref_node.data_ref

        new_payment = self.new_itm_validation(Payment, tenant)  

        if not new_payment:
            return

        payment = Payment(
            amount=float(new_payment["amount"]),
            pmt_date=new_payment["pmt_date"],
            method=new_payment["method"],
            tenant_id=int(new_payment["tenant_id"]),                
            category=new_payment["category"],
        )
        path = fr"./outputs/RECEIPT_FOR_{tenant.name.upper()}_{new_payment['pmt_date']}.pdf"
        payment.print_receipt(path)
        self.finalize_add(payment)
        self.menu.print_output_message(path)

    def add_tenant_ops(self):
        '''
        creates and links nodes related to tenant operations

        Procedures
        ---------
        - creates tenants node with multiple children nodes
        - adds tenants node as a child of the main menu node
        '''
        tenants = Node(option_label="Tenants")
        tenants.add_procedure(lambda: setattr(self.select_unit, "data_ref", None)) # clear unit information when accessing tenant

        # select tenant

        self.select_tenant = Node(option_label="Select Tenant")
        self.select_tenant.add_procedure(lambda: self.store_selected_tenant(self.select_tenant))

        # add tenant
        
        self.add_tenant = Node(option_label="Add Tenant")
        self.add_tenant.add_procedure(lambda: self.save_tenant_info(self.select_unit))

        # payments

        payments = Node(option_label="Payments")

        # view payment rollforward

        rollforward = Node(option_label="View Payments Rollforward")
        rollforward.add_procedure(lambda: self.payment_rollforward(self.select_tenant))

        # select payment

        select_payment = Node(option_label="View Payments")
        select_payment.add_procedure(lambda: self.store_selected_instance(Payment, select_payment, self.select_tenant))

        # add payment

        add_payment = Node(option_label="Add Payment")
        add_payment.add_procedure(lambda: self.save_payment_info(self.select_tenant))

        # edit payment information
        
        edit_payment = Node(option_label="Update Payment Information")
        edit_payment.add_procedure(lambda: self.update_selected_instance(select_payment))

        # delete payment information
        
        delete_payment = Node(option_label="Delete Payment")
        delete_payment.add_procedure(lambda: self.delete_selected_instance(select_payment))

        # manage tenant

        manage_tenant = Node(option_label="Manage Tenant")

        # edit tenant information
        
        edit_tenant = Node(option_label="Update Tenant Information")
        edit_tenant.add_procedure(lambda: self.update_selected_instance(self.select_tenant))

        # delete tenant record
        
        delete_tenant = Node(option_label="Remove Tenant from Records")
        delete_tenant.add_procedure(lambda: self.delete_selected_instance(self.select_tenant))
        
        # attach nodes to parent elements

        select_payment.add_children([edit_payment, delete_payment, self.to_main, self.exit_app])
        payments.add_children([rollforward, select_payment, add_payment, self.to_main, self.exit_app])
        manage_tenant.add_children([edit_tenant, delete_tenant, self.to_main, self.exit_app])
        self.select_tenant.add_children([payments, manage_tenant, self.to_main, self.exit_app])
        tenants.add_children([self.select_tenant, self.add_tenant, self.to_main, self.exit_app])
        self.main.add_child(tenants)

    # ///////////////////////////////////////////////////////////////
    # SET UP RENTAL UNIT OPERATIONS

    def save_unit_info(self):
        '''
        allows user to create new Unit instance and optionally saves to DB
        '''
        new_unit = self.new_itm_validation(Unit)

        if not new_unit:
            return
        
        unit = Unit(
            acquisition_date=new_unit["acquisition_date"],
            address=new_unit["address"],
            monthly_mortgage=float(new_unit["monthly_mortgage"]),
            monthly_rent=float(new_unit["monthly_rent"]),
            late_fee=float(new_unit["late_fee"]),                
        )
        self.finalize_add(unit)

    def save_tenant_info(self, ref_node=None):
        '''
        allows user to create new Tenant instance and optionally saves to DB

        Parameters
        ---------
        ref_node (optional): Node instance
            - node which stores the reference to the user-selected instance
        '''
        if ref_node:
            if ref_node.data_ref:
                unit = ref_node.data_ref
            else:
                unit, index = pick(Unit.get_all_instances(), "Select Unit")
        else:
            unit = pick(Unit.get_all_instances(), "Select Unit")

        new_tenant = self.new_itm_validation(Tenant, unit)  

        if not new_tenant:
            return

        tenant = Tenant(
            name=new_tenant["name"],
            email_address=new_tenant["email_address"],
            phone_number=new_tenant["phone_number"],
            move_in_date=new_tenant["move_in_date"],
            unit_id=int(new_tenant["unit_id"])             
        )
        self.finalize_add(tenant)

    def save_expense_info(self, ref_node):
        '''
        allows user to create new Expense instance and optionally saves to DB

        Parameters
        ---------
        ref_node: Node instance
            - node which stores the reference to the user-selected instance
        '''
        unit = ref_node.data_ref

        new_expense = self.new_itm_validation(Expense, unit)

        if not new_expense:
            return
        
        expense = Expense(
            descr=new_expense["descr"],
            category=new_expense["category"],
            amount=float(new_expense["amount"]),
            exp_date=new_expense["exp_date"],
            unit_id=int(new_expense["unit_id"]),                
        )
        self.finalize_add(expense)

    def add_unit_ops(self):
        '''
        creates and links nodes related to unit operations

        Procedures
        ---------
        - creates rental node with multiple children nodes
        - adds rental node as a child of the main menu node
        '''
        rentals = Node(option_label="Rental Units")
        unit_transactions = Node(option_label="Transactions for Selected Unit")
        unit_tenants = Node(option_label="Tenants for Selected Unit")

        # select unit

        self.select_unit = Node(option_label="Select Unit")
        self.select_unit.add_procedure(lambda: self.store_selected_instance(Unit, self.select_unit))

        # add unit
        
        add_unit = Node(option_label="Add Unit")
        add_unit.add_procedure(lambda: self.save_unit_info())

        # print summary of transactions

        transaction_summary = Node(option_label="Transaction Summary")
        transaction_summary.add_procedure(lambda: self.print_transaction_summary(self.select_unit))

        # view transaction history

        view_transactions = Node(option_label="Transaction History")
        view_transactions.add_procedure(lambda: self.print_transaction_history(self.select_unit))

        # manage unit
        
        manage_unit = Node(option_label="Manage Unit")

        # edit unit information
        
        edit_unit = Node(option_label="Update Unit Information")
        edit_unit.add_procedure(lambda: self.update_selected_instance(self.select_unit))

        # delete expense information
        
        delete_unit = Node(option_label="Delete Unit Record")
        delete_unit.add_procedure(lambda: self.delete_selected_instance(self.select_unit))

        # edit expense information
        
        select_expense = Node(option_label="View Expenses")
        select_expense.add_procedure(lambda: self.store_selected_instance(Expense, select_expense, self.select_unit))

        # add expense
        
        add_expense = Node(option_label="Add Expense")
        add_expense.add_procedure(lambda: self.save_expense_info(self.select_unit))

        # edit expense information
        
        edit_expense = Node(option_label="Update Expense Information")
        edit_expense.add_procedure(lambda: self.update_selected_instance(select_expense))

        # delete expense information
        
        delete_expense = Node(option_label="Delete Expense")
        delete_expense.add_procedure(lambda: self.delete_selected_instance(select_expense))

        # attach nodes to parent elements

        select_expense.add_children([edit_expense, delete_expense, self.go_back, self.to_main, self.exit_app])
        unit_transactions.add_children([transaction_summary, view_transactions, select_expense, add_expense, self.go_back, self.to_main, self.exit_app])
        unit_tenants.add_children([self.select_tenant, self.add_tenant, self.go_back, self.to_main, self.exit_app])
        manage_unit.add_children([edit_unit, delete_unit, self.go_back, self.to_main, self.exit_app])
        self.select_unit.add_children([unit_transactions, unit_tenants, manage_unit, self.go_back, self.to_main, self.exit_app])
        rentals.add_children([self.select_unit, add_unit, self.to_main, self.exit_app])
        self.main.add_child(rentals)

    # ///////////////////////////////////////////////////////////////
    # SET UP SUMMARY OPERATIONS

    def output_revenue_report(self):
        '''
        generates revenue report and prints to pdf
        '''
        from lib.helper.report import generate_income_report

        df = sql.get_all_transactions()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year

        years = df['Year'].unique()

        year, index = pick(years, "Select Year from options below")
        path = fr"./outputs/Revenue Report for {str(year)}.pdf"

        funcs_to_run = [
            lambda: print("[blue]generating report...\n[/blue]"),
            lambda: generate_income_report(year, path),
            lambda: self.menu.print_output_message(path)
        ]
        self.menu.print_page_header('Revenue Report', f'For the {year} calendar year')
        self.run_func_if_confirm(f'Create pdf revenue report for {year}?', 
                                 funcs_to_run)

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
        income_summary.add_procedure(self.print_transaction_summary)

        # print detailed income information

        income_detailed = Node(option_label="View All Transactions")
        income_detailed.add_procedure(self.print_transaction_history)

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
    rental_mgmt.add_tenant_ops()
    rental_mgmt.add_unit_ops()
    rental_mgmt.add_summary_ops()
    rental_mgmt.main.add_child(rental_mgmt.exit_app)

    menu = rental_mgmt.menu

    menu.display_welcome()

    return menu