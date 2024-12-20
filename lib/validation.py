import re
from datetime import datetime

def name_validation(name):
    if isinstance(name, str) and len(name):
        return name
    else:
        raise ValueError("Name must be a non-empty string")

def address_validation(address):
    if isinstance(address, str) and len(address):
        return address
    else:
        raise ValueError("Address must be a non-empty string")
    
def email_validation(email_address):
    email_pattern = r"[A-z][A-z0-9._-]+@\w+\.[a-z]+"
    email_regex = re.compile(email_pattern)

    if email_regex.fullmatch(email_address):
        return email_address
    else:
        raise ValueError("Email address is invalid")

def phone_validation(phone_number):
    phone_pattern = r"\([0-9]{3}\) [0-9]{3}-[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4}|[0-9]{10}"
    phone_regex = re.compile(phone_pattern)

    if phone_regex.fullmatch(phone_number):
        return phone_number
    else:
        raise ValueError("Phone number is invalid")

def date_validation(date):
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    date_regex = re.compile(date_pattern)

    if date_regex.fullmatch(date):
        return date
    else:
        raise ValueError("Date is invalid")

def dollar_amt_validation(amount):

    if (isinstance(amount, float) or isinstance(amount, int)) and amount >= 0:
        return float(amount)
    else:
        raise ValueError("Value must be a positive number")

def method_validation(method):
    approved_methods = ["check", "venmo", "zelle", "cash"]

    if method in approved_methods:
        return method
    else:
        raise ValueError("Payment method must match one of the following:", approved_methods)


def pmt_type_validation(pmt_type):
    approved_pmt_types = ["rent", "security deposit", "late fee"]

    if pmt_type in approved_pmt_types:
        return pmt_type
    else:
        raise ValueError("Payment type must match one of the following:", approved_pmt_types)
    
def parent_id_validation(parent_id, parent_cls):

    if type(parent_id) is int and parent_cls.find_by_id(parent_id):
        return parent_id
    else:
        raise ValueError(f"parent_id must reference a parent in the database")
