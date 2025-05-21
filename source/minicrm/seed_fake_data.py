import os
import django
import random
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minicrm.settings')
django.setup()

from customer.models import Customer
from product.models import Product
from order.models import Order, OrderItem

fake = Faker()

def seed_customers(n=10):
    for _ in range(n):
        Customer.objects.create(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.msisdn()[0:10],
            address=fake.address()
        )

def seed_products(n=10):
    for _ in range(n):
        name = fake.word().capitalize()
        description = fake.sentence()
        price = round(random.uniform(5, 100), 2)
        stock = random.randint(50, 1000)

        print(f"[DEBUG] name={name}, price={price}, stock={stock}")
        
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock
        )


def seed_orders(n=20):
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    for _ in range(n):
        customer = random.choice(customers)
        order = Order.objects.create(
            customer=customer,
            status=random.choice(['new', 'pending', 'shipped', 'delivered']),
        )

        total = 0
        items = random.sample(products, k=random.randint(1, 4))
        for product in items:
            quantity = random.randint(1, 5)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            total += product.price * quantity

        order.total_price = total
        order.save()

def run():
    print("Seeding data...")
    seed_customers(10)
    seed_products(10)
    seed_orders(20)
    print("Done.")

if __name__ == "__main__":
    run()
