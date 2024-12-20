from __init__ import CURSOR, CONN
from unit import Unit
from tenant import Tenant
import validation as val
import sql_helper as sql

class Payment:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, amount, pmt_date, method, tenant_id, pmt_type="rent", id=None):
        self.id = id
        self.amount = amount
        self.pmt_date = pmt_date
        self.method = method
        self.pmt_type = pmt_type
        self.tenant_id = tenant_id

    def __repr__(self):
        return (
            f"<Payment {self.id}: {self.pmt_type}, {self.pmt_date}, {self.amount}, {self.method}, "
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
    def pmt_type(self):
        return self._pmt_type

    @pmt_type.setter
    def pmt_type(self, pmt_type):
        self._pmt_type = val.pmt_type_validation(pmt_type)

    @property
    def tenant_id(self):
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        self._tenant_id = val.parent_id_validation(tenant_id, Tenant)
        
    # ///////////////////////////////////////////////////////////////
    # MANAGE CLASS INSTANCES

    @classmethod
    def create(cls, amount, pmt_date, method, tenant_id, pmt_type):
        """ Initialize a new Payment instance and save the object to the database. Return the new instance. """
        payment = cls(amount, pmt_date, method, tenant_id, pmt_type)
        payment.save()
        return payment
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Payment instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        payment = cls.all.get(row[0])
        if payment:
            # ensure attributes match row values in case local object was modified
            payment.pmt_type = row[1]
            payment.amount = row[2]
            payment.pmt_date = row[3]
            payment.method = row[4]
            payment.tenant_id = row[5]
        else:
            # not in dictionary, create new instance and add to dictionary
            payment = cls(row[1], row[2], row[3], row[4], row[5])
            payment.id = row[0]
            cls.all[payment.id] = payment
        return payment
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Payment instances """
        sql.drop_table(CURSOR, CONN, "payments")
   
    @classmethod
    def find_by_id(cls, id):
        """Return Payment object corresponding to the table row matching the specified primary key"""
        return sql.find_by_id(cls, CURSOR, "payments", id)

    def delete(self):
        """Delete the table row corresponding to the current Payment instance,
        delete the dictionary entry, and reassign id attribute"""

        sql.delete(CURSOR, CONN, "payments", self.id)

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        return sql.get_all(cls, CURSOR, "payments")

    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            pmt_type TEXT,
            amount FLOAT,
            pmt_date DATE,
            method TEXT,
            tenant_id INTEGER,
            FOREIGN KEY (tenant_id) REFERENCES tenant(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the values of the current Payment object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
            INSERT INTO payments (pmt_type, amount, pmt_date, method, tenant_id)
            VALUES (?, ?, ?, ?, ?)
        """

        CURSOR.execute(sql, (self.pmt_type, self.amount, 
                             self.pmt_date, self.method, 
                             self.tenant_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE payments
            SET pmt_type = ?, amount = ?, pmt_date = ?, method = ?, tenant_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.pmt_type, self.amount, 
                             self.pmt_date, self.method, 
                             self.tenant_id, self.id))
        CONN.commit()