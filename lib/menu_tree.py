import sys
import types

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
        print("[cyan]Thanks for using Pet Minder! Goodbye![/cyan]")

    def invalid_option(self):
        print("[red]Error: selected option not available. Please try again[/red]")

    def exit_app(self):
        self.display_goodbye()
        sys.exit()

    def to_main(self):
        return self.root

class Node:
    def __init__(self, label):
        self.label = label
        self.menu_tree = None
        self.parent = None
        self.children = []

        self.procedure = None

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
        
    def add_procedure(self, prompt, func, input_req=False, lowerBound=None, upperBound=None):
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

            if input_req == True: # lower and upper bounds are only used when user input is required
                if isinstance(lowerBound, int) and lowerBound > 0:
                    _lowerBound = lowerBound
                else:
                    raise ValueError("Lower bound must be an integer > 0")
                if isinstance(upperBound, int) and upperBound > lowerBound:
                    _upperBound = upperBound
                else:
                    raise ValueError("Upper bound must be an integer > lower bound")
            else:
                _lowerBound = None
                _upperBound = None
        else:
            raise ValueError("Input required must be either True or False")
        
        self.procedure = {
            "prompt": _prompt,
            "func": _func,
            "input_req": _input_req,
            "lowerBound": _lowerBound,
            "upperBound": _upperBound
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

    def show_menu(self, prompt="What is your command?"):
        print(f"[bold]{self.label}[/bold]")

        for i, child in enumerate(self.children, start=1):
            print(f"[i]{i}. {child.label}[/i]")
        try:
            return self.children[int(input(prompt))-1]
        except:
            self.menu_tree.invalid_option()

            return self
    
    def run_procedure(self):
        prompt, func, input_req, lowerBound, upperBound  = self.procedure.values()

        print(prompt)

        if input_req:
            user_selection = int(input(f"select an option between {lowerBound} and {upperBound}"))
            if (lowerBound <= user_selection <= upperBound):
                next_mode = func(user_selection)
                return next_mode if next_mode else self.parent
            else:
                raise ValueError(f"Value must be an integer between {lowerBound} and {upperBound}")
        else:
            next_mode = func()
            return next_mode if next_mode else self.parent
        
    def go_back(self):
        return self.parent