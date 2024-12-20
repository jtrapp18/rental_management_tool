import sys

from rich import print
from unit import Unit
from tenant import Tenant
from payment import Payment

# ///////////////////////////////////////////////////////////////
# MENU DISPLAYS

def display_welcome():
    print("[magenta]Hello! Welcome to [/magenta][bold cyan] My App![/bold cyan]")

def formatted_menu(menu_dict):
    title = menu_dict["title"]
    options = menu_dict["options"]

    print(f"[bold]{title}[/bold]")

    for i, option in enumerate(options):
        print(f"[i]{i}. {option["label"]}[/i]")

def display_goodbye():
    print("[cyan]Thanks for using Pet Minder! Goodbye![/cyan]")

def exit_app():
    display_goodbye()
    sys.exit()

# ///////////////////////////////////////////////////////////////
# UNIT OPERATIONS
def view_unit_information(unit):
    print(f"This does something for {unit}")

# ///////////////////////////////////////////////////////////////
# TENANT OPERATIONS

# ///////////////////////////////////////////////////////////////
# PAYMENT OPERATIONS