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

- **Frontend**: React 19.2, React Router 7.9, Axios, Vite
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
   - **Frontend:** http://localhost:5173
   - **API:** http://localhost:8000/api/
   - **Swagger Documentation:** http://localhost:8000/swagger/
   - **Django Admin Panel:** http://localhost:8000/admin/
   - **Default superuser:** `admin` / `admin123`

5. **Create users with different roles (via Django Admin)**
   - Go to http://localhost:8000/admin/
   - Login with `admin` / `admin123`
   - Click on **"Users"** → **"Add User"**
   - Create test users with roles:
     - **Staff:** Can create purchase requests
     - **Approver Level 1:** Can approve/reject requests (first level)
     - **Approver Level 2:** Can approve/reject requests (final level)
     - **Finance:** Can view all requests and data

### Manual Setup (Without Docker)

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows: venv\Scripts\activate
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

8. **Run frontend (in a separate terminal)**
   ```bash
   cd frontend
   npm install
   npm run dev
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

## User Management

### Creating Users with Different Roles

To test the complete workflow, you need to create users with different roles:

1. **Access Django Admin Panel**
   - URL: http://localhost:8000/admin/
   - Login: `admin` / `admin123`

2. **Add a New User**
   - Navigate to **"Users"** section
   - Click **"Add User"** button
   - Enter username and password
   - Click **"Save and continue editing"**

3. **Assign Role**
   - Scroll down to find the **"Role"** dropdown
   - Select one of:
     - `Staff` - For purchase request creators
     - `Approver Level 1` - For first-level approvers
     - `Approver Level 2` - For second-level approvers
     - `Finance` - For finance team oversight
   - Optionally set Department, Phone, Email
   - Click **"Save"**

4. **Test Login**
   - Go to http://localhost:5173
   - Login with the new user credentials
   - The dashboard will show features based on the assigned role

### Example Test Users

Create these users for complete workflow testing:

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| john_staff | password123 | Staff | Create purchase requests |
| mary_l1 | password123 | Approver Level 1 | First approval |
| bob_l2 | password123 | Approver Level 2 | Final approval |
| finance_user | password123 | Finance | View all data |

## User Roles & Permissions

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
   - Approve or reject requests (final approval triggers PO generation)
   - View approval history

4. **Finance**
   - View all requests
   - Access complete system data
   - Monitor entire workflow

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

## Deployment to Render

This project is configured for easy deployment to Render.com using the included `render.yaml` file.

### Prerequisites

1. GitHub account with this repository
2. Render account (sign up at https://render.com)
3. OpenAI API key (optional, for AI features)

### Deployment

5. **Access Application**
   - Frontend: `https://procure-to-pay-frontend.onrender.com`
   - Backend API: `https://procure-to-pay-backend.onrender.com/api/`
   - Swagger Docs: `https://procure-to-pay-backend.onrender.com/swagger/`

6. **Create Users via Django Admin**
   - Access: `https://procure-to-pay-backend-gzky.onrender.com/admin/`
   - Default superuser: `admin` / `admin123`
   - Create test users with different roles (Staff, Approver L1, Approver L2, Finance)


### Updating Your Deployment

After making code changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy your services.

### Troubleshooting

**Backend not starting:**
- Check logs in Render dashboard
- Verify DATABASE_URL is set correctly
- Ensure all dependencies are in requirements.txt

**Frontend not loading:**
- Check that VITE_API_URL environment variable is set correctly
- Verify build completed successfully in Render logs

**Database connection issues:**
- Ensure backend service has DATABASE_URL from database
- Check database service is running

## License

This project is for assessment purposes.

## Contact

For questions or issues, please contact: admin@procure2pay.local
