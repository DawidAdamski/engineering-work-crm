"""
SQL queries for RFM (Recency, Frequency, Monetary) analysis.

This module contains the SQL query used to calculate RFM scores
using Common Table Expressions (CTEs) and NTILE window function
for quantile-based scoring.
"""

RFM_CALCULATION_QUERY = """
WITH customer_orders AS (
    -- Calculate raw RFM values for each customer
    SELECT
        c.id AS customer_id,
        -- Recency: days since last order (NULL if no orders = very old)
        COALESCE(
            EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(o.order_date))) / 86400,
            9999
        )::INTEGER AS recency_days,
        -- Frequency: total number of orders
        COUNT(o.id) AS frequency,
        -- Monetary: total value of all orders
        COALESCE(SUM(o.total_price), 0) AS monetary
    FROM customer_customer c
    LEFT JOIN order_order o ON o.customer_id = c.id
    GROUP BY c.id
),
rfm_with_scores AS (
    -- Calculate quintile-based scores (1-5) using NTILE
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        -- Recency: lower days = better, so we reverse the order
        -- NTILE(5) assigns 1 to lowest values, 5 to highest
        -- For recency, we want 5 for most recent (lowest days)
        -- So we order by recency_days ASC (lowest first)
        6 - NTILE(5) OVER (ORDER BY recency_days ASC) AS recency_score,
        -- Frequency: higher = better, order by DESC
        NTILE(5) OVER (ORDER BY frequency DESC) AS frequency_score,
        -- Monetary: higher = better, order by DESC
        NTILE(5) OVER (ORDER BY monetary DESC) AS monetary_score
    FROM customer_orders
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    -- Segment assignment based on RFM scores
    CASE
        -- Champions: R=5, F=5, M=5
        WHEN recency_score = 5 AND frequency_score = 5 AND monetary_score = 5 THEN 'Champions'
        -- Loyal Customers: R=4-5, F=4-5, M=3-5
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 3 THEN 'Loyal Customers'
        -- Potential Loyalists: R=4-5, F=1-3, M=1-3
        WHEN recency_score >= 4 AND frequency_score <= 3 AND monetary_score <= 3 THEN 'Potential Loyalists'
        -- New Customers: R=4-5, F=1, M=1-2
        WHEN recency_score >= 4 AND frequency_score = 1 AND monetary_score <= 2 THEN 'New Customers'
        -- Promising: R=4-5, F=1, M=3-5
        WHEN recency_score >= 4 AND frequency_score = 1 AND monetary_score >= 3 THEN 'Promising'
        -- Need Attention: R=3, F=3, M=3
        WHEN recency_score = 3 AND frequency_score = 3 AND monetary_score = 3 THEN 'Need Attention'
        -- About to Sleep: R=3, F=1-2, M=1-2
        WHEN recency_score = 3 AND frequency_score <= 2 AND monetary_score <= 2 THEN 'About to Sleep'
        -- At Risk: R=1-2, F=4-5, M=3-5
        WHEN recency_score <= 2 AND frequency_score >= 4 AND monetary_score >= 3 THEN 'At Risk'
        -- Cannot Lose Them: R=1-2, F=1-2, M=4-5
        WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 4 THEN 'Cannot Lose Them'
        -- Hibernating: R=1-2, F=1-2, M=1-3
        WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score <= 3 THEN 'Hibernating'
        -- Lost: R=1, F=1, M=1
        WHEN recency_score = 1 AND frequency_score = 1 AND monetary_score = 1 THEN 'Lost'
        -- Default: Need Attention
        ELSE 'Need Attention'
    END AS segment
FROM rfm_with_scores
ORDER BY customer_id;
"""


def get_rfm_calculation_query():
    """
    Returns the SQL query for RFM calculation.
    
    This query:
    1. Calculates raw RFM values (recency_days, frequency, monetary) using CTEs
    2. Assigns quintile-based scores (1-5) using NTILE window function
    3. Assigns segment labels based on RFM score combinations
    
    Returns:
        str: SQL query string
    """
    return RFM_CALCULATION_QUERY
