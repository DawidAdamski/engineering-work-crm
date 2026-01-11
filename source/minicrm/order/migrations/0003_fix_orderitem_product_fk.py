# Generated manually to fix OrderItem.product_id FK type
# Migration to change OrderItem.product_id from bigint to uuid
# This is needed because Product.id was changed from BigAutoField to UUIDField

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_remove_order_product_remove_order_quantity_and_more'),
        ('product', '0002_alter_product_id'),  # Product now has UUID id
    ]

    operations = [
        # Drop OrderItem table
        migrations.DeleteModel(
            name='OrderItem',
        ),
        # Recreate OrderItem with correct FK type (uuid)
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
    ]
