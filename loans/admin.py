from django.contrib import admin

from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "customer_id",
        "first_name",
        "last_name",
        "phone_number",
        "monthly_income",
        "approved_limit",
        "current_debt",
    ]
    list_filter = ["created_at", "approved_limit"]
    search_fields = ["first_name", "last_name", "phone_number", "customer_id"]
    readonly_fields = ["customer_id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "customer_id",
                    "first_name",
                    "last_name",
                    "age",
                    "phone_number",
                )
            },
        ),
        (
            "Financial Info",
            {"fields": ("monthly_income", "approved_limit", "current_debt")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        "loan_id",
        "customer",
        "loan_amount",
        "interest_rate",
        "tenure",
        "status",
        "monthly_installment",
    ]
    list_filter = ["status", "created_at", "interest_rate"]
    search_fields = [
        "loan_id",
        "customer__first_name",
        "customer__last_name",
        "customer__phone_number",
    ]
    readonly_fields = ["loan_id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Loan Info",
            {
                "fields": (
                    "loan_id",
                    "customer",
                    "loan_amount",
                    "tenure",
                    "interest_rate",
                )
            },
        ),
        (
            "Payment Info",
            {
                "fields": (
                    "monthly_installment",
                    "emis_paid",
                    "status",
                    "repayments_left",
                )
            },
        ),
        ("Dates", {"fields": ("start_date", "end_date")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
