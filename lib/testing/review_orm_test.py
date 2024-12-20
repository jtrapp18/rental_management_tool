from employee import Employee, CONN, CURSOR
from department import Department
from review import Review
import pytest


class TestReview:
    '''Class Review in review.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''drop tables prior to each test.'''

        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")

    def test_creates_table(self):
        '''contains method "create_table()" that creates table "reviews" if it does not exist.'''

        Department.create_table()
        Employee.create_table()
        Review.create_table()
        assert (CURSOR.execute("SELECT * FROM reviews"))

    def test_drops_table(self):
        '''contains method "drop_table()" that drops table "reviews" if it exists.'''

        sql = """
            CREATE TABLE IF NOT EXISTS departments
                (id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT)
        """
        CURSOR.execute(sql)

        sql = """  
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)

        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """

        Review.drop_table()

        # Confirm employee table exists
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employees'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result)

        # Confirm reviews table does not exist
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='reviews'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result is None)

    def test_saves_review(self):
        '''contains method "save()" that saves an Review instance to the db and sets the instance id.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        employee = Employee("Sasha", "Manager", department.id)
        employee.save()

        Review.create_table()
        review = Review(2023, "Excellent Python skills!", employee.id)
        review.save()

        sql = """
            SELECT * FROM reviews
        """

        row = CURSOR.execute(sql).fetchone()
        assert ((row[0], row[1], row[2], row[3]) ==
                (review.id, review.year, review.summary, review.employee_id) ==
                (review.id, 2023, "Excellent Python skills!", employee.id))

    def test_creates_review(self):
        '''contains method "create()" that creates a new row in the db using the parameter data and returns a Review instance.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        employee = Employee.create("Kai", "Web Developer", department.id)

        Review.create_table()
        review = Review.create(2023, "Excellent Python skills!", employee.id)

        sql = """
            SELECT * FROM reviews
        """
        row = CURSOR.execute(sql).fetchone()
        assert ((row[0], row[1], row[2], row[3]) ==
                (review.id, review.year, review.summary, review.employee_id) ==
                (review.id, 2023, "Excellent Python skills!", employee.id))

    def test_instance_from_db(self):
        '''contains method "instance_from_db()" that takes a db row and creates an Review instance.'''

        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (2022, 'Amazing coder!', ?)
        """
        CURSOR.execute(sql, (employee.id,))

        sql = """
            SELECT * FROM reviews
        """
        row = CURSOR.execute(sql).fetchone()

        review = Review.instance_from_db(row)
        assert ((row[0], row[1], row[2], row[3]) ==
                (review.id, review.year, review.summary, review.employee_id) ==
                (review.id, 2022, "Amazing coder!", employee.id))

    def test_finds_by_id(self):
        '''contains method "find_by_id()" that returns a Review instance corresponding to its db row retrieved by id.'''

        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Great coder!", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Awesome coder!", employee.id)
        id2 = review2.id

        review = Review.find_by_id(review1.id)
        assert ((review.id, review.year, review.summary, review.employee_id) ==
                (id1, 2020, "Great coder!", employee.id))

        review = Review.find_by_id(review2.id)
        assert ((review.id, review.year, review.summary, review.employee_id) ==
                (id2, 2000, "Awesome coder!", employee.id))

        review = Review.find_by_id(3)
        assert (review is None)

    def test_updates_row(self):
        '''contains a method "update()" that updates an instance's corresponding database record to match its new attribute values.'''

        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(
            2020, "Usually double checks their work", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Takes long lunches", employee.id)
        id2 = review2.id

        review1.year = 2023
        review1.summary = "Always double checks their work"
        review1.update()

        # Confirm review1 updated
        review = Review.find_by_id(id1)
        assert ((review.id, review.year, review.summary, review.employee_id) ==
                (review1.id, review1.year, review1.summary, review1.employee_id) ==
                (id1, 2023, "Always double checks their work", employee.id))

        # Confirm review2 not updated
        review = Review.find_by_id(id2)
        assert ((review.id, review.year, review.summary, review.employee_id) ==
                (review2.id, review2.year, review2.summary, review2.employee_id) ==
                (id2, 2000, "Takes long lunches", employee.id))

    def test_deletes_row(self):
        '''contains a method "delete()" that deletes the instance's corresponding database record'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(
            2020, "Usually double checks their work", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Takes long lunches", employee.id)
        id2 = review2.id

        review1.delete()
        # assert row deleted
        assert (Review.find_by_id(id1) is None)
        # assert Review object state is correct, id is None
        assert ((review1.id, review1.year, review1.summary, review1.employee_id) ==
                (None, 2020, "Usually double checks their work", employee.id))
        # assert dictionary entry was deleted
        assert(Review.all.get(id1) is None)
        
        review = Review.find_by_id(id2)
        # assert review2 row not modified, review2 object not modified
        assert ((review.id, review.year, review.summary, review.employee_id) ==
                (review2.id, review2.year, review2.summary, review2.employee_id) ==
                (id2, 2000, "Takes long lunches", employee.id))

    
    def test_gets_all(self):
        '''contains method "get_all()" that returns a list of Review instances for every record in the db.'''

        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Great coder!", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Awesome coders!", employee.id)
        id2 = review2.id

        reviews = Review.get_all()
        assert (len(reviews) == 2)
        assert ((reviews[0].id, reviews[0].year, reviews[0].summary, reviews[0].employee_id) ==
                (review1.id, review1.year, review1.summary, review1.employee_id))
        assert ((reviews[1].id, reviews[1].year, reviews[1].summary, reviews[1].employee_id) ==
                (review2.id, review2.year, review2.summary, review2.employee_id))

 