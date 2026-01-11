from django.db import models
from django.utils import timezone
from customer.models import Customer


class RFMScore(models.Model):
    """
    RFM (Recency, Frequency, Monetary) scores for customer segmentation.
    
    Stores calculated RFM scores and segment assignment for each customer.
    Scores range from 1-5, where 5 is the best performing quintile.
    """
    
    # RFM Segment definitions
    SEGMENT_CHOICES = [
        ('Champions', 'Champions - High value, frequent, recent customers'),
        ('Loyal Customers', 'Loyal Customers - Regular customers with good value'),
        ('Potential Loyalists', 'Potential Loyalists - Recent customers with potential'),
        ('New Customers', 'New Customers - Recent but low frequency/value'),
        ('Promising', 'Promising - Recent customers with moderate value'),
        ('Need Attention', 'Need Attention - Average customers at risk'),
        ('About to Sleep', 'About to Sleep - Low frequency, recent customers'),
        ('At Risk', 'At Risk - Previously frequent, now declining'),
        ('Cannot Lose Them', 'Cannot Lose Them - High value but infrequent'),
        ('Hibernating', 'Hibernating - Low activity, low value'),
        ('Lost', 'Lost - No recent activity, low value'),
    ]
    
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='rfm_score',
        primary_key=True
    )
    
    # Raw RFM values (calculated from orders)
    recency_days = models.IntegerField(
        help_text="Number of days since last order"
    )
    frequency = models.IntegerField(
        help_text="Total number of orders"
    )
    monetary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total monetary value of all orders"
    )
    
    # RFM scores (1-5, where 5 is best)
    recency_score = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Recency score (1-5), 5 = most recent"
    )
    frequency_score = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Frequency score (1-5), 5 = most frequent"
    )
    monetary_score = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Monetary score (1-5), 5 = highest value"
    )
    
    # Segment assignment based on RFM scores
    segment = models.CharField(
        max_length=50,
        choices=SEGMENT_CHOICES,
        help_text="Customer segment based on RFM scores"
    )
    
    # Metadata
    calculated_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when RFM scores were calculated"
    )
    
    class Meta:
        db_table = 'rfm_scores'
        verbose_name = 'RFM Score'
        verbose_name_plural = 'RFM Scores'
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"{self.customer.name} - {self.segment} (R{self.recency_score}F{self.frequency_score}M{self.monetary_score})"
    
    @property
    def rfm_code(self):
        """Returns RFM code as string (e.g., '555', '321')"""
        return f"{self.recency_score}{self.frequency_score}{self.monetary_score}"
