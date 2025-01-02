# Rental Management Tool

## About this project

The **Rental Management Tool** is a command-line application designed to help landlords efficiently manage rental property data. It allows for easy tracking of tenants, payments, expenses, and generates detailed yearly income reports.

## Contributors

**Jacqueline Trapp**  
GitHub: [JTrapp18](https://github.com/jtrapp18)

## Features

- **Manage Rental Information**: Add, view, update, and delete rental units, tenants, expenses, and payment records.
- **Receipt Generation**: Automatically generates and prints receipts for payments linked to specific tenants.
- **Payment History & Rollforward**: Provides a monthly rollforward showing amounts due for each tenant, including a full payment history.
- **Income Reporting**: Generates and prints a PDF income report summarizing both aggregate results and individual unit performance for a specified year.

## Technical

- **Hierarchical Menu System**: Implements a tree structure using `Node` instances to provide dynamic, multi-level menu navigation with parent-child relationships.
- **Customizable Actions**: Each `Node` can trigger user-defined procedures, allowing for dynamic operations like filtering tenants or viewing payment details.
- **Dynamic Menu Navigation**: Built with `MenuTree` and `Node` classes, enabling an expandable, user-friendly navigation structure.
- **CLI Interface with Custom ASCII Art**: A command-line interface enhanced with rich text formatting and custom ASCII art for improved user experience.
- **Modular and Extendable**: Easily extend the menu system to support future features and operations like tenant or payment management.
- **Procedural Chaining**: Seamlessly chain multiple actions (e.g., saving data and generating receipts) for greater flexibility in workflows.
- **Database Integration & CRUD Operations**: Manages database interactions for creating, reading, updating, and deleting records, with SQL (SQLite or chosen database).
- **Data Binding**: Menu `Node` instances bind dynamically to data, such as tenants or payments, enabling users to view and edit records interactively.
- **Input Validation**: Ensures that only valid data is entered into the system with custom validation functions for all key attributes (e.g., description, payment amounts).
- **SQL Helper Functions**: SQL functions abstracted for simplified database interactions, making it easier to execute CRUD operations.
- **Well-Organized Codebase**: The project is structured with clear separation of concerns, including dedicated modules for database models, helpers, and menu navigation.

## Demo

See this gif for an example of how the app works.

![demo](img/demo-gif.gif)

## Setup

1. Fork and clone this repo to your local machine.
2. Run `pipenv install` to install dependencies.
3. Run `pipenv shell` to activate the virtual environment.
4. Run `pipenv run start` to launch the application in the CLI.

## Description of Key Directories and Files

- **`src/lib/database/`**: Contains models and CRUD operations for `Expense`, `Payment`, `Tenant`, and `Unit` data.
  
- **`src/lib/helper/`**: Utility files for:
  - **`ascii.py`**: Functions for displaying ASCII art and formatted text.
  - **`report.py`**: Functions for generating PDF income reports based on stored data.
  - **`sql_helper.py`**: Helper functions that simplify database queries and operations.
  - **`validation.py`**: Custom validation functions to ensure data integrity (e.g., valid payment amounts, description lengths).

- **`src/lib/tree/`**: Menu and navigation components:
  - **`menu_tree.py`**: Defines the menu structure, with options and navigation.
  - **`populate_menu.py`**: Manages the population of menu options and linking actions to user interactions.

- **`_1_seeds.py`**: Used for seeding the database with initial test data.
- **`_2_cli.py`**: The entry point for the CLI interface, where users interact with the application.
- **`outputs/`**: Stores generated output files like reports and receipts.
- **`img/`**: Contains image assets used in the application.
- **`Pipfile`**: Defines project dependencies and virtual environment setup.