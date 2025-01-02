import pandas as pd

# project modules
from lib import Unit
from lib.helper import validation as val
from lib.helper import sql_helper as sql

class Tenant:
    '''
    A class to create and manage tenants in DB

    Constants
    ---------
    DF_COLUMNS: tuple
        - columns to be used for Tenant dataframes
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
    name: str
        - full name of tenant
    email_address: str
        - email address of tenant
    phone_number: str or float
        - phone number of tenant
    move_in_date: str
        - move in date of tenant
    move_out_date: str
        - move out date of tenant
    unit_id: int
        - id of parent unit

    Instance Methods
    ---------
    - delete: delete the table row corresponding to the current instance
    - save: insert a new row with the values of the current object
    - update: update the table row corresponding to the current instance
    - payments: returns list of payments associated with current unit
    - get_rollforward: creates and returns a detailed payment rollforward for tenant

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
    DF_COLUMNS = ("id", "Name", "Email Address", "Phone Number", "Move In Date", "Move Out Date", "Unit ID")
    VALIDATION_DICT = {
        "name": val.name_validation, 
        "email_address": val.email_validation, 
        "phone_number": val.phone_validation, 
        "move_in_date": val.date_validation,
        "move_out_date": val.optional_date_validation
        }

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, name, email_address, phone_number, unit_id, move_in_date, move_out_date=None, id=None):
        '''
        Constructs the necessary attributes for the Tenant object.

        Instance Attributes
        ---------
        id: int
            - unique identifier for instance
        name: str
            - full name of tenant
        email_address: str
            - email address of tenant
        phone_number: str or float
            - phone number of tenant
        move_in_date: str
            - move in date of tenant
        move_out_date: str
            - move out date of tenant
        unit_id: int
            - id of parent unit
        '''
        self.id = id
        self.name = name
        self.email_address = email_address
        self.phone_number = phone_number
        self.move_in_date = move_in_date
        self.move_out_date = move_out_date        
        self.unit_id = unit_id

    def __repr__(self):
        move_out_txt = self.move_out_date if self.move_out_date else 'Present'
        return (
            f"<Tenant {self.id}: {self.name} | " +
            f"Contact Info: {self.email_address}, {self.phone_number} | " +
            f"Dates: {self.move_in_date} to {move_out_txt} | " +
            f"Unit ID: {self.unit_id}>"
        )

    # ///////////////////////////////////////////////////////////////
    # VALIDATION OF INPUTS
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = val.name_validation(name)

    @property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, email_address):
        self._email_address = val.email_validation(email_address)
        
    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        self._phone_number = val.phone_validation(phone_number)

    @property
    def move_in_date(self):
        return self._move_in_date

    @move_in_date.setter
    def move_in_date(self, move_in_date):
        self._move_in_date = val.date_validation(move_in_date)
        
    @property
    def move_out_date(self):
        return self._move_out_date

    @move_out_date.setter
    def move_out_date(self, move_out_date):
        self._move_out_date = val.optional_date_validation(move_out_date)

    @property
    def unit_id(self):
        return self._unit_id

    @unit_id.setter
    def unit_id(self, unit_id):
        self._unit_id = val.parent_id_validation(unit_id, Unit)
    
    # ///////////////////////////////////////////////////////////////
    # MANAGE CLASS INSTANCES

    @classmethod
    def create(cls, name, email_address, phone_number, unit_id, move_in_date, move_out_date):
        '''
        initialize a new instance and save the object to the database
        '''
        tenant = cls(name, email_address, phone_number, unit_id, move_in_date, move_out_date)
        tenant.save()
        return tenant

    @classmethod
    def instance_from_db(cls, row):
        '''
        return instance having the attribute values from the table row
        '''
        # Check the dictionary for  existing instance using the row's primary key
        tenant = cls.all.get(row[0])

        id = row[0]
        name = row[1]
        email_address = row[2]
        phone_number = row[3]
        move_in_date = row[4]
        move_out_date = row[5]
        unit_id = row[6]
    
        if tenant:
            # ensure attributes match row values in case local instance was modified
            tenant.name = name
            tenant.email_address = email_address
            tenant.phone_number = phone_number
            tenant.move_in_date = move_in_date
            tenant.move_out_date = move_out_date
            tenant.unit_id = unit_id
        else:
            # not in dictionary, create new instance and add to dictionary
            tenant = cls(name, email_address, phone_number, unit_id, move_in_date, move_out_date, id) # reordering due to optional values
            cls.all[tenant.id] = tenant
        return tenant
    
    # ///////////////////////////////////////////////////////////////
    # GENERIC DATABASE FUNCTIONS

    @classmethod
    def drop_table(cls):
        '''
        drop the table that persists instances
        '''
        sql.drop_table("tenants")

    @classmethod
    def find_by_id(cls, id):
        '''
        return object corresponding to the table row matching the specified primary key
        '''
        return sql.find_by_id(cls, "tenants", id)
    
    def delete(self):
        '''
        delete the table row corresponding to the current instance
        '''
        sql.delete(self, "tenants")

    @classmethod
    def get_all_instances(cls):
        '''
        return a list containing one instance per table row
        '''
        return sql.get_all(cls, "tenants", output_as_instances=True)

    @classmethod
    def get_dataframe(cls):
        '''
        return a Pandas DataFrame containing information from table
        '''
        return sql.get_all(cls, "tenants", output_as_instances=False)
    
    # ///////////////////////////////////////////////////////////////
    # CLASS-SPECIFIC DATABASE FUNCTIONS

    @classmethod
    def create_table(cls):
        '''
        create a new table to persist the attributes of all instances
        '''
        query = """
            CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email_address TEXT,
            phone_number TEXT,
            move_in_date DATE,
            move_out_date DATE,
            unit_id INTEGER,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE)
        """
        sql.CURSOR.execute(query)
        sql.CONN.commit()

    def save(self):
        '''
        insert a new row with the values of the current object
        '''
        query = """
                INSERT INTO tenants (name, email_address, phone_number, move_in_date, move_out_date, unit_id)
                VALUES (?, ?, ?, ?, ?, ?)
        """

        sql.CURSOR.execute(query, (self.name, 
                             self.email_address, self.phone_number, 
                             self.move_in_date, self.move_out_date, 
                             self.unit_id))
        sql.CONN.commit()

        self.id = sql.CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        '''
        update the table row corresponding to the current instance
        '''
        query = """
            UPDATE tenants
            SET name = ?, email_address = ?, phone_number = ?, move_in_date = ?, move_out_date = ?, unit_id = ?
            WHERE id = ?
        """
        sql.CURSOR.execute(query, (self.name, 
                             self.email_address, self.phone_number,
                             self.move_in_date, self.move_out_date,
                             self.unit_id, self.id))
        sql.CONN.commit()

    # ///////////////////////////////////////////////////////////////
    # LOOKUPS FROM LINKED TABLES

    def payments(self, output_as_instances=False):
        '''
        returns list of payments associated with current unit
        '''        
        from lib import Payment
        query = """
            SELECT * FROM payments
            WHERE tenant_id = ?
        """
        sql.CURSOR.execute(query, (self.id,),)

        rows = sql.CURSOR.fetchall()

        output = [Payment.instance_from_db(row) for row in rows] \
            if output_as_instances else pd.DataFrame(rows, columns=Payment.DF_COLUMNS)

        return output
    
    def get_rollforward(self):
        '''
        creates and returns a detailed payment rollforward for tenant
        '''
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta

        payments = self.payments(output_as_instances=True)
        payments.sort(key=lambda p: p.pmt_date)
        unit = Unit.find_by_id(self.unit_id)

        pmt_start_date = datetime.strptime(self.move_in_date, '%Y-%m-%d')
        pmt_stop_date = datetime.strptime(self.move_out_date, '%Y-%m-%d') if self.move_out_date else datetime.now()

        BOP = pmt_start_date
        back_due = 0
        rollforward_data = []

        while BOP < pmt_stop_date:
            payments_applied = []

            EOP = BOP + relativedelta(months=1)
            date_late = BOP + relativedelta(days=11)

            for payment in payments[:]:
                pmt_date = datetime.strptime(payment.pmt_date, '%Y-%m-%d')
                if pmt_date >= EOP:
                    break

                payments.remove(payment)  # Remove the payment from the list
                if payment.category=='rent':
                    payments_applied.append(payment)  # Add it to payments_applied

            bop_due = unit.monthly_rent + back_due

            BOP_dict = {
                'Due Date': BOP,
                'Rent Due': unit.monthly_rent,
                'Back Due': back_due,
                'BOP Due': bop_due
            }

            payment_dict = {}
            rent_paid = 0
            rent_paid_on_time = 0

            for i, payment in enumerate(payments_applied, start=1):
                pmt_date = datetime.strptime(payment.pmt_date, '%Y-%m-%d')
                payment_info = {
                    f'Pmt {i}: Check no.': payment.id,
                    f'Pmt {i}: Method': payment.method,
                    f'Pmt {i}: Date': payment.pmt_date,
                    f'Pmt {i}: Amount': payment.amount,
                }
                rent_paid += payment.amount
                rent_paid_on_time += rent_paid * (pmt_date < date_late)

                payment_dict = {**payment_dict, **payment_info}

            # determine if tenant owes a late fee
            late = (unit.monthly_rent - rent_paid_on_time) > 0
            late_fee_owed = late*unit.late_fee

            rent_owed = unit.monthly_rent - rent_paid
            total_owed = late_fee_owed + rent_owed
            back_due += total_owed

            EOP_dict = {
                'Late Fee': late_fee_owed,
                'Rent Owed': rent_owed,
                'Total Owed': total_owed,
                'EOP Due': back_due
            }

            rollforward_data.append({**BOP_dict, **payment_dict, **EOP_dict})

            BOP += relativedelta(months=1)

        return pd.DataFrame(rollforward_data)
