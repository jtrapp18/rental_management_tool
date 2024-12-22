from _2_populate_menu import populate_menu

if __name__ == "__main__":
    menu = populate_menu() # populate tree to create feedback loop

    node = menu.root # set initial node to root
    while True:
        if node.procedure:
            node = node.run_procedure() # invoke callback function if user is at the end of the menu tree
        
        if len(node.children) > 0:
            node = node.show_menu() # show next menu if the user is not at the end of the menu tree