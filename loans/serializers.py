from rest_framework import serializers

from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""

    name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "customer_id",
            "first_name",
            "last_name",
            "name",
            "age",
            "phone_number",
            "monthly_income",
            "approved_limit",
            "current_debt",
        ]
        read_only_fields = ["customer_id", "approved_limit", "current_debt"]

    def get_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Detailed customer serializer with calculated fields"""

    name = serializers.SerializerMethodField()
    total_emis = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "customer_id",
            "name",
            "age",
            "phone_number",
            "monthly_income",
            "approved_limit",
            "current_debt",
            "total_emis",
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_total_emis(self, obj):
        return obj.total_emis_for_month


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model"""

    repayments_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "customer",
            "loan_amount",
            "tenure",
            "interest_rate",
            "monthly_installment",
            "status",
            "emis_paid",
            "start_date",
            "end_date",
            "repayments_left",
        ]
        read_only_fields = ["loan_id", "status", "monthly_installment", "start_date"]


class LoanDetailSerializer(serializers.ModelSerializer):
    """Detailed loan serializer with customer info"""

    customer_details = CustomerDetailSerializer(source="customer", read_only=True)
    repayments_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "customer",
            "customer_details",
            "loan_amount",
            "tenure",
            "interest_rate",
            "monthly_installment",
            "status",
            "emis_paid",
            "start_date",
            "end_date",
            "repayments_left",
        ]
        read_only_fields = ["loan_id", "customer_details", "repayments_left"]


class RegisterCustomerSerializer(serializers.Serializer):
    """Serializer for customer registration"""

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.FloatField(min_value=0)
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        """Validate unique phone number"""
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def create(self, validated_data):
        """Create new customer with calculated approved limit"""
        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = validated_data["monthly_income"] * 36
        # Round to nearest lakh (100,000)
        approved_limit = round(approved_limit / 100000) * 100000

        customer = Customer.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            age=validated_data["age"],
            phone_number=validated_data["phone_number"],
            monthly_income=validated_data["monthly_income"],
            approved_limit=approved_limit,
        )
        return customer


class EligibilityCheckSerializer(serializers.Serializer):
    """Serializer for loan eligibility check"""

    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class EligibilityResponseSerializer(serializers.Serializer):
    """Response serializer for eligibility check"""

    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()


class CreateLoanSerializer(serializers.Serializer):
    """Serializer for creating a new loan"""

    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class CreateLoanResponseSerializer(serializers.Serializer):
    """Response serializer for loan creation"""

    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField(allow_blank=True)
    monthly_installment = serializers.FloatField()
