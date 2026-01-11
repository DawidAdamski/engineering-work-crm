# RFM Analysis Module

This module implements classical RFM (Recency, Frequency, Monetary) analysis for customer segmentation.

## Overview

The RFM module provides:
- **Model**: `RFMScore` - stores calculated RFM scores and segments
- **SQL Query**: Uses CTEs and NTILE(5) for quantile-based scoring
- **API Endpoints**: RESTful API for accessing RFM scores
- **Management Command**: `calculate_rfm` for batch calculation

## Model

The `RFMScore` model stores:
- Raw RFM values: `recency_days`, `frequency`, `monetary`
- RFM scores (1-5): `recency_score`, `frequency_score`, `monetary_score`
- Segment assignment: e.g., 'Champions', 'At Risk', 'Lost'
- Metadata: `calculated_at` timestamp

## SQL Query

The RFM calculation uses a SQL query with:
1. **CTE `customer_orders`**: Calculates raw RFM values
   - Recency: days since last order
   - Frequency: total number of orders
   - Monetary: total value of all orders

2. **CTE `rfm_with_scores`**: Assigns quintile-based scores (1-5)
   - Uses `NTILE(5) OVER (ORDER BY ...)` window function
   - Recency: lower days = better (reversed order)
   - Frequency: higher = better
   - Monetary: higher = better

3. **Final SELECT**: Assigns segment labels based on RFM score combinations

## API Endpoints

### List RFM Scores
```
GET /api/rfm/
```

### Get RFM Score by Customer
```
GET /api/rfm/{customer_id}/
```

### Calculate RFM Scores
```
POST /api/rfm/calculate/
```

### Get Statistics
```
GET /api/rfm/statistics/
```

### Get by Segment
```
GET /api/rfm/by-segment/
```

## Management Command

Calculate RFM scores for all customers:

```bash
python manage.py calculate_rfm
```

With verbose output:

```bash
python manage.py calculate_rfm --verbose
```

Dry run (show what would be calculated):

```bash
python manage.py calculate_rfm --dry-run
```

## Segments

The module assigns customers to one of the following segments:

- **Champions**: R=5, F=5, M=5 - High value, frequent, recent customers
- **Loyal Customers**: R=4-5, F=4-5, M=3-5 - Regular customers with good value
- **Potential Loyalists**: R=4-5, F=1-3, M=1-3 - Recent customers with potential
- **New Customers**: R=4-5, F=1, M=1-2 - Recent but low frequency/value
- **Promising**: R=4-5, F=1, M=3-5 - Recent customers with moderate value
- **Need Attention**: R=3, F=3, M=3 - Average customers at risk
- **About to Sleep**: R=3, F=1-2, M=1-2 - Low frequency, recent customers
- **At Risk**: R=1-2, F=4-5, M=3-5 - Previously frequent, now declining
- **Cannot Lose Them**: R=1-2, F=1-2, M=4-5 - High value but infrequent
- **Hibernating**: R=1-2, F=1-2, M=1-3 - Low activity, low value
- **Lost**: R=1, F=1, M=1 - No recent activity, low value

## Usage Example

1. Generate customer and order data
2. Run RFM calculation:
   ```bash
   python manage.py calculate_rfm
   ```
3. Access results via API:
   ```bash
   curl http://localhost:8000/api/rfm/
   ```
4. Or use Django admin to view RFM scores

## Database Migration

After creating the model, run migrations:

```bash
python manage.py makemigrations rfm
python manage.py migrate
```
