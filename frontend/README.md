# Procure-to-Pay Frontend

React frontend application for the Procure-to-Pay system.

## Features

- **Authentication**: JWT-based login system
- **Role-based UI**: Different views for Staff, Approvers (Level 1 & 2), and Finance
- **Purchase Requests**: Create, view, and manage purchase requests
- **File Upload**: Upload proforma invoices and receipts
- **Approval Workflow**: Approve/reject requests with comments
- **Receipt Validation**: View AI-powered validation results

## Tech Stack

- React 19.2
- React Router 7.9
- Axios for API calls
- Vite for build tooling
- CSS3 (no external UI libraries for simplicity)

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at http://localhost:5173

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000/api
```

For production, update with your backend URL.

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Project Structure

```
src/
├── components/        # Reusable components
│   └── RequestList.jsx
├── contexts/          # React contexts
│   └── AuthContext.jsx
├── pages/             # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── RequestForm.jsx
│   └── RequestDetail.jsx
├── services/          # API services
│   └── api.js
├── utils/             # Utility functions
├── App.jsx            # Main app component
└── main.jsx           # Entry point
```

## Available Routes

- `/login` - Login page
- `/dashboard` - Main dashboard (role-based)
- `/requests/new` - Create new request (Staff only)
- `/requests/:id` - View request details

## User Roles & Permissions

### Staff
- Create purchase requests with file uploads
- View and edit own pending requests
- Submit receipts for approved requests

### Approver Level 1
- View all pending requests
- Approve/reject requests
- View approval history

### Approver Level 2
- View all pending requests
- Approve/reject requests
- View approval history

### Finance
- View all requests
- Full access to system data

## Demo Account

After backend setup, use:
- Username: `admin`
- Password: `admin123`

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## License

This project is for assessment purposes.
