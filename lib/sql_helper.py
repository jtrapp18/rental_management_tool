import pandas as pd
from __init__ import CURSOR, CONN

def find_by_id(cls, table, id):
    '''
    return class instance based on id attribute

    Parameters
    ---------
    cls: class
        - class which contains desired instance (e.g. Payment, Tenant)
    table: str
        - name of table in DB which corresponds to specified class
    id: int
        - id of class instance

    Returns
    ---------
    class instance
        - instance of specified class whose id attribute matches parameter
    '''
    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")
    
    sql = "SELECT * FROM " + table + " WHERE id = ?;"

    row = CURSOR.execute(sql, (id,)).fetchone()
    return cls.instance_from_db(row) if row else None

def drop_table(table):
    '''
    drops specified table in DB

    Parameters
    ---------
    table: str
        - name of table in DB to drop
    '''
    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DROP TABLE IF EXISTS " + table + ";"
    
    CURSOR.execute(sql)
    CONN.commit()

def delete(inst, table):
    '''
    deletes table row corresponding to specified instance

    Parameters
    ---------
    inst: class instance
        - instance of class which corresponds to DB row to be deleted
    table: str
        - name of table in DB which corresponds to specified instance
    '''
    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DELETE FROM " + table + " WHERE id = ?;"

    CURSOR.execute(sql, (inst.id,))
    CONN.commit()

    # Delete the dictionary entry using id as the key
    del type(inst).all[inst.id]

    # Set the id to None
    inst.id = None

def get_all(cls, table, output_as_instances=False):
    '''
    retreives information from a specified table from DB

    Parameters
    ---------
    cls: class
        - class which contains desired instance (e.g. Payment, Tenant)
    table: str
        - name of table in DB which corresponds to specified class
    output_as_instances (optional): boolean
        - indicates whether to return values as a list of instances or in DataFrame

    Returns
    ---------
    output: list or Pandas DataFrame
        - list of class instances output_as_instances set to True
        - Pandas DataFrame containing DB table information if output_as_instances set to False
    '''
    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "SELECT * FROM " + table + ";"

    rows = CURSOR.execute(sql).fetchall()

    output = [cls.instance_from_db(row) for row in rows] \
        if output_as_instances else pd.DataFrame(rows, columns=cls.DF_COLUMNS)

    return output

def get_all_transactions(unit_id=None):
    '''
    retreives transactions (payments, expenses) linked to a specified unit

    Parameters
    ---------
    unit_id (optional): int
        - id of Unit to filter on
        - if set to None, shows all units

    Returns
    ---------
    output: Pandas DataFrame
        - DataFrame containing all transactions (payments, expenses) for specified unit
    '''
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

def get_transaction_summary():
    '''
    retreives summary of transactions for all units

    Returns
    ---------
    output: Pandas DataFrame
        - DataFrame containing summary of transaction data
    '''
    df = get_all_transactions()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    df_pivot = df.pivot_table(index='Year', columns='Type', values='Amount', aggfunc='sum')

    return df_pivot