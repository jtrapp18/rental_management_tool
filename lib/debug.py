#!/usr/bin/env python3
# import ipdb
import pandas as pd
import sql_helper as sql
import numpy as np

import matplotlib.pyplot as plt

from report import generate_income_report

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

payment = Payment.find_by_id(1)
tenant = Tenant.find_by_id(payment.tenant_id)
unit = Unit.find_by_id(tenant.unit_id)
