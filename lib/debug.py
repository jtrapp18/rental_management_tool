#!/usr/bin/env python3
# import ipdb
import pandas as pd
import sql_helper as sql
import numpy as np

import matplotlib.pyplot as plt

from report import Report

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense


def generate_income_report(year='all'):
    expense_report = Report(year)

    expense_report.add_section_cover('All Units', 'Analytics for aggregated unit data')
    expense_report.add_transaction_bar()
    expense_report.add_subplots()

    expense_report.add_section_cover('Individual Units', 'Analytics for individual rental units')
    for unit in range(1, 6):
        expense_report.indiv_unit_charts(unit)
    expense_report.report.close()

generate_income_report(2022)