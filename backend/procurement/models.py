from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('approver-level-1', 'Approver Level 1'),
        ('approver-level-2', 'Approver Level 2'),
        ('finance', 'Finance'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        db_table = 'users'


class PurchaseRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Document fields
    proforma = models.FileField(upload_to='proformas/', null=True, blank=True)
    proforma_data = models.JSONField(null=True, blank=True, help_text='Extracted data from proforma')

    purchase_order = models.FileField(upload_to='purchase_orders/', null=True, blank=True)
    purchase_order_data = models.JSONField(null=True, blank=True, help_text='Generated PO data')

    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    receipt_data = models.JSONField(null=True, blank=True, help_text='Extracted data from receipt')
    receipt_validation = models.JSONField(null=True, blank=True, help_text='Receipt validation results')

    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

    def save(self, *args, **kwargs):
        # Prevent status changes if already approved or rejected
        if self.pk:
            old_instance = PurchaseRequest.objects.get(pk=self.pk)
            if old_instance.status in ['approved', 'rejected'] and old_instance.status != self.status:
                raise ValidationError("Cannot change status of approved or rejected requests")
        super().save(*args, **kwargs)

    def can_be_edited_by(self, user):
        return self.created_by == user and self.status == 'pending'

    def get_required_approval_levels(self):
        return ['approver-level-1', 'approver-level-2']

    def check_approval_status(self):
        required_levels = self.get_required_approval_levels()
        approved_levels = self.approvals.filter(approved=True).values_list('approver__role', flat=True)

        if all(level in approved_levels for level in required_levels):
            self.status = 'approved'
            self.save()
            return True
        return False

    class Meta:
        db_table = 'purchase_requests'
        ordering = ['-created_at']


class Approval(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals_given')
    approved = models.BooleanField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'approvals'
        unique_together = ('purchase_request', 'approver')
        ordering = ['approved_at']

    def __str__(self):
        status = 'Approved' if self.approved else 'Rejected' if self.approved == False else 'Pending'
        return f"{self.purchase_request.title} - {self.approver.username} - {status}"
