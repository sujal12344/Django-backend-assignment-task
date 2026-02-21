from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Customer, Loan
from .serializers import (
    CreateLoanSerializer,
    EligibilityCheckSerializer,
    RegisterCustomerSerializer,
)
from .utils import calculate_monthly_installment, check_loan_eligibility


@api_view(["POST"])
def register_customer(request: Request) -> Response:
    """
    Register a new customer
    POST /api/register
    """
    serializer = RegisterCustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer: Customer = serializer.save()  # type: ignore
        return Response(
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "age": customer.age,
                "monthly_income": customer.monthly_income,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def check_eligibility(request: Request) -> Response:
    """
    Check loan eligibility based on credit score
    POST /api/check-eligibility
    """
    serializer = EligibilityCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(customer_id=serializer.validated_data["customer_id"])  # type: ignore
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
        )

    loan_amount = serializer.validated_data["loan_amount"]  # type: ignore
    interest_rate = serializer.validated_data["interest_rate"]  # type: ignore
    tenure = serializer.validated_data["tenure"]  # type: ignore

    # Check eligibility
    is_approved, corrected_rate, monthly_emi, credit_score = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )

    response_data = {
        "customer_id": customer.customer_id,
        "approval": is_approved,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_rate,
        "tenure": tenure,
        "monthly_installment": round(monthly_emi, 2) if monthly_emi > 0 else 0,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_loan(request: Request) -> Response:
    """
    Create a new loan based on eligibility
    POST /api/create-loan
    """
    serializer = CreateLoanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.get(customer_id=serializer.validated_data["customer_id"])  # type: ignore
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
        )

    loan_amount = serializer.validated_data["loan_amount"]  # type: ignore
    interest_rate = serializer.validated_data["interest_rate"]  # type: ignore
    tenure = serializer.validated_data["tenure"]  # type: ignore

    # Check eligibility
    is_approved, corrected_rate, monthly_emi, credit_score = check_loan_eligibility(
        customer, loan_amount, interest_rate, tenure
    )

    if not is_approved:
        return Response(
            {
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan cannot be approved based on credit score and financial criteria.",
                "monthly_installment": 0,
            },
            status=status.HTTP_200_OK,
        )

    # Create the loan
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30 * tenure)

    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_rate,
        monthly_installment=round(monthly_emi, 2),
        status="approved",
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        {
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully",
            "monthly_installment": round(monthly_emi, 2),
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def view_loan(request: Request, loan_id: int) -> Response:
    """
    View loan details with customer information
    GET /api/view-loan/<loan_id>
    """
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    customer = loan.customer
    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "age": customer.age,
        },
        "loan_amount": loan.loan_amount,
        "is_loan_approved": loan.status == "approved",
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_installment,
        "tenure": loan.tenure,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def view_loans_by_customer(request: Request, customer_id: int) -> Response:
    """
    View all loans of a customer
    GET /api/view-loans/<customer_id>
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND
        )

    loans = Loan.objects.filter(customer=customer)
    loans_data = []

    for loan in loans:
        loans_data.append(
            {
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "is_loan_approved": loan.status == "approved",
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "tenure": loan.tenure,
                "emis_paid": loan.emis_paid,
                "repayments_left": loan.repayments_left,
            }
        )

    return Response(loans_data, status=status.HTTP_200_OK)
