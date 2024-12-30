# lib/department.py
from __init__ import CURSOR, CONN
import sql_helper as sql
import validation as val
import pandas as pd

class Unit:

    DF_COLUMNS = ("id", "Acquisition Date", "Address", "Monthly Mortgage", "Monthly Rent", "Late Fee")

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, acquisition_date, address, monthly_mortgage, monthly_rent, late_fee=150, id=None):
        self.id = id
        self.acquisition_date = acquisition_date
        self.address = address
        self.monthly_mortgage = monthly_mortgage
        self.monthly_rent = monthly_rent
        self.late_fee = late_fee

    def __repr__(self):
        address_parsed = self.address.replace("\n", ", ")
        return (
            f"<Unit {self.id}: {address_parsed} | " +
            f"Acquired on: {self.acquisition_date} | " +
            f"Monthly Mortgage: {self.monthly_mortgage} | " +
            f"Monthly Rent: {self.monthly_rent} | " +
            f"Late Fee: {self.late_fee}>"
        )

    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS

    @property
    def acquisition_date(self):
        return self._acquisition_date

    @acquisition_date.setter
    def acquisition_date(self, acquisition_date):
        self._acquisition_date = val.date_validation(acquisition_date)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = val.address_validation(address)

    @property
    def monthly_mortgage(self):
        return self._monthly_mortgage

    @monthly_mortgage.setter
    def monthly_mortgage(self, monthly_mortgage):
        self._monthly_mortgage = val.dollar_amt_validation(monthly_mortgage)

    @property
    def monthly_rent(self):
        return self._monthly_rent

    @monthly_rent.setter
    def monthly_rent(self, monthly_rent):
        self._monthly_rent = val.dollar_amt_validation(monthly_rent)

    @property
    def late_fee(self):
        return self._late_fee

    @late_fee.setter
    def late_fee(self, late_fee):
        self._late_fee = val.dollar_amt_validation(late_fee)

    # ///////////////////////////////////////////////////////////////
    # MANAGE CLASS INSTANCES

    @classmethod
    def create(cls, acquisition_date, address, monthly_mortgage, monthly_rent, late_fee):
        """ Initialize a new Department instance and save the object to the database """
        unit = cls(acquisition_date, address, monthly_mortgage, monthly_rent, late_fee)
        unit.save()
        return unit
    
    @classmethod
    def instance_from_db(cls, row):
        """Return a Unit object having the attribute values from the table row."""

        # Check the dictionary for an existing instance using the row's primary key
        unit = cls.all.get(row[0])

        id = row[0]
        acquisition_date = row[1]
        address = row[2]
        monthly_mortgage = row[3]
        monthly_rent = row[4]
        late_fee = row[5]
        
        if unit:
            # ensure attributes match row values in case local instance was modified
            unit.acquisition_date = acquisition_date
            unit.address = address
            unit.monthly_mortgage = monthly_mortgage
            unit.monthly_rent = monthly_rent
            unit.late_fee = late_fee
        else:
            # not in dictionary, create new instance and add to dictionary
            unit = cls(acquisition_date, address, monthly_mortgage, monthly_rent, late_fee, id)
            cls.all[unit.id] = unit
        return unit
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Unit instances """
        sql.drop_table("units")

    @classmethod
    def find_by_id(cls, id):
        """Return a Unit object corresponding to the table row matching the specified primary key"""
        return sql.find_by_id(cls, "units", id)

    def delete(self):
        """Delete the table row corresponding to the current Unit instance,
        delete the dictionary entry, and reassign id attribute"""

        sql.delete(self, "units")

    @classmethod
    def get_all_instances(cls):
        """Return a list containing one Unit instance per table row"""
        return sql.get_all_instances(cls, "units")

    @classmethod
    def get_dataframe(cls):
        """Return a list containing one Unit instance per table row"""
        return sql.get_dataframe(cls, "units")
    
    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY,
            acquisition_date DATE,
            address TEXT,
            monthly_mortgage NUMERIC,
            monthly_rent NUMERIC,
            late_fee NUMERIC)
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the values of the current Unit object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO units (acquisition_date, address, monthly_mortgage, monthly_rent, late_fee)
            VALUES (?, ?, ?, ?, ?)
        """

        CURSOR.execute(sql, (self.acquisition_date, self.address, self._monthly_mortgage, self.monthly_rent, 
                             self.late_fee))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET acquisition_date = ?, address = ?, monthly_mortgage = ?, 
            monthly_rent = ?, late_fee = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.acquisition_date, self.address, self.monthly_mortgage, 
                             self.monthly_rent, self.late_fee, self.id))
        CONN.commit()

    
    # ///////////////////////////////////////////////////////////////
    # LOOKUPS FROM LINKED TABLES

    def tenants(self):
        """Return list of tenants associated with current unit"""
        from tenant import Tenant
        sql = """
            SELECT * FROM tenants
            WHERE unit_id = ?
        """
        CURSOR.execute(sql, (self.id,),)

        rows = CURSOR.fetchall()

        return pd.DataFrame(rows, columns=Tenant.DF_COLUMNS)

    def expenses(self):
        """Return list of expenses associated with current unit"""
        from expense import Expense
        sql = """
            SELECT * FROM expenses
            WHERE unit_id = ?
        """
        CURSOR.execute(sql, (self.id,),)

        rows = CURSOR.fetchall()

        return pd.DataFrame(rows, columns=Expense.DF_COLUMNS)
    
    def transactions(self):
        """Return list of transactions associated with current unit"""

        return sql.get_all_transactions(self.id)