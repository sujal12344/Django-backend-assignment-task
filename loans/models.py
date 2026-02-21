from datetime import datetime

from django.core.validators import MinValueValidator
from django.db import models


class Customer(models.Model):
    """Customer model to store customer information"""

    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18)])
    phone_number = models.CharField(max_length=20, unique=True)
    monthly_income = models.FloatField(validators=[MinValueValidator(0)])
    approved_limit = models.FloatField(validators=[MinValueValidator(0)])
    current_debt = models.FloatField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["customer_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer_id} - {self.first_name} {self.last_name}"

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def total_emis_for_month(self) -> float:
        """Calculate total EMIs due for current month"""
        loans = Loan.objects.filter(customer=self, end_date__gte=datetime.now().date())
        return sum(loan.monthly_installment for loan in loans)


class Loan(models.Model):
    """Loan model to store loan records"""

    APPROVAL_STATUS = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("pending", "Pending"),
    ]

    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField(validators=[MinValueValidator(0)])
    tenure = models.IntegerField(validators=[MinValueValidator(1)])  # in months
    interest_rate = models.FloatField(validators=[MinValueValidator(0)])
    monthly_installment = models.FloatField(
        default=0, validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default="pending")
    emis_paid = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["loan_id"]),
        ]

    def __str__(self) -> str:
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"

    @property
    def repayments_left(self) -> int:
        """Calculate remaining EMIs"""
        return max(0, self.tenure - self.emis_paid)

    @property
    def is_active(self) -> bool:
        """Check if loan is still active"""
        return self.status == "approved" and self.repayments_left > 0
