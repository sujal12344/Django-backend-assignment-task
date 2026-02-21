from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Avg

from .models import Customer, Loan


def calculate_monthly_installment(
    principal: float, annual_interest_rate: float, tenure_months: int
) -> float:
    """
    Calculate monthly EMI using compound interest formula
    EMI = P * [r(1+r)^n] / [(1+r)^n - 1]
    where:
    P = Principal (loan amount)
    r = Monthly interest rate (annual_rate / 12 / 100)
    n = Tenure in months
    """
    if tenure_months == 0 or annual_interest_rate == 0:
        return principal / tenure_months if tenure_months > 0 else 0

    monthly_rate = (annual_interest_rate / 12) / 100
    numerator = principal * (monthly_rate * (1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1

    if denominator == 0:
        return principal / tenure_months

    return numerator / denominator


def calculate_credit_score(customer: Customer) -> float:
    """
    Calculate credit score (0-100) based on historical loan data
    Components:
    1. Past loans paid on time (25 points)
    2. Number of loans taken in past (20 points)
    3. Loan activity in current year (20 points)
    4. Loan approved volume (20 points)
    5. Exceeding approved limit (automatic 0 score)
    """
    # Get customer's past loans
    past_loans = Loan.objects.filter(
        customer=customer, status="approved", end_date__lt=datetime.now().date()
    )

    # Get current active loans
    current_loans = Loan.objects.filter(
        customer=customer, status="approved", end_date__gte=datetime.now().date()
    )

    # Check if current debt exceeds approved limit
    total_current_debt = sum(loan.loan_amount for loan in current_loans)
    if total_current_debt > customer.approved_limit:
        return 0

    score = 0.0

    # 1. Past loans paid on time (25 points)
    if past_loans.exists():
        first_loan = past_loans.first()
        if first_loan and first_loan.tenure > 0:
            emis_paid_on_time = past_loans.filter(emis_paid=first_loan.tenure).count()
            score += (emis_paid_on_time / past_loans.count()) * 25

    # 2. Number of loans taken in past (20 points)
    # More loans = better history (max 20 points for 5+ loans)
    num_past_loans = past_loans.count()
    score += min(20, (num_past_loans / 5) * 20)

    # 3. Loan activity in current year (20 points)
    current_year_start = datetime(datetime.now().year, 1, 1).date()
    current_year_loans = past_loans.filter(start_date__gte=current_year_start).count()
    score += min(20, (current_year_loans / 3) * 20)

    # 4. Loan approved volume (20 points)
    # Higher approved amounts = higher score
    if past_loans.exists():
        avg_loan_amount = past_loans.aggregate(avg=Avg("loan_amount"))["avg"] or 0
        # Normalize to approved limit
        if customer.approved_limit > 0:
            score += min(20, (avg_loan_amount / customer.approved_limit) * 20)

    return min(100, score)


def check_loan_eligibility(
    customer: Customer, loan_amount: float, interest_rate: float, tenure: int
) -> tuple[bool, float, float, float]:
    """
    Check loan eligibility based on credit score and other factors
    Returns: (is_eligible, corrected_rate, monthly_emi, credit_score)
    """
    # Calculate credit score
    credit_score = calculate_credit_score(customer)

    # Check if sum of current EMIs exceeds 50% of monthly salary
    current_emis_sum = customer.total_emis_for_month
    if current_emis_sum > (customer.monthly_income * 0.5):
        return False, interest_rate, 0, credit_score

    # Check if requested loan + current debt exceeds approved limit
    active_loans = Loan.objects.filter(
        customer=customer, status="approved", end_date__gte=datetime.now().date()
    )
    total_debt = sum(loan.loan_amount for loan in active_loans) + loan_amount

    if total_debt > customer.approved_limit:
        return False, interest_rate, 0, credit_score

    # Determine approval and corrected interest rate based on credit score
    is_approved = True
    corrected_rate = interest_rate

    if credit_score > 50:
        # Approve loan as-is
        is_approved = True
        corrected_rate = interest_rate
    elif 50 >= credit_score > 30:
        # Approve only if interest_rate > 12%
        if interest_rate > 12:
            is_approved = True
            corrected_rate = interest_rate
        else:
            is_approved = False
            corrected_rate = 12  # Minimum rate for this slab
    elif 30 >= credit_score > 10:
        # Approve only if interest_rate > 16%
        if interest_rate > 16:
            is_approved = True
            corrected_rate = interest_rate
        else:
            is_approved = False
            corrected_rate = 16  # Minimum rate for this slab
    else:
        # Credit score <= 10: Don't approve
        is_approved = False
        corrected_rate = 16

    # Calculate monthly installment with corrected rate
    if is_approved:
        monthly_emi = calculate_monthly_installment(loan_amount, corrected_rate, tenure)
    else:
        monthly_emi = 0

    return is_approved, corrected_rate, monthly_emi, credit_score
