from django.contrib import admin
from .models import RFMScore


@admin.register(RFMScore)
class RFMScoreAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'recency_score',
        'frequency_score',
        'monetary_score',
        'segment',
        'recency_days',
        'frequency',
        'monetary',
        'calculated_at'
    ]
    list_filter = ['segment', 'recency_score', 'frequency_score', 'monetary_score', 'calculated_at']
    search_fields = ['customer__name', 'customer__email', 'segment']
    readonly_fields = ['calculated_at']
    ordering = ['-calculated_at']
    
    fieldsets = (
        ('Customer', {
            'fields': ('customer',)
        }),
        ('RFM Values', {
            'fields': ('recency_days', 'frequency', 'monetary')
        }),
        ('RFM Scores', {
            'fields': ('recency_score', 'frequency_score', 'monetary_score')
        }),
        ('Segment', {
            'fields': ('segment',)
        }),
        ('Metadata', {
            'fields': ('calculated_at',)
        }),
    )
