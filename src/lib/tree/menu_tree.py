import sys
import types
from pick import pick
from rich import print
from datetime import datetime
import os
import art

# project modules
from lib.helper import ascii

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
    - print_output_message: prints message with file location when user prints data to a csv file
    - print_continue_message: prints message with blank input to freeze page before going to next menu
    - print_directions: prints directions on page in a specific format
    - print_cancellation_directions: prints note indicating how to cancel out of current menu
    - print page header: prints page header and subheader in specific format
    - exit_app: prints goodbye message and exits out of the application
    - to_main: returns user to main menu
    '''
    def __init__(self, node):
        '''
        Constructs the necessary attributes for the MenuTree object.

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
        os.system('cls' if os.name == 'nt' else 'clear')
        print(art.text2art("Rental", font='tarty7'))
        print(art.text2art("Management", font='tarty7'))
        print("[blue]--------------------------------------------------------------------[/blue]")
        print("[bold cyan]MANAGE RENTAL UNITS, TENANT INFORMATION, AND RELATED PAYMENTS AND EXPENSES[/bold cyan]")
        print(ascii.buildings("white"))
        print(f"[yellow]{art.text2art('press any key to continue', font='tiny2')}[/yellow]")
        input("")

    def invalid_option(self):
        '''
        prints error message when user tries to enter an invalid
        '''
        print("[red]ERROR: Input not valid. Please try again using the format specified above.[/red]")

    def print_output_message(self, filename):
        '''
        prints message with file location when user prints data to a csv file

        Parameters
        ---------
        filename: str
            - file path where the data should be saved
        '''
        print(f"Output saved to: [bold green]{filename}[/bold green]")
        self.print_continue_message()

    def print_continue_message(self):
        '''
        prints message with blank input to freeze page before going to next menu
        '''
        print(f"[yellow]{art.text2art('press any key to continue', font='tiny2')}[/yellow]")
        input("")

    def print_directions(self, directions):
        '''
        prints directions on page in a specific format
        '''
        print(f"[cyan]{directions}[/cyan]")

    def print_cancellation_directions(self):
        '''
        prints note indicating how to cancel out of current menu
        '''
        self.print_directions('Enter `e` or `exit` to cancel')

    def print_page_header(self, header, subheader=False):
        '''
        prints page header and subheader in specific format
        '''
        print(art.text2art(f"{header}", font='tarty4'))
        print("")
        print(f"[yellow]{subheader}[/yellow]")
        print("")

    # ///////////////////////////////////////////////////////////////
    # CLI NAVIGATION

    def exit_app(self):
        '''
        prints goodbye message and exits out of the application
        '''
        print(art.text2art("Goodbye!", font='tarty7'))
        print("")
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

class Node:
    '''
    A class to create and manage nodes on a menu tree for rental management application

    Attributes
    ---------
    root: Node instance
        - Root node of the tree instance
    option_label: str
        - label when node is displayed as a menu option
    title_label: str
        - title after node is selected from menu options
    menu_tree: MenuTree instance
        - menu tree that current instance is connected to
    parent: Node instance
        - parent of current instance
    children: list
        - list of child Node instances
    procedure: callable object
        - function to run when instance is selected from menu
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
        '''
        Constructs the necessary attributes for the Node object.

        Parameters
        ---------
        option_label: str
            - label when node is displayed as a menu option
        title_label (optional): str
            - title after node is selected from menu options
        '''
        self.option_label = option_label
        self.title_label = option_label if title_label is None else title_label
        self.menu_tree = None
        self.parent = None
        self.children = []
        self.procedure = None
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
        os.system('cls' if os.name == 'nt' else 'clear')
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