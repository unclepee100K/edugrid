from django.db import models
from academics.models import StudentProfile


class FeeStructure(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('ZWL', 'Zimbabwe Gold'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fees')
    term = models.ForeignKey('academics.SchoolTerm', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    description = models.CharField(max_length=200, blank=True)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.student.user.full_name} - {self.term} - {self.amount} {self.currency}"


class FeePayment(models.Model):
    PAYMENT_METHODS = [
        ('ecocash', 'EcoCash'),
        ('swipe', 'Swipe Card'),
        ('cash', 'Cash USD'),
        ('bank', 'Bank Transfer'),
    ]

    fee = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency_paid = models.CharField(max_length=3, choices=FeeStructure.CURRENCY_CHOICES)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=50, blank=True)
    receipt_upload = models.FileField(upload_to='receipts/', blank=True, null=True)
    paid_on = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fee.student.user.full_name} - {self.amount_paid} {self.currency_paid}"v