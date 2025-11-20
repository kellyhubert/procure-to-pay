# Procure-to-Pay System

A mini "Procure-to-Pay" system with REST APIs using Django + Django REST Framework, featuring multi-level approval workflows, AI-powered document processing, and automated purchase order generation.

## Features

- **Multi-level Approval Workflow**: Purchase requests require approval from Level 1 and Level 2 approvers
- **Role-Based Access Control**: Staff, Approver (Level 1 & 2), and Finance roles
- **AI-Powered Document Processing**:
  - Automatic extraction of data from proforma invoices using OCR and OpenAI
  - Automatic PO generation upon final approval
  - Receipt validation against purchase orders with discrepancy detection
- **REST API**: Full-featured API with JWT authentication
- **Swagger Documentation**: Interactive API documentation
- **Dockerized**: Easy deployment with Docker and Docker Compose

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Document Processing**: pdfplumber, pytesseract, OpenAI API
- **Containerization**: Docker, Docker Compose
- **API Documentation**: drf-yasg (Swagger/OpenAPI)

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (optional, for AI features)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/kellyhubert/procure-to-pay.git
   cd procure-to-pay
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OPENAI_API_KEY
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8000/api/
   - Swagger Documentation: http://localhost:8000/swagger/
   - Admin Panel: http://localhost:8000/admin/
   - Default superuser: `admin` / `admin123`

### Manual Setup (Without Docker)

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   ```bash
   createdb procure_to_pay
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and OpenAI credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/users/register/` - Register new user
- `GET /api/users/me/` - Get current user info

### Purchase Requests
- `POST /api/requests/` - Create new request (Staff)
- `GET /api/requests/` - List requests (filtered by role)
- `GET /api/requests/{id}/` - Get request details
- `PUT /api/requests/{id}/` - Update pending request (Staff)
- `PATCH /api/requests/{id}/approve/` - Approve request (Approver)
- `PATCH /api/requests/{id}/reject/` - Reject request (Approver)
- `POST /api/requests/{id}/submit_receipt/` - Submit receipt (Staff)

### Approvals
- `GET /api/approvals/` - List approvals for current user

## User Roles

1. **Staff**
   - Create purchase requests
   - Upload proforma documents
   - View and edit own pending requests
   - Submit receipts for approved requests

2. **Approver Level 1**
   - View pending requests
   - Approve or reject requests
   - View approval history

3. **Approver Level 2**
   - View pending requests
   - Approve or reject requests
   - View approval history

4. **Finance**
   - View all requests
   - Access complete system data

## Workflow

1. **Staff** creates a purchase request and uploads a proforma invoice
2. System extracts data from the proforma using AI (vendor, items, prices)
3. **Approver Level 1** reviews and approves/rejects the request
4. **Approver Level 2** reviews and approves/rejects the request
5. If both approve, system automatically generates a Purchase Order
6. **Staff** uploads receipt after purchase
7. System validates receipt against PO and flags any discrepancies

## Project Structure

```
procure-to-pay/
├── backend/
│   ├── config/              # Django project settings
│   ├── procurement/         # Main app
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # DRF serializers
│   │   ├── permissions.py  # Custom permissions
│   │   ├── utils.py        # Document processing utilities
│   │   └── admin.py        # Admin interface
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
└── README.md
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Shell
```bash
python manage.py shell
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | - |
| `DEBUG` | Debug mode | `True` |
| `DB_NAME` | Database name | `procure_to_pay` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `OPENAI_API_KEY` | OpenAI API key for document processing | - |

## License

This project is for assessment purposes.

## Contact

For questions or issues, please contact: admin@procure2pay.local
