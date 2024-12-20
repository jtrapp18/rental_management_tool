import random

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker
from unit import Unit
from tenant import Tenant
from payment import Payment

if __name__ == "__main__":

    print("Resetting tables...")

    Unit.drop_table()
    Tenant.drop_table()
    Payment.drop_table()

    Unit.create_table()
    Tenant.create_table()
    Payment.create_table()

    print("Creating constants...")

    fake = Faker()

    print("Seeding unit table...")

    units = []

    for _ in range(5):
        monthly_rent = random.randint(1800 // 50, 3500 // 50) * 50
        
        unit = Unit(
            address=fake.address(),
            monthly_rent=float(monthly_rent),
            late_fee=150,
        )
        unit.save()
        units.append(unit)

    print("Seeding tenant table...")

    tenants = []

    for unit in units:
        setback = random.randint(5 * 365, 10 * 365)
        move_in = datetime.now() - timedelta(days=setback)

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
        unit_info = tenant.unit_information()

        pmt_start_date = datetime.strptime(tenant.move_in_date, '%Y-%m-%d')
        pmt_stop_date = datetime.strptime(tenant.move_out_date, '%Y-%m-%d') if tenant.move_out_date else datetime.now()
        monthly_rent = unit_info[2]
        preferred_pmt_method = random.choice(approved_methods)

        pmt_date = pmt_start_date

        while pmt_date <= pmt_stop_date:
            if pmt_date == pmt_start_date:
                payment = Payment(
                    amount=monthly_rent,
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
