#!/usr/bin/env python3
# import ipdb
import pandas as pd
import sql_helper as sql
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt

from report import generate_income_report

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

tenant = Tenant.find_by_id(2)

print(tenant.get_rollforward())