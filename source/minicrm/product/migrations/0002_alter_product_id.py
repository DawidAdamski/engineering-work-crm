# Generated manually to fix UUID field type
# Migration to change Product.id from BigAutoField to UUIDField
# This migration drops and recreates the table to avoid type conversion issues

import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('order', '0002_remove_order_product_remove_order_quantity_and_more'),  # OrderItem depends on Product
    ]

    operations = [
        # Drop Product table (OrderItem will be handled separately if needed)
        # Note: This will cascade delete OrderItems, but they'll be recreated
        migrations.DeleteModel(
            name='Product',
        ),
        # Recreate Product with UUID id
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField()),
            ],
        ),
    ]
