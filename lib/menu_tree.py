import sys
import types
from pick import pick
from rich import print
from datetime import datetime

# ///////////////////////////////////////////////////////////////
# MENU DISPLAYS

class MenuTree:
    '''
    A class to...

    Attributes
    ---------
    node: object
        - Node ...
        - 

    Methods
    ---------
    display_welcome: describe this...

    
    '''
    def __init__(self, node):
        '''
        Constructs the necessary attributes for the Node object.

        Parameters
        ---------
        node: object
            describe...

        '''
        self.root = node
        node.menu_tree = self

    @property
    def node(self):
        return self._node
    
    @node.setter
    def node(self, node):
        if isinstance(node, Node):
            self._node = node
        else:
            raise ValueError("Node must be an instance of the Node class")
        
    def display_welcome(self):
        print("[magenta]Hello! Welcome to [/magenta][bold cyan] My App![/bold cyan]")

    def display_goodbye(self):
        print("[cyan]Goodbye![/cyan]")

    def invalid_option(self):
        print("[red]ERROR: Input not valid. Please try again.[/red]")

    def print_message(self, filename):
        print(f"[pink]Output data to: {filename}[/pink]")

    def exit_app(self):
        self.display_goodbye()
        sys.exit()

    def to_main(self):
        return self.root
    
    def user_selection(self, constraints, key):
        if isinstance(constraints, list):
            user_input, index = pick(constraints, f"Select {key} from the following options")
        else:
            user_input = input(f"Enter {key} ({constraints}): ")
        return user_input
    
    def new_itm_validation(self, val_dict):
        '''
        describe...

        Parameters
        ---------

        Procedures
        ---------
        - describe

        Returns
        ---------
                     
        
        '''
        new_obj = {}
        
        for key, val_func in val_dict.items():
            constraints = val_func.constraints
            user_input = self.user_selection(constraints, key)

            while True:
                try:
                    user_input = float(user_input) if key=="amount" else user_input
                    value = val_func(user_input)
                    new_obj[key] = value

                    break
                except:
                    self.invalid_option()
                    user_input = self.user_selection(constraints, key)

        return new_obj

    def update_itm(self, inst, val_dict):
        '''
        describe...

        Parameters
        ---------

        Procedures
        ---------
        - describe

        Returns
        ---------
                     
        
        '''
        
        attributes = [f"{key}: {getattr(inst, key, None)}" for key in val_dict]
        itm_to_update, index = pick(attributes+['SUBMIT CHANGES'], "Choose item to update")

        if itm_to_update == 'SUBMIT CHANGES':
            return
        
        key = itm_to_update.split(":")[0].strip()
        val_func = val_dict[key]
        constraints = val_func.constraints
        user_input = self.user_selection(constraints, key)

        while True:
            try:
                user_input = float(user_input) if key=="amount" else user_input
                value = val_func(user_input)
                setattr(inst, key, value)

                break
            except:
                self.invalid_option()
                user_input = self.user_selection(constraints, key)

        self.update_itm(inst, val_dict)
    
    def print_to_csv(self, df, report_type, report_for):
        print(df)
              
        confirm = input(f"Print output to CSV? (Y/N)")
        
        if confirm == "Y":
            date_today = datetime.now().strftime('%Y-%m-%d')
            path = f"./outputs/{report_type}_AS_OF_{date_today}_FOR_{report_for}.csv"
            df.to_csv(path, index=False)

            self.print_message(path)

class Node:
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
        
    def add_procedure(self, prompt, func, input_req=False):
        # validate inputs
        if isinstance(prompt, str) and len(prompt) > 0:
            _prompt = prompt
        else:
            raise ValueError("Prompt must be a string greater than 0 characters")
        if callable(func):
            _func = func
        else:
            raise ValueError("Function parameter must be a function")
        if isinstance(input_req, bool):
            _input_req = input_req
        else:
            raise ValueError("Input required must be either True or False")
        
        self.procedure = {
            "prompt": _prompt,
            "func": _func,
            "input_req": _input_req
        }

    def validate_child(self, node):
        if isinstance(node, Node):
            return True
        else:
            raise ValueError("Child must be an instance of the Node class")        

    def add_child(self, node):
        if self.validate_child(node):
            node.parent = self
            node.menu_tree = self.menu_tree
            self.children.append(node)
        
    def add_children(self, nodes):
        for node in nodes:
            self.add_child(node)

    def show_menu(self, prompt="Enter id from menu options above"):
        Node.last_node = self

        user_selection, index = pick([child.option_label for child in self.children], self.title_label)
        return self.children[index]
    
    def run_procedure(self):
        prompt, func, input_req  = self.procedure.values()

        print(prompt)

        if input_req:
            try:
                user_selection = int(input(f"select an option"))
                self.last_input = user_selection

                next_node = func(user_selection)
                return next_node if next_node else self
            except:
                self.menu_tree.invalid_option()
                return self
        else:
            default_next = self if len(self.children) > 0 else self.parent
            next_node = func()

            return next_node if next_node else default_next
        
    def go_back(self):
        return Node.last_node.parent
    
    