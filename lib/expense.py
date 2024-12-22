from __init__ import CURSOR, CONN
from unit import Unit
import validation as val
import sql_helper as sql
import pandas as pd

class Expense:

    DF_COLUMNS = ("id", "Description", "Amount", "Date", "Unit ID")

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, descr, amount, exp_date, unit_id, id=None):
        self.id = id
        self.descr = descr
        self.amount = amount
        self.exp_date = exp_date
        self.unit_id = unit_id

    def __repr__(self):
        return (
            f"<expense {self.id}: {self.descr}, {self.amount}, {self.exp_date}, "
            + f"Unit: {self.unit_id}>"
        )
    
    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS

    @property
    def descr(self):
        return self._descr

    @descr.setter
    def descr(self, descr):

        self._descr = val.name_validation(descr)

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
    def create(cls, descr, amount, exp_date, unit_id):
        """ Initialize a new Expense instance and save the object to the database. Return the new instance. """
        expense = cls(descr, amount, exp_date, unit_id)
        expense.save()
        return expense
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Expense instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        expense = cls.all.get(row[0])

        id = row[0]
        descr = row[1]
        amount = row[2]
        exp_date = row[3]
        unit_id = row[4]
        
        if expense:
            # ensure attributes match row values in case local object was modified
            expense.descr = descr
            expense.amount = amount
            expense.exp_date = exp_date
            expense.unit_id = unit_id
        else:
            # not in dictionary, create new instance and add to dictionary
            expense = cls(descr, amount, exp_date, unit_id, id) # reordering due to optional values
            cls.all[expense.id] = expense
        return expense
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists expense instances """
        sql.drop_table(CURSOR, CONN, "expenses")
   
    @classmethod
    def find_by_id(cls, id):
        """Return Expense object corresponding to the table row matching the specified primary key"""
        return sql.find_by_id(cls, CURSOR, "expenses", id)

    def delete(self):
        """Delete the table row corresponding to the current Expense instance,
        delete the dictionary entry, and reassign id attribute"""

        sql.delete(CURSOR, CONN, "expenses", self.id)

    @classmethod
    def get_all_instances(cls):
        """Return a list containing one Expense instance per table row"""
        return sql.get_all_instances(cls, CURSOR, "expenses")
    
    @classmethod
    def get_dataframe(cls):
        """Return a list containing one Expense instance per table row"""
        return sql.get_dataframe(cls, CURSOR, "expenses")

    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Expense instances """
        sql = """
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            descr TEXT,
            amount FLOAT,
            exp_date DATE,
            unit_id INTEGER,
            FOREIGN KEY (unit_id) REFERENCES Unit(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the values of the current expense object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO expenses (descr, amount, exp_date, unit_id)
            VALUES (?, ?, ?, ?)
        """

        CURSOR.execute(sql, (self.descr, self.amount, 
                             self.exp_date, self.unit_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE expenses
            SET descr = ?, amount = ?, exp_date = ?, unit_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.descr, self.amount, 
                             self.exp_date, self.unit_id, 
                             self.id))
        CONN.commit()

    @classmethod
    def expense_summary(cls):
        df = cls.get_dataframe()

        return df