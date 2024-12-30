import random

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker
from unit import Unit
from tenant import Tenant
from payment import Payment
from expense import Expense

if __name__ == "__main__":

    print("Resetting tables...")

    Unit.drop_table()
    Tenant.drop_table()
    Payment.drop_table()
    Expense.drop_table()

    Unit.create_table()
    Tenant.create_table()
    Payment.create_table()
    Expense.create_table()

    print("Creating constants...")

    fake = Faker()

    print("Seeding unit table...")

    units = []
    acquisition_date = datetime.now() - timedelta(11 * 365)

    for _ in range(5):
        monthly_rent = random.randint(1800 // 50, 3500 // 50) * 50
        monthly_mortgage = monthly_rent*random.randint(85, 105) // 100
        
        unit = Unit(
            acquisition_date=acquisition_date.strftime('%Y-%m-%d'),
            address=fake.address(),
            monthly_mortgage=float(monthly_mortgage),
            monthly_rent=float(monthly_rent),
            late_fee=150,
        )
        unit.save()
        units.append(unit)

        acquisition_date += timedelta(random.randint(1 * 365, 2 * 365))

    print("Seeding expense table...")

    maintenance_expenses = ["repairs", "regular maintenance", "home improvements", "cleaning fee"]

    expenses = []

    for unit in units:

        monthly_rent = unit.monthly_rent
        exp_date = datetime.strptime(unit.acquisition_date, '%Y-%m-%d')

        while exp_date <= datetime.now():

            # Monthly mortgage payment
            expense = Expense(
                descr="mortgage",
                amount=monthly_mortgage,
                exp_date=exp_date.strftime('%Y-%m-%d'),
                unit_id=unit.id,
            )
            expense.save()
            expenses.append(expense)

            # Monthly property management fee
            expense = Expense(
                descr="property mgmt fee",
                amount=monthly_rent*0.1,
                exp_date=exp_date.strftime('%Y-%m-%d'),
                unit_id=unit.id,
            )
            expense.save()
            expenses.append(expense)

            # Miscellaneous expenses
            setfwd = random.randint(1, 30)
            misc_date = exp_date + timedelta(days=setfwd)
            misc_num = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1], k=1)[0]

            for i in range(0, misc_num):
                expense = Expense(
                    descr=random.choice(maintenance_expenses),
                    amount=monthly_rent*0.1,
                    exp_date=misc_date.strftime('%Y-%m-%d'),
                    unit_id=unit.id,
                )
                expense.save()
                expenses.append(expense)
            
                setfwd = random.randint(1, 30)

                if (30 - setfwd) < 1:
                    break

                misc_date += timedelta(days=(30-setfwd))

            exp_date += relativedelta(months=1)

    print("Seeding tenant table...")

    tenants = []

    for unit in units:
        acquisition_date = datetime.strptime(unit.acquisition_date, '%Y-%m-%d')
        days_vacant = random.randint(15, 60)
        move_in = acquisition_date + timedelta(days=days_vacant)

        while move_in:
            first_name = fake.first_name()
            last_name = fake.last_name()

            days_occupied = random.randint(365, 5 * 365)
            move_out = move_in + timedelta(days=days_occupied)
            move_out = None if move_out > datetime.now() else move_out

            tenant = Tenant(
                name=f"{first_name} {last_name}",
                email_address=f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                phone_number=str(random.randint(1000000000, 9999999999)),
                unit_id=unit.id,
                move_in_date=move_in.strftime('%Y-%m-%d'),                      
                move_out_date=move_out.strftime('%Y-%m-%d') if move_out else None,
            )
            tenant.save()
            tenants.append(tenant)

            if move_out is None:
                break  # Exit the loop if the tenant has no move-out date

            days_vacant = random.randint(15, 60)
            move_in = move_out + timedelta(days=days_vacant)

    print("Seeding payment table...")

    approved_methods = ["check", "venmo", "zelle", "cash"]

    payments = []

    for tenant in tenants:
        unit = Unit.find_by_id(tenant.unit_id)

        pmt_start_date = datetime.strptime(tenant.move_in_date, '%Y-%m-%d')
        pmt_stop_date = datetime.strptime(tenant.move_out_date, '%Y-%m-%d') if tenant.move_out_date else datetime.now()
        preferred_pmt_method = random.choice(approved_methods)

        pmt_date = pmt_start_date

        while pmt_date <= pmt_stop_date:
            if pmt_date == pmt_start_date:
                payment = Payment(
                    amount=unit.monthly_rent,
                    pmt_date=pmt_date.strftime('%Y-%m-%d'),
                    method=preferred_pmt_method,
                    tenant_id=tenant.id,                
                    pmt_type="security deposit",
                )
                payment.save()
                payments.append(payment)

            payment = Payment(
                amount=monthly_rent,
                pmt_date=pmt_date.strftime('%Y-%m-%d'),
                method=preferred_pmt_method,
                tenant_id=tenant.id,                
                pmt_type="rent",
            )
            payment.save()
            payments.append(payment)

            pmt_date += relativedelta(months=1)

    print("Seeding complete!")
