#!/usr/bin/env python3
# import ipdb
import pandas as pd
import sql_helper as sql

import matplotlib.pyplot as plt

from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

df = sql.get_all_transactions()

# # Group by Unit and Type to calculate total amounts
grouped = df[["Type", "Amount", "Unit"]].groupby(["Unit", "Type"], as_index=False).sum()

# Plotting
fig, ax = plt.subplots(figsize=(8, 6))
grouped.plot(kind="bar", stacked=True, ax=ax, color=["skyblue", "orange"])

# Customize plot
ax.set_title("Bar Chart of Amounts Split by Unit and Type")
ax.set_xlabel("Unit")
ax.set_ylabel("Total Amount")
ax.legend(title="Transaction Type")
plt.xticks(rotation=0)
plt.tight_layout()

# Show plot
plt.show()

print(grouped)

