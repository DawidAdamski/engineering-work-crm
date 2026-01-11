"""
Generate synthetic customer and order data for RFM analysis.

This script generates realistic customer data based on predefined personas
with Gaussian distribution to simulate different purchasing behaviors:
- High-Value Champions: High frequency + high monetary value
- Loyal Customers: Consistent frequency, average monetary value
- New Customers: High recency, low frequency and monetary value
- At-Risk Customers: Previously high frequency, now low recency
- Lapsed Customers: Low scores across all dimensions
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from faker import Faker

# Add the minicrm directory to the Python path
# In container: /app/scripts -> /app/ (where Django app is)
# Locally: source/scripts -> source/minicrm
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(script_dir, '..', 'minicrm')):
    # Local development: source/scripts -> source/minicrm
    sys.path.insert(0, os.path.join(script_dir, '..', 'minicrm'))
else:
    # Container: /app/scripts -> /app/
    sys.path.insert(0, os.path.join(script_dir, '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minicrm.settings')
django.setup()

from customer.models import Customer
from product.models import Product
from order.models import Order, OrderItem

fake = Faker('pl_PL')  # Polish locale for more realistic data

# Configuration parameters
CONFIG = {
    'total_customers': 500,
    'date_range_days': 730,  # 2 years
    'personas': {
        'champions': {
            'count': 100,
            'frequency_mean': 12,  # orders per year
            'frequency_std': 3,
            'monetary_mean': 5000,  # total value per year
            'monetary_std': 1500,
            'recency_mean': 15,  # days since last order
            'recency_std': 10,
        },
        'loyal': {
            'count': 150,
            'frequency_mean': 8,
            'frequency_std': 2,
            'monetary_mean': 2000,
            'monetary_std': 500,
            'recency_mean': 30,
            'recency_std': 15,
        },
        'new': {
            'count': 100,
            'frequency_mean': 2,
            'frequency_std': 1,
            'monetary_mean': 500,
            'monetary_std': 200,
            'recency_mean': 5,
            'recency_std': 3,
        },
        'at_risk': {
            'count': 80,
            'frequency_mean': 10,  # historical high frequency
            'frequency_std': 3,
            'monetary_mean': 3000,
            'monetary_std': 1000,
            'recency_mean': 120,  # low recency (old last order)
            'recency_std': 30,
        },
        'lapsed': {
            'count': 70,
            'frequency_mean': 1,
            'frequency_std': 1,
            'monetary_mean': 200,
            'monetary_std': 100,
            'recency_mean': 200,
            'recency_std': 50,
        },
    }
}


def generate_gaussian_value(mean, std, min_value=0):
    """Generate a value from Gaussian distribution with minimum constraint."""
    value = random.gauss(mean, std)
    return max(min_value, int(round(value)))


def seed_products(n=20):
    """Generate product catalog."""
    print(f"Generating {n} products...")
    products = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + fake.word().capitalize()
        description = fake.sentence()
        price = round(random.uniform(10, 500), 2)
        stock = random.randint(50, 1000)
        
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock
        )
        products.append(product)
    print(f"Created {len(products)} products")
    return products


def generate_orders_for_customer(customer, persona_config, products, end_date):
    """
    Generate orders for a customer based on persona configuration.
    
    Args:
        customer: Customer instance
        persona_config: Dictionary with frequency_mean, monetary_mean, etc.
        products: List of available products
        end_date: End date for order generation
    """
    # Calculate target values from persona
    target_frequency = generate_gaussian_value(
        persona_config['frequency_mean'],
        persona_config['frequency_std'],
        min_value=1
    )
    
    target_monetary = generate_gaussian_value(
        persona_config['monetary_mean'],
        persona_config['monetary_std'],
        min_value=50
    )
    
    # Calculate recency (days since last order)
    target_recency_days = generate_gaussian_value(
        persona_config['recency_mean'],
        persona_config['recency_std'],
        min_value=1
    )
    
    # Calculate last order date
    last_order_date = end_date - timedelta(days=target_recency_days)
    
    # Generate orders spread over time
    # Distribute orders over the date range, with more recent orders for new customers
    if persona_config['recency_mean'] < 30:  # New customers
        # Most orders in recent period
        order_dates = []
        for i in range(target_frequency):
            # Bias towards recent dates
            days_ago = random.randint(0, min(90, target_recency_days + 30))
            order_date = end_date - timedelta(days=days_ago)
            order_dates.append(order_date)
    elif persona_config['recency_mean'] > 100:  # At-risk or lapsed
        # Orders in the past, not recent
        order_dates = []
        for i in range(target_frequency):
            days_ago = random.randint(target_recency_days - 30, target_recency_days + 100)
            order_date = end_date - timedelta(days=days_ago)
            order_dates.append(order_date)
    else:  # Champions, loyal
        # Spread evenly over time
        order_dates = []
        for i in range(target_frequency):
            days_ago = random.randint(0, target_recency_days + 60)
            order_date = end_date - timedelta(days=days_ago)
            order_dates.append(order_date)
    
    # Sort dates and ensure last order matches target recency
    order_dates.sort()
    if order_dates:
        order_dates[-1] = last_order_date
    
    # Calculate average order value
    avg_order_value = target_monetary / max(target_frequency, 1)
    
    # Generate orders
    orders = []
    total_generated = 0
    
    for order_date in order_dates:
        # Create order - we'll set the date after creation
        order = Order(
            customer=customer,
            status=random.choice(['delivered', 'shipped', 'delivered']),  # Mostly completed
            total_price=0
        )
        # Save without date first
        order.save()
        # Then update the date field directly (bypassing auto_now_add)
        Order.objects.filter(id=order.id).update(order_date=order_date)
        order.refresh_from_db()
        
        # Generate order items
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        order_total = 0
        for product in selected_products:
            quantity = random.randint(1, 3)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )
            order_total += product.price * quantity
        
        # Adjust order value to match target monetary (with some variance)
        variance = random.uniform(0.7, 1.3)
        target_order_value = avg_order_value * variance
        
        if order_total < target_order_value:
            # Add more items or increase quantity
            additional_items = random.randint(1, 2)
            for _ in range(additional_items):
                product = random.choice(products)
                quantity = random.randint(1, 2)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
                order_total += product.price * quantity
        
        # Update order total
        order.total_price = round(order_total, 2)
        order.save()
        
        orders.append(order)
        total_generated += order_total
    
    return orders, total_generated


def seed_customers_with_personas(products, end_date):
    """Generate customers based on predefined personas."""
    print("\n=== Generating customers with personas ===")
    
    all_customers = []
    
    for persona_name, persona_config in CONFIG['personas'].items():
        count = persona_config['count']
        print(f"\nGenerating {count} {persona_name} customers...")
        
        for i in range(count):
            customer = Customer.objects.create(
                name=fake.name(),
                email=fake.unique.email(),
                phone=fake.msisdn()[:10],
                address=fake.address()
            )
            
            # Generate orders for this customer
            orders, total_value = generate_orders_for_customer(
                customer, persona_config, products, end_date
            )
            
            all_customers.append({
                'customer': customer,
                'persona': persona_name,
                'orders_count': len(orders),
                'total_value': total_value
            })
            
            if (i + 1) % 20 == 0:
                print(f"  Generated {i + 1}/{count} customers...")
    
    return all_customers


def print_summary(customers_data):
    """Print summary of generated data."""
    print("\n=== Generation Summary ===")
    
    total_customers = len(customers_data)
    total_orders = sum(c['orders_count'] for c in customers_data)
    total_value = sum(c['total_value'] for c in customers_data)
    
    print(f"Total customers: {total_customers}")
    print(f"Total orders: {total_orders}")
    print(f"Total value: {total_value:.2f}")
    
    print("\nBy persona:")
    for persona_name in CONFIG['personas'].keys():
        persona_customers = [c for c in customers_data if c['persona'] == persona_name]
        persona_orders = sum(c['orders_count'] for c in persona_customers)
        persona_value = sum(c['total_value'] for c in persona_customers)
        
        print(f"  {persona_name}:")
        print(f"    Customers: {len(persona_customers)}")
        print(f"    Orders: {persona_orders}")
        print(f"    Total value: {persona_value:.2f}")


def run(total_customers=None, date_range_days=None):
    """
    Main function to generate synthetic data.
    
    Args:
        total_customers: Override total number of customers (optional)
        date_range_days: Override date range in days (optional)
    """
    if total_customers:
        # Adjust persona counts proportionally
        current_total = sum(c['count'] for c in CONFIG['personas'].values())
        ratio = total_customers / current_total
        for persona in CONFIG['personas'].values():
            persona['count'] = int(persona['count'] * ratio)
    
    if date_range_days:
        CONFIG['date_range_days'] = date_range_days
    
    print("=" * 60)
    print("Synthetic Data Generation for RFM Analysis")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Total customers: {sum(c['count'] for c in CONFIG['personas'].values())}")
    print(f"  Date range: {CONFIG['date_range_days']} days (~{CONFIG['date_range_days']/365:.1f} years)")
    print("=" * 60)
    
    # Calculate end date (today) - use timezone-aware datetime
    end_date = timezone.now()
    start_date = end_date - timedelta(days=CONFIG['date_range_days'])
    
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Generate products first
    products = seed_products(20)
    
    # Generate customers with personas
    customers_data = seed_customers_with_personas(products, end_date)
    
    # Print summary
    print_summary(customers_data)
    
    print("\n✅ Data generation completed!")
    print("\nNext steps:")
    print("  1. Calculate RFM scores: python manage.py calculate_rfm")
    print("  2. Check results: GET /api/rfm/")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic customer data for RFM analysis')
    parser.add_argument('--customers', type=int, help='Total number of customers to generate')
    parser.add_argument('--days', type=int, help='Date range in days (default: 730 = 2 years)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    run(
        total_customers=args.customers,
        date_range_days=args.days
    )
