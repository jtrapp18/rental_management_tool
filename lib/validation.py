import re
from datetime import datetime

def name_validation(name):
    '''
    validate name input and return only if validation passes
    '''
    if isinstance(name, str) and len(name) > 0:
        return name
    else:
        raise ValueError(f"Name must be non-empty string")
name_validation.constraints = "non-empty string"

def address_validation(address):
    '''
    validate address input and return only if validation passes
    '''
    if isinstance(address, str) and len(address) > 0:
        return address
    else:
        raise ValueError(f"Address must be non-empty string")
address_validation.constraints = "non-empty string"
    
def descr_validation(descr):
    '''
    validate description input and return only if validation passes
    '''
    if isinstance(descr, str) and len(descr) > 1:
        return descr
    else:
        raise ValueError(f"Description must be string greater than one character")
descr_validation.constraints = "string greater than one character"
    
def email_validation(email_address):
    '''
    validate email input and return only if validation passes
    '''
    email_pattern = r"[A-z][A-z0-9._-]+@\w+\.[a-z]+"
    email_regex = re.compile(email_pattern)

    if email_regex.fullmatch(email_address):
        return email_address
    else:
        raise ValueError(f"Did not enter valid email address")
email_validation.constraints = "valid email address"

def phone_validation(phone_number):
    '''
    validate phone number input and return only if validation passes
    '''
    phone_pattern = r"\([0-9]{3}\) [0-9]{3}-[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4}|[0-9]{10}"
    phone_regex = re.compile(phone_pattern)

    if phone_regex.fullmatch(phone_number):
        return phone_number
    else:
        raise ValueError(f"Did not enter valid phone number")
phone_validation.constraints = "valid 10-digit phone number"

def date_validation(date):
    '''
    validate date input and return only if validation passes
    '''
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    date_regex = re.compile(date_pattern)

    if date_regex.fullmatch(date):
        return date
    else:
        raise ValueError(f"Did not enter date in YYYY-DD-MM format")
date_validation.constraints = "YYYY-DD-MM format"

def optional_date_validation(date):
    '''
    validate date input and return only if validation passes
    '''
    if date is None or date == "":
        return None
    else:
        return date_validation(date)
optional_date_validation.constraints = "enter date in YYYY-DD-MM format or click enter to bypass"

def dollar_amt_validation(amount):
    '''
    validate dollar value input and return only if validation passes
    '''
    if (isinstance(amount, float) or isinstance(amount, int)) and amount >= 0:
        return float(amount)
    else:
        raise ValueError(f"Value must be positive number")
dollar_amt_validation.constraints = "positive number"

def method_validation(method):
    '''
    validate payment method input and return only if validation passes
    '''
    approved_methods = ["check", "venmo", "zelle", "cash"]

    if method in approved_methods:
        return method
    else:
        raise ValueError("Payment method must match one of the following:", approved_methods)
method_validation.constraints = ["check", "venmo", "zelle", "cash"]

def exp_category_validation(category):
    '''
    validate payment type input and return only if validation passes
    '''
    approved_categories = ["mortgage", "property mgmt", "repairs", "maintenance", "rennovations", "cleaning"]

    if category in approved_categories:
        return category
    else:
        raise ValueError("Payment type must match one of the following:", approved_categories)
exp_category_validation.constraints = ["mortgage", "property mgmt", "repairs", "maintenance", "rennovations", "cleaning"]
    
def pmt_category_validation(category):
    '''
    validate payment type input and return only if validation passes
    '''
    approved_categories = ["rent", "security deposit", "late fee"]

    if category in approved_categories:
        return category
    else:
        raise ValueError("Payment type must match one of the following:", approved_categories)
pmt_category_validation.constraints = ["rent", "security deposit", "late fee"]
    
def parent_id_validation(parent_id, parent_cls):
    '''
    validate parent id input and return only if validation passes
    '''
    if type(parent_id) is int and parent_cls.find_by_id(parent_id):
        return parent_id
    else:
        raise ValueError(f"parent_id must match an existing parent id in the database")
parent_id_validation.constraints = "match an existing parent id in the database"