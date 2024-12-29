#!/usr/bin/env python3
# import ipdb
import pandas as pd
import sql_helper as sql

import matplotlib.pyplot as plt

from report import Report

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

df = sql.get_all_transactions()

# # Group by Unit and Type to calculate total amounts
grouped = df[["Type", "Amount", "Unit"]].groupby(["Unit", "Type"], as_index=False).sum()

def plotData(data):
    fig = plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax2=ax.twinx

    data.plot(kind='bar', ax=ax, figsize=(12, 8))

    ax.set_ylabel('y label')
    ax.set_title('title')
    # ax.yaxis.set_major_formatter()
    ax.tick_params(axis='x', labelrotation=45)
    # ax.get_legend.remove()

    ax.legend(loc='best')
    ax.grid(axis='y')

    print(grouped)

    return fig

fig = plotData(grouped)

expense_report = Report('Expense', 2020)
expense_report.add_figure(fig)
expense_report.report.close()


