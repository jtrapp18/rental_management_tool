#!/usr/bin/env python3
# import ipdb
import pandas as pd

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

expense_df = Expense.get_dataframe()

print(expense_df)

