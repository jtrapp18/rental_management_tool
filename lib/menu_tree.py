import sys
import types
from pick import pick
from rich import print
from datetime import datetime

class MenuTree:
    '''
    A class to create and manage a menu tree for rental management application

    Attributes
    ---------
    root: Node instance
        - Root node of the tree instance

    Methods
    ---------
    - display_welcome: prints welcome message when user opens the application
    - invalid_option: prints error message when user tries to enter an invalid
    - print_message: prints message with file location when user prints data to a csv file
    - exit_app: prints goodbye message and exits out of the application
    - to_main: returns user to main menu
    - show_user_selections: displays user selections for adding or updating an instance
    - new_itm_validation: creates and validates new object to be used to create a new instance
    - update_itm_validation: updates an existing instance after validating user's desired changes
    - print_to_csv: prints data to csv file
    '''
    def __init__(self, node):
        '''
        Constructs the necessary attributes for the Node object.

        Parameters
        ---------
        node: Node instance
            - Node to be used for the root of the tree instance
        '''
        self.root = node
        node.menu_tree = self

    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS

    @property
    def node(self):
        return self._node
    
    @node.setter
    def node(self, node):
        if isinstance(node, Node):
            self._node = node
        else:
            raise ValueError("Node must be an instance of the Node class")
        
    # ///////////////////////////////////////////////////////////////
    # CLI PRINT MESSAGES
        
    def display_welcome(self):
        '''
        prints welcome message when user opens the application
        '''
        print("[magenta]Hello! Welcome to [/magenta][bold cyan] My App![/bold cyan]")

    def invalid_option(self):
        '''
        prints error message when user tries to enter an invalid
        '''
        print("[red]ERROR: Input not valid. Please try again.[/red]")

    def print_message(self, filename):
        '''
        prints message with file location when user prints data to a csv file

        Parameters
        ---------
        filename: str
            - file path where the data should be saved
        '''
        print(f"[pink]Output data to: {filename}[/pink]")

    # ///////////////////////////////////////////////////////////////
    # CLI NAVIGATION

    def exit_app(self):
        '''
        prints goodbye message and exits out of the application
        '''
        print("[cyan]Goodbye![/cyan]")
        sys.exit()

    def to_main(self):
        '''
        returns user to main menu

        Returns
        ---------
        self.root: Node instance
            - Root node of the tree instance
        '''
        return self.root

    # ///////////////////////////////////////////////////////////////
    # CLI FUNCTIONALITY
    
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

        if user_input == 'exit' or 'e':
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
        '''
        print(df)
              
        confirm = input(f"Print output to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/{report_type}_AS_OF_{date_today}_FOR_{report_for}.csv"
            df.to_csv(path, index=False)

            self.print_message(path)

class Node:
    '''
    A class to create and manage a menu tree for rental management application

    Attributes
    ---------
    root: Node instance
        - Root node of the tree instance
    option_label: str
        -
    title_label
        -option_label if title_label is None else title_label
    menu_tree: MenuTree instance
    parent: Node instance
    children: list
    procedure: dict

    last_input: 
    data_ref: class instance


    Methods
    ---------
    - add_procedure: validates and adds dictionary with procedure information to instance
    - validate_child: validates child node before adding to list of children
    - add_child: adds child node to list of children
    - add_children: adds multiple children to instance
    - show_menu: navigates to next menu based on user selection
    - run_procedure: runs procedure stored in instance
    '''
    last_node = None

    def __init__(self, option_label, title_label=None):
        self.option_label = option_label
        self.title_label = option_label if title_label is None else title_label
        self.menu_tree = None
        self.parent = None
        self.children = []

        self.procedure = None
        self.last_input = None
        self.data_ref = None # used to store references to objects or instances for ease of reference in app

    def __repr__(self):
        return (
            f"<Node: {self.option_label}>"
        )
    
    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS
    
    @property
    def option_label(self):
        return self._option_label
    
    @option_label.setter
    def option_label(self, option_label):
        if isinstance(option_label, str) and len(option_label) > 0:
            self._option_label = option_label
        else:
            raise ValueError("option_label must be a string greater than 0 characters")
        
    @property
    def title_label(self):
        return self._title_label
    
    @title_label.setter
    def title_label(self, title_label):
        if isinstance(title_label, str) and len(title_label) > 0:
            self._title_label = title_label
        else:
            raise ValueError("title_label must be a string greater than 0 characters")

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        if parent is None or isinstance(parent, Node):
            self._parent = parent
        else:
            raise ValueError("Parent must be an instance of the Node class")
        
    @property
    def menu_tree(self):
        return self._menu_tree
    
    @menu_tree.setter
    def menu_tree(self, menu_tree):
        if menu_tree is None or isinstance(menu_tree, MenuTree):
            self._menu_tree = menu_tree
        else:
            raise ValueError("Menu tree must be an instance of the MenuTree class")
           
    @property
    def children(self):
        return self._children
    
    @children.setter
    def children(self, children):
        if isinstance(children, list):
            for child in children:
                self.validate_child(child)
            self._children = children
        else:
            raise ValueError("Children must be of type list with all values from the Node class")
        
    # ///////////////////////////////////////////////////////////////
    # MANAGEMENT OF NODE RELATIONSHIPS
        
    def add_procedure(self, procedure):
        '''
        validates and procedure to instance

        Parameters
        ---------
        procedure: callable object
            - function to be run when node is activated

        Procedures
        ---------
        - stores specified procedure in instance
        '''
        if callable(procedure):
            _procedure = procedure
        else:
            raise ValueError("Function parameter must be a function")

        self.procedure = _procedure

    def validate_child(self, node):
        '''
        validates child node before adding to list of children

        Parameters
        ---------
        node: Node instance
            - node to be added as a child of instance

        Returns
        ---------
        True
            - returns only if validation passes, else value error is raised        
        '''
        if isinstance(node, Node):
            return True
        else:
            raise ValueError("Child must be an instance of the Node class")        

    def add_child(self, node):
        '''
        adds child node to list of children

        Parameters
        ---------
        node: Node instance
            - node to be added as a child of instance
        '''
        if self.validate_child(node):
            node.parent = self
            node.menu_tree = self.menu_tree
            self.children.append(node)
        
    def add_children(self, nodes):
        '''
        adds multiple children to instance

        Parameters
        ---------
        nodes: list
            - list of Node instances to be added as children of instance
        '''
        for node in nodes:
            self.add_child(node)

    # ///////////////////////////////////////////////////////////////
    # CLI FUNCTIONALITY

    def show_menu(self):
        '''
        navigates to next menu based on user selection

        Returns
        ---------
        self.children[index]: Node instance
            - Node to display in the application after user selection
        '''
        Node.last_node = self
        user_selection, index = pick([child.option_label for child in self.children], self.title_label)

        return self.children[index]
    
    def run_procedure(self):
        '''
        runs procedure stored in instance

        Returns
        ---------
        Node instance
            - Node to display in the application after procedure runs

        '''
        default_next = self if len(self.children) > 0 else self.parent
        next_node = self.procedure()

        return next_node if next_node else default_next