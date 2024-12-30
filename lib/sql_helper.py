import pandas as pd
from __init__ import CURSOR, CONN

def find_by_id(cls, table, id):
    """Return a Class instance having the attribute values from the table row."""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")
    
    sql = "SELECT * FROM " + table + " WHERE id = ?;"

    row = CURSOR.execute(sql, (id,)).fetchone()
    return cls.instance_from_db(row) if row else None


def drop_table(table):
    """ Drop the table that persists Class  instances """

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DROP TABLE IF EXISTS " + table + ";"
    
    CURSOR.execute(sql)
    CONN.commit()

def delete(self, table):
    """Delete the table row corresponding to the current Payment instance,
    delete the dictionary entry, and reassign id attribute"""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DELETE FROM " + table + " WHERE id = ?;"

    CURSOR.execute(sql, (self.id,))
    CONN.commit()

    # Delete the dictionary entry using id as the key
    del type(self).all[self.id]

    # Set the id to None
    self.id = None

def get_all(table):
    """Return a list containing one Review instance per table row"""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "SELECT * FROM " + table + ";"

    return CURSOR.execute(sql).fetchall()

def get_all_instances(cls, table):
    """Return a list containing one Review instance per table row"""

    rows = get_all(table)

    return [cls.instance_from_db(row) for row in rows]

def get_dataframe(cls, table):
    """Return a list containing one Review instance per table row"""

    rows = get_all(table)

    return pd.DataFrame(rows, columns=cls.DF_COLUMNS)

def get_all_transactions(unit_id=None):
    """Return a list of transactions"""

    columns = ["ID", "Type", "Amount", "Date", "Detail", "Unit"]

    sql_expenses = """
    SELECT 
        e.id AS ID, 
        'expense' AS Type, 
        e.amount AS Amount, 
        e.exp_date AS Date, 
        e.descr AS Detail, 
        e.unit_id AS Unit
    FROM expenses AS e"""

    sql_expenses += " WHERE e.unit_id = ?" if unit_id else ""

    sql_payments = """
    SELECT 
        p.id AS ID, 
        'payment' AS Type, 
        p.amount AS Amount, 
        p.pmt_date AS Date, 
        p.pmt_type AS Detail, 
        t.unit_id AS Unit
    FROM payments AS p
    JOIN tenants AS t
    ON p.tenant_id = t.id"""

    sql_payments += " WHERE t.unit_id = ?" if unit_id else ""

    sql = f"{sql_expenses} UNION {sql_payments} ORDER BY Unit, Date"

    filt = (unit_id, unit_id) if unit_id else ()
    rows = CURSOR.execute(sql, filt).fetchall()

    return pd.DataFrame(rows, columns=columns)

