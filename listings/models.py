from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Listing(models.Model):
    """
    Simple Listing model used by the app. Adjust fields as needed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=512, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        indexes = [
            models.Index(fields=['host']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.id})"
    
    
class Payment(models.Model):
    """
    Payment model to store Chapa payment transaction information.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Unique identifier for this payment
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to booking (assuming you have a Booking model)
    booking = models.ForeignKey(
        'Booking', 
        on_delete=models.CASCADE, 
        related_name='payments',
        help_text="Associated booking"
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Payment amount in ETB"
    )
    currency = models.CharField(max_length=3, default='ETB')
    
    # Chapa transaction details
    transaction_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Chapa transaction reference"
    )
    chapa_reference = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Unique reference for Chapa payment"
    )
    
    # Payment status
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    
    # Customer information
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Chapa response data
    checkout_url = models.URLField(null=True, blank=True)
    chapa_response = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['chapa_reference']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payment {self.chapa_reference} - {self.status}"
    
    def is_successful(self):
        """Check if payment was completed successfully"""
        return self.status == 'completed'
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()


class Booking(models.Model):
    """
    Booking model (add this if you don't have it already)
    """
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    
    # Add your booking fields here (property, dates, guests, etc.)
    # For example:
    # property = models.ForeignKey('Property', on_delete=models.CASCADE)
    # check_in = models.DateField()
    # check_out = models.DateField()
    # guests = models.IntegerField()
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=BOOKING_STATUS_CHOICES, 
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.status}"