from _2_populate_menu import my_menu_tree

if __name__ == "__main__":
    menu = my_menu_tree() # create feedback loop by populating tree
    menu.display_welcome()

    node = menu.root # set initial node to root
    while True:
        if node.procedure:
            set_node = node.run_procedure() # invoke callback function if user is at the end of the menu tree
        
        if len(node.children) > 0:
            set_node = node.show_menu() # show next menu if the user is not at the end of the menu tree
        
        node = set_node # update node based on user interaction