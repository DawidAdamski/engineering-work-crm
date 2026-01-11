# Synthetic Data Generation Scripts

## Overview

Scripts for generating synthetic customer and order data for RFM analysis testing.

## seed_fake_data.py

Generates realistic customer data based on predefined personas with Gaussian distribution.

### Personas

The script generates customers based on 5 personas:

1. **Champions** (100 customers)
   - High frequency, high monetary value
   - Recent purchases
   
2. **Loyal Customers** (150 customers)
   - Consistent frequency, average monetary value
   - Regular purchases

3. **New Customers** (100 customers)
   - High recency, low frequency and monetary value
   - Recent but infrequent purchases

4. **At-Risk Customers** (80 customers)
   - Previously high frequency, now low recency
   - Declining engagement

5. **Lapsed Customers** (70 customers)
   - Low scores across all dimensions
   - Inactive customers

### Usage

```bash
cd source/minicrm
python ../scripts/seed_fake_data.py
```

With custom parameters:

```bash
python ../scripts/seed_fake_data.py --customers 1000 --days 365
```

### Parameters

- `--customers`: Total number of customers (default: 500)
- `--days`: Date range in days (default: 730 = 2 years)
- `--verbose`: Enable verbose output

## Table 4.1: Synthetic Data Generation Parameters

| Persona | Count | Frequency (orders/year) | Monetary (value/year) | Recency (days) |
|:--------|:-----:|:------------------------:|:---------------------:|:--------------:|
|         |       | Mean | Std | Mean | Std | Mean | Std |
| Champions | 100 | 12 | 3 | 5000 | 1500 | 15 | 10 |
| Loyal Customers | 150 | 8 | 2 | 2000 | 500 | 30 | 15 |
| New Customers | 100 | 2 | 1 | 500 | 200 | 5 | 3 |
| At-Risk Customers | 80 | 10 | 3 | 3000 | 1000 | 120 | 30 |
| Lapsed Customers | 70 | 1 | 1 | 200 | 100 | 200 | 50 |
| **Total** | **500** | - | - | - | - | - | - |

**Date Range**: 730 days (~2 years)

**Distribution**: Gaussian (normal) distribution with mean and standard deviation as specified.

## Output

The script generates:
- Customers with realistic names, emails, phones, addresses
- Products (20 default)
- Orders distributed over time according to persona characteristics
- Order items with quantities

## Next Steps

After generating data:

1. Calculate RFM scores:
   ```bash
   python manage.py calculate_rfm
   ```

2. Check results via API:
   ```bash
   curl http://localhost:8000/api/rfm/
   ```

3. View in Django admin:
   ```
   http://localhost:8000/admin/
   ```
