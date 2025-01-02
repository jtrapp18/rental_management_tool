import pandas as pd
from datetime import datetime

# project modules
from lib import Unit
from lib import Tenant
from lib.helper import validation as val
from lib.helper import sql_helper as sql

class Payment:
    '''
    A class to create and manage payments in DB

    Constants
    ---------
    DF_COLUMNS: tuple
        - columns to be used for Payment dataframes
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
    amount: float
        - dollar value of payment
    pmt_date: str
        - date payment was incurred
    method: str
        - method used to pay (e.g. check, cash)
    category: str
        - type of payment (e.g. rent, security deposit)
    tenant_id: int
        - id of parent tenant

    Instance Methods
    ---------
    - delete: delete the table row corresponding to the current instance
    - save: insert a new row with the values of the current object
    - update: update the table row corresponding to the current instance
    - print_receipt: generates and prints receipt to pdf for a single payment

    Class Methods
    ---------
    - create: initialize a new instance and save the object to the database
    - instance_from_db: return instance having the attribute values from the table row
    - drop_table: drop the table that persists instances
    - find_by_id: return object corresponding to the table row matching the specified primary key
    - get_all_instances: return a list containing one instance per table row
    - get_dataframe: return a Pandas DataFrame containing information from table
    - get_dataframe_w_unit: return a Pandas DataFrame which includes unit ID
    - create_table: create a new table to persist the attributes of all instances
    '''
    DF_COLUMNS = ("id", "Category", "Amount", "Date", "Method", "Tenant ID")
    VALIDATION_DICT = {
        "amount": val.dollar_amt_validation,
        "pmt_date": val.date_validation,
        "method": val.method_validation,
        "category": val.pmt_category_validation
        }

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, amount, pmt_date, method, tenant_id, category="rent", id=None):
        '''
        Constructs the necessary attributes for the Payment object.

        Parameters
        ---------
        amount: float
            - dollar value of payment
        pmt_date: str
            - date payment was incurred
        method: str
            - method used to pay (e.g. check, cash)
        tenant_id: int
            - id of parent tenant
        category: str
            - type of payment (e.g. rent, security deposit)
        id: int
            - unique identifier for instance
        '''
        self.id = id
        self.amount = amount
        self.pmt_date = pmt_date
        self.method = method
        self.category = category
        self.tenant_id = tenant_id

    def __repr__(self):
        return (
            f"<Payment {self.id}: {self.category}, {self.pmt_date}, {self.amount}, {self.method}, "
            + f"Tenant: {self.tenant_id}>"
        )
    
    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):

        self._amount = val.dollar_amt_validation(amount)
        
    @property
    def pmt_date(self):
        return self._pmt_date

    @pmt_date.setter
    def pmt_date(self, pmt_date):
        self._pmt_date = val.date_validation(pmt_date)
        
    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = val.method_validation(method)
        
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = val.pmt_category_validation(category)

    @property
    def tenant_id(self):
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        self._tenant_id = val.parent_id_validation(tenant_id, Tenant)
        
    # ///////////////////////////////////////////////////////////////
    # MANAGE CLASS INSTANCES

    @classmethod
    def create(cls, amount, pmt_date, method, tenant_id, category):
        '''
        initialize a new instance and save the object to the database
        '''
        payment = cls(amount, pmt_date, method, tenant_id, category)
        payment.save()
        return payment
   
    @classmethod
    def instance_from_db(cls, row):
        '''
        return instance having the attribute values from the table row
        '''
        # Check the dictionary for  existing instance using the row's primary key
        payment = cls.all.get(row[0])

        id = row[0]
        category = row[1]
        amount = row[2]
        pmt_date = row[3]
        method = row[4]
        tenant_id = row[5]
        
        if payment:
            # ensure attributes match row values in case local object was modified
            payment.category = category
            payment.amount = amount
            payment.pmt_date = pmt_date
            payment.method = method
            payment.tenant_id = tenant_id
        else:
            # not in dictionary, create new instance and add to dictionary
            payment = cls(amount, pmt_date, method, tenant_id, category, id) # reordering due to optional values
            cls.all[payment.id] = payment
        return payment
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        '''
        drop the table that persists instances
        '''
        sql.drop_table("payments")
   
    @classmethod
    def find_by_id(cls, id):
        '''
        return object corresponding to the table row matching the specified primary key
        '''
        return sql.find_by_id(cls, "payments", id)

    def delete(self):
        '''
        delete the table row corresponding to the current instance
        '''
        sql.delete(self, "payments")

    @classmethod
    def get_all_instances(cls):
        '''
        return a list containing one instance per table row
        '''
        return sql.get_all(cls, "payments", output_as_instances=True)
    
    @classmethod
    def get_dataframe(cls):
        '''
        return a Pandas DataFrame containing information from table
        '''
        return sql.get_all(cls, "payments", output_as_instances=False)
    
    @classmethod
    def get_dataframe_w_unit(cls):
        '''
        return a Pandas DataFrame which includes unit ID
        '''
        query = """
        SELECT
            p.id,
            p.category,
            p.amount, 
            p.pmt_date,
            p.method,
            p.tenant_id,
            t.unit_id
        FROM payments AS p
        JOIN tenants AS t
        ON p.tenant_id = t.id
        """
        sql.CURSOR.execute(query)

        rows = sql.CURSOR.fetchall()

        return pd.DataFrame(rows, columns=cls.DF_COLUMNS + ('Unit',))
    
    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        '''
        create a new table to persist the attributes of all instances
        '''
        query = """
            CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            category TEXT,
            amount FLOAT,
            pmt_date DATE,
            method TEXT,
            tenant_id INTEGER,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE)
        """
        sql.CURSOR.execute(query)
        sql.CONN.commit()

    def save(self):
        '''
        insert a new row with the values of the current object
        '''
        query = """
            INSERT INTO payments (category, amount, pmt_date, method, tenant_id)
            VALUES (?, ?, ?, ?, ?)
        """

        sql.CURSOR.execute(query, (self.category, self.amount, 
                             self.pmt_date, self.method, 
                             self.tenant_id))
        sql.CONN.commit()

        self.id = sql.CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        '''
        update the table row corresponding to the current instance
        '''
        query = """
            UPDATE payments
            SET category = ?, amount = ?, pmt_date = ?, method = ?, tenant_id = ?
            WHERE id = ?
        """
        sql.CURSOR.execute(query, (self.category, self.amount, 
                             self.pmt_date, self.method, 
                             self.tenant_id, self.id))
        sql.CONN.commit()

    def print_receipt(self, path):
        '''
        generates and prints receipt to pdf for a single payment

        path: str
            - file path to save receipt
        '''
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors

        tenant = Tenant.find_by_id(self.tenant_id)
        unit = Unit.find_by_id(tenant.unit_id)

        doc = SimpleDocTemplate(path)

        table_style = TableStyle([
            ('FONT', (0, 0), (1, 0), 'Helvetica-Bold', 20),  # Bold title
            ('SPAN', (0, 0), (1, 0)),  # Merge title cells
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 12),  # Regular font for other rows
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        payment_info = [
            [f"Receipt of Payment", ""],
            ["Receipt Number:", self.id],
            ["For:", self.category.title()],             
            ["Date:", self.pmt_date],
            ["Amount:", f"${self.amount:,.2f}"],
            ["Method:", self.method],
            ["Paid by:", tenant.name],
            ["Address:", unit.address],
        ]

        payment_table = Table(payment_info, colWidths=[150, 300])
        payment_table.setStyle(table_style)
        
        doc.build([payment_table])