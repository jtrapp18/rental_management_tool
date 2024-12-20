

def find_by_id(cls, CURSOR, table, id):
    """Return a Class instance having the attribute values from the table row."""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")
    
    sql = "SELECT * FROM " + table + " WHERE id = ?;"

    row = CURSOR.execute(sql, (id,)).fetchone()
    return cls.instance_from_db(row) if row else None


def drop_table(CURSOR, CONN, table):
    """ Drop the table that persists Class  instances """

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DROP TABLE IF EXISTS " + table + ";"
    
    CURSOR.execute(sql)
    CONN.commit()

def delete(CURSOR, CONN, table, id):
    """Delete the table row corresponding to the current Payment instance,
    delete the dictionary entry, and reassign id attribute"""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "DELETE FROM " + table + " WHERE id = ?;"

    CURSOR.execute(sql, (id,))
    CONN.commit()

    # Delete the dictionary entry using id as the key
    del type(self).all[id]

    # Set the id to None
    id = None

def get_all(cls, CURSOR, table):
    """Return a list containing one Review instance per table row"""

    # Validate the table name to prevent SQL injection
    if not table.isidentifier():
        raise ValueError("Invalid table name")

    sql = "SELECT * FROM " + table + ";"

    rows = CURSOR.execute(sql).fetchall()

    return [cls.instance_from_db(row) for row in rows]