# lib/department.py
from __init__ import CURSOR, CONN
import sql_helper as sql
import validation as val
import pandas as pd

class Unit:
    '''
    A class to create and manage units in DB

    Constants
    ---------
    DF_COLUMNS: tuple
        - columns to be used for Unit dataframes

    Class Attributes
    ---------
    all: dict
        - dictionary of objects saved to the database

    Instance Attributes
    ---------
    id: int
        - unique identifier for instance
    acquisition_date: str
        - date property was acquired
    address: str
        - address of unit
    monthly_mortgage: float
        - monthly mortgage expense
    monthly_rent: float
        - monthly rental charge
    late_fee: float
        - charge for late payment

    Instance Methods
    ---------
    - delete: delete the table row corresponding to the current instance
    - save: insert a new row with the values of the current object
    - update: update the table row corresponding to the current instance
    - tenants: returns list of tenants associated with current unit
    - expenses: returns list of expenses associated with current unit
    - transactions: returns list of transactions associated with current unit

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
    DF_COLUMNS = ("id", "Acquisition Date", "Address", "Monthly Mortgage", "Monthly Rent", "Late Fee")

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, acquisition_date, address, monthly_mortgage, monthly_rent, late_fee=150, id=None):
        '''
        Constructs the necessary attributes for the Unit object.

        Instance Attributes
        ---------
        acquisition_date: str
            - date property was acquired
        address: str
            - address of unit
        monthly_mortgage: float
            - monthly mortgage expense
        monthly_rent: float
            - monthly rental charge
        late_fee: float
            - charge for late payment
        id: int
            - unique identifier for instance            
        '''
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
        '''
        initialize a new instance and save the object to the database
        '''
        unit = cls(acquisition_date, address, monthly_mortgage, monthly_rent, late_fee)
        unit.save()
        return unit
    
    @classmethod
    def instance_from_db(cls, row):
        '''
        return instance having the attribute values from the table row
        '''
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
        '''
        drop the table that persists instances
        '''
        sql.drop_table("units")

    @classmethod
    def find_by_id(cls, id):
        '''
        return object corresponding to the table row matching the specified primary key
        '''
        return sql.find_by_id(cls, "units", id)

    def delete(self):
        '''
        delete the table row corresponding to the current instance
        '''
        sql.delete(self, "units")

    @classmethod
    def get_all_instances(cls):
        '''
        return a list containing one instance per table row
        '''
        return sql.get_all(cls, "units", output_as_instances=True)

    @classmethod
    def get_dataframe(cls):
        '''
        return a Pandas DataFrame containing information from table
        '''
        return sql.get_all(cls, "units", output_as_instances=False)
    
    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        '''
        create a new table to persist the attributes of all instances
        '''
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
        '''
        insert a new row with the values of the current object
        '''
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
        '''
        update the table row corresponding to the current instance
        '''
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
        '''
        returns list of tenants associated with current unit
        '''
        from tenant import Tenant
        sql = """
            SELECT * FROM tenants
            WHERE unit_id = ?
        """
        CURSOR.execute(sql, (self.id,),)

        rows = CURSOR.fetchall()

        return pd.DataFrame(rows, columns=Tenant.DF_COLUMNS)

    def expenses(self):
        '''
        returns list of expenses associated with current unit
        '''
        from expense import Expense
        sql = """
            SELECT * FROM expenses
            WHERE unit_id = ?
        """
        CURSOR.execute(sql, (self.id,),)

        rows = CURSOR.fetchall()

        return pd.DataFrame(rows, columns=Expense.DF_COLUMNS)
    
    def transactions(self):
        '''
        returns list of transactions associated with current unit
        '''
        return sql.get_all_transactions(self.id)