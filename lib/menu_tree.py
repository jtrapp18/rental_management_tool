import sys
import types
from pick import pick
from rich import print

# ///////////////////////////////////////////////////////////////
# MENU DISPLAYS

class MenuTree:
    def __init__(self, node):
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
    
    def new_itm_validation(self, val_dict):
        new_obj = {}

        def user_selection(constraints, key):
            if isinstance(constraints, list):
                user_input, index = pick(constraints, f"Select {key} from the following options")
            else:
                user_input = input(f"Enter {key} ({constraints})")
            return user_input
        
        for key, val_func in val_dict.items():
            constraints = val_func.constraints
            user_input = user_selection(constraints, key)

            while True:
                try:
                    user_input = float(user_input) if key=="amount" else user_input
                    value = val_func(user_input)
                    new_obj[key] = value

                    break
                except:
                    self.invalid_option()
                    user_input = user_selection(constraints, key)

        return new_obj

class Node:
    last_node = None

    def __init__(self, label):
        self.label = label
        self.menu_tree = None
        self.parent = None
        self.children = []

        self.procedure = None
        self.last_input = None
        self.data_ref = None # used to store references to objects or instances for ease of reference in app

    def __repr__(self):
        return (
            f"<Node: {self.label}>"
        )

    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, label):
        if isinstance(label, str) and len(label) > 0:
            self._label = label
        else:
            raise ValueError("Label must be a string greater than 0 characters")

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

        print(f"[bold][yellow]{self.label}[/yellow][/bold]")

        for i, child in enumerate(self.children, start=1):
            print(f"[i]{i}. {child.label}[/i]")
        try:
            return self.children[int(input(prompt))-1]
        except:
            self.menu_tree.invalid_option()
            return self
    
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
    
    