from __init__ import CURSOR, CONN
from unit import Unit
import validation as val
import sql_helper as sql
import pandas as pd

class Expense:
    '''
    A class to create and manage expenses in DB

    Constants
    ---------
    DF_COLUMNS: tuple
        - columns to be used for Expense dataframes
    VALIDATION_DICT: dict
        - dictionary containing validation functions to apply when user makes DB edits

    Class Attributes
    ---------
    all: dict
        - dictionary of objects saved to the database

    Instance Attributes
    ---------
    id: int
        - unique identifier for instance
    descr: str
        - description of expense
    category: str
        - expense category
    amount: float
        - dollar value of expense
    exp_date: str
        - date expense was incurred
    unit_id: int
        - id of parent unit

    Instance Methods
    ---------
    - delete: delete the table row corresponding to the current instance
    - save: insert a new row with the values of the current object
    - update: update the table row corresponding to the current instance

    Class Methods
    ---------
    - create: initialize a new instance and save the object to the database
    - instance_from_db: return instance having the attribute values from the table row
    - drop_table: drop the table that persists instances
    - find_by_id: return object corresponding to the table row matching the specified primary key
    - get_all_instances: return a list containing one instance per table row
    - get_dataframe: return a Pandas DataFrame containing information from table
    - create_table: create a new table to persist the attributes of all instances
    '''
    DF_COLUMNS = ("id", "Description", "Category", "Amount", "Date", "Unit")
    VALIDATION_DICT = {
        "descr": val.descr_validation,
        "category": val.exp_category_validation,
        "amount": val.dollar_amt_validation,
        "exp_date": val.date_validation
        }

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, descr, category, amount, exp_date, unit_id, id=None):
        '''
        Constructs the necessary attributes for the Expense object.

        Parameters
        ---------
        descr: str
            - description of expense
        category: str
            - expense category
        amount: float
            - dollar value of expense
        exp_date: str
            - date expense was incurred
        unit_id: int
            - id of parent unit
        id: int
            - unique identifier for instance
        '''
        self.id = id
        self.descr = descr
        self.category = category
        self.amount = amount
        self.exp_date = exp_date
        self.unit_id = unit_id

    def __repr__(self):
        return (
            f"<expense {self.id}: {self.descr}, {self.category}, {self.amount}, {self.exp_date}, "
            + f"Unit: {self.unit_id}>"
        )
    
    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS

    @property
    def descr(self):
        return self._descr

    @descr.setter
    def descr(self, descr):
        self._descr = val.descr_validation(descr)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = val.exp_category_validation(category)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        self._amount = val.dollar_amt_validation(amount)
        
    @property
    def exp_date(self):
        return self._exp_date

    @exp_date.setter
    def exp_date(self, exp_date):
        self._exp_date = val.date_validation(exp_date)

    @property
    def unit_id(self):
        return self._unit_id

    @unit_id.setter
    def unit_id(self, unit_id):
        self._unit_id = val.parent_id_validation(unit_id, Unit)
        
    # ///////////////////////////////////////////////////////////////
    # MANAGE CLASS INSTANCES

    @classmethod
    def create(cls, descr, category, amount, exp_date, unit_id):
        '''
        initialize a new instance and save the object to the database
        '''
        expense = cls(descr, category, amount, exp_date, unit_id)
        expense.save()
        return expense
   
    @classmethod
    def instance_from_db(cls, row):
        '''
        return instance having the attribute values from the table row
        '''
        # Check the dictionary for  existing instance using the row's primary key
        expense = cls.all.get(row[0])

        id = row[0]
        descr = row[1]
        category = row[2]
        amount = row[3]
        exp_date = row[4]
        unit_id = row[5]
        
        if expense:
            # ensure attributes match row values in case local object was modified
            expense.descr = descr
            expense.category = category
            expense.amount = amount
            expense.exp_date = exp_date
            expense.unit_id = unit_id
        else:
            # not in dictionary, create new instance and add to dictionary
            expense = cls(descr, category, amount, exp_date, unit_id, id) # reordering due to optional values
            cls.all[expense.id] = expense
        return expense
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        '''
        drop the table that persists instances
        '''
        sql.drop_table("expenses")
   
    @classmethod
    def find_by_id(cls, id):
        '''
        return object corresponding to the table row matching the specified primary key
        '''
        return sql.find_by_id(cls, "expenses", id)

    def delete(self):
        '''
        delete the table row corresponding to the current instance
        '''
        sql.delete(self, "expenses")

    @classmethod
    def get_all_instances(cls):
        '''
        return a list containing one instance per table row
        '''
        return sql.get_all(cls, "expenses", output_as_instances=True)
    
    @classmethod
    def get_dataframe(cls):
        '''
        return a Pandas DataFrame containing information from table
        '''
        return sql.get_all(cls, "expenses", output_as_instances=False)

    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        '''
        create a new table to persist the attributes of all instances
        '''
        sql = """
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            descr TEXT,
            category TEXT,
            amount FLOAT,
            exp_date DATE,
            unit_id INTEGER,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE)
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        '''
        insert a new row with the values of the current object
        '''
        sql = """
            INSERT INTO expenses (descr, category, amount, exp_date, unit_id)
            VALUES (?, ?, ?, ?, ?)
        """

        CURSOR.execute(sql, (self.descr, self.category, self.amount, 
                             self.exp_date, self.unit_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        '''
        update the table row corresponding to the current instance
        '''
        sql = """
            UPDATE expenses
            SET descr = ?, category = ?, amount = ?, exp_date = ?, unit_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.descr, self.category, self.amount, 
                             self.exp_date, self.unit_id, self.id))
        CONN.commit()