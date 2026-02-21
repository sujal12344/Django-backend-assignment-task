# Credit Approval System — Django REST API

A backend REST API for a Credit Approval System built with Django, PostgreSQL, and Docker.

## Tech Stack

- **Backend**: Django 6.0.2 + Django REST Framework
- **Database**: PostgreSQL (Docker) / Supabase (cloud)
- **Containerization**: Docker + Docker Compose
- **Server**: Gunicorn (production)

---

## Quick Start with Docker (Recommended)

**Prerequisites**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

```bash
# Clone the repository
git clone https://github.com/sujal12344/Django-backend-assignment-task.git
cd Django-backend-assignment-task

# Build and run (migrations + data loading happens automatically)
docker-compose up --build
```

API is available at: `http://localhost:8000`

---

## Local Development Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo DATABASE_URL=your_postgresql_url > .env

# Run migrations and load data
python manage.py migrate
python manage.py load_data

# Start server
python manage.py runserver
```

---

## API Endpoints

Base URL: `http://localhost:8000/api`

### 1. Register Customer
```
POST /api/register
```
**Request Body:**
```json
{
  "first_name": "Raj",
  "last_name": "Kumar",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": "9999999999"
}
```
**Response (201):**
```json
{
  "customer_id": 301,
  "name": "Raj Kumar",
  "age": 30,
  "monthly_income": 50000.0,
  "approved_limit": 1800000.0,
  "phone_number": "9999999999"
}
```

---

### 2. Check Loan Eligibility
```
POST /api/check-eligibility
```
**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 15,
  "tenure": 12
}
```
**Response (200):**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 15,
  "corrected_interest_rate": 15,
  "tenure": 12,
  "monthly_installment": 18062.68
}
```

---

### 3. Create Loan
```
POST /api/create-loan
```
**Request Body:**
```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 15,
  "tenure": 12
}
```
**Response (201 if approved, 200 if rejected):**
```json
{
  "loan_id": 91,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 18062.68
}
```

---

### 4. View Loan Details
```
GET /api/view-loan/<loan_id>
```
**Example:** `GET /api/view-loan/5152`

**Response (200):**
```json
{
  "loan_id": 5152,
  "customer": {
    "id": 28,
    "first_name": "Adena",
    "last_name": "Serrano",
    "phone_number": "9169200783",
    "age": 25
  },
  "loan_amount": 200000.0,
  "is_loan_approved": true,
  "interest_rate": 12.39,
  "monthly_installment": 5526.0,
  "tenure": 147
}
```

---

### 5. View All Loans by Customer
```
GET /api/view-loans/<customer_id>
```
**Example:** `GET /api/view-loans/1`

**Response (200):**
```json
[
  {
    "loan_id": 7798,
    "loan_amount": 900000.0,
    "is_loan_approved": true,
    "interest_rate": 17.92,
    "monthly_installment": 39978.0,
    "tenure": 138,
    "emis_paid": 86,
    "repayments_left": 52
  }
]
```

---

## Credit Score Algorithm

| Credit Score | Decision                      |
| ------------ | ----------------------------- |
| > 50         | ✅ Approved at requested rate  |
| 30 – 50      | ✅ Approved only if rate > 12% |
| 10 – 30      | ✅ Approved only if rate > 16% |
| ≤ 10         | ❌ Rejected                    |

Additional checks:
- Current EMIs > 50% of monthly income → Rejected
- Total debt > approved limit → Rejected

---

## Docker Hub

```bash
docker pull sujal12344/credit-approval-system:latest
```

Image: [hub.docker.com/r/sujal12344/credit-approval-system](https://hub.docker.com/r/sujal12344/credit-approval-system)

---

## Project Structure

```
├── credit_system/        # Django project settings
├── loans/                # Main app
│   ├── models.py         # Customer + Loan database models
│   ├── views.py          # API endpoint handlers (5 endpoints)
│   ├── serializers.py    # Request/response validation
│   ├── utils.py          # Credit scoring + EMI calculation
│   ├── urls.py           # URL routing
│   └── management/
│       └── commands/
│           └── load_data.py  # Excel data loader
├── Dockerfile            # Docker image recipe
├── docker-compose.yml    # Multi-container setup (Django + PostgreSQL)
├── entrypoint.sh         # Container startup script
└── requirements.txt      # Python dependencies
```
