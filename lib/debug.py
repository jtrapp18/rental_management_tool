#!/usr/bin/env python3
# import ipdb

from unit import Unit
from tenant import Tenant
from payment import Payment

tenant = Tenant.find_by_id(1)

# print(tenant.payments())
print(tenant.unit_information())

# ipdb.set_trace()