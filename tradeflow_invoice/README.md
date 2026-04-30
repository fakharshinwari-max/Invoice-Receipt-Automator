# InvoiceCrafting Invoice

**The simplest way for tradespeople and freelancers to create professional invoices, auto-categorize receipts into expenses, and see real profit per job.**

## Features

- ✅ Professional invoice creation with trade-specific templates
- ✅ Receipt upload and expense tracking
- ✅ Job/project-based profit calculation
- ✅ Client management
- ✅ Automatic payment reminders
- ✅ PDF invoice generation
- ✅ Email invoicing
- ✅ Dashboard with charts and insights
- ✅ Mobile-first responsive design
- ✅ Dark/Light mode
- ✅ Freemium model (10 free invoices/month)

## Tech Stack

- **Backend**: Python 3.10+ with Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript, Chart.js
- **PDF Generation**: ReportLab
- **Authentication**: Flask-Login with secure password hashing

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd invoicecrafting_invoice
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database and run:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and go to `http://localhost:5000`

### Default Admin Account

For testing purposes, a default admin account is created:
- **Email**: admin@example.com
- **Password**: password123

**⚠️ Change this immediately in production!**

## Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///invoicecrafting.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Database Setup

For production with PostgreSQL:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Set DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/invoicecrafting_db
```

## Deployment

### Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables from `.env.example`

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create invoicecrafting-invoice

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Open app
heroku open
```

### Deploy with Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads/receipts static/uploads/logos

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Project Structure

```
invoicecrafting_invoice/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── models.py              # SQLAlchemy database models
├── forms.py               # WTForms form classes
├── extensions.py          # Flask extensions initialization
├── utils.py               # Helper functions (PDF, email, etc.)
├── decorators.py          # Custom decorators
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── dashboard.py      # Dashboard routes
│   ├── invoices.py       # Invoice CRUD routes
│   ├── clients.py        # Client management routes
│   ├── expenses.py       # Expense tracking routes
│   ├── jobs.py           # Job/project routes
│   └── settings.py       # Settings routes
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── features.html     # Features page
│   ├── pricing.html      # Pricing page
│   ├── auth/             # Auth templates
│   ├── dashboard/        # Dashboard templates
│   ├── invoices/         # Invoice templates
│   ├── clients/          # Client templates
│   ├── expenses/         # Expense templates
│   ├── jobs/             # Job templates
│   ├── settings/         # Settings templates
│   └── errors/           # Error pages
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── uploads/          # User uploads
└── tests/
    └── test_app.py       # Test cases
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Invoices
- `GET /invoices` - List all invoices
- `POST /invoices/create` - Create new invoice
- `GET /invoices/<id>` - View invoice
- `PUT /invoices/<id>/edit` - Update invoice
- `DELETE /invoices/<id>` - Delete invoice
- `GET /invoices/<id>/pdf` - Download PDF
- `POST /invoices/<id>/send` - Send via email

### Expenses
- `GET /expenses` - List all expenses
- `POST /expenses/create` - Create new expense
- `POST /expenses/upload-receipt` - Upload receipt(s)
- `GET /expenses/export` - Export to CSV

### Dashboard
- `GET /dashboard` - Main dashboard
- `GET /api/stats` - Get statistics (JSON)
- `GET /api/monthly-data` - Get chart data (JSON)

## Freemium Model

### Free Tier
- Up to 10 invoices per month
- Basic features included
- Perfect for getting started

### Premium ($9/month)
- Unlimited invoices
- Advanced reporting
- Priority support
- Custom branding
- Auto-reminders

## Security Features

- ✅ Password hashing with Werkzeug
- ✅ CSRF protection with Flask-WTF
- ✅ Secure file upload validation
- ✅ SQL injection prevention with SQLAlchemy ORM
- ✅ XSS protection with template escaping
- ✅ Session security with Flask-Login

## Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=.
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For support, email support@invoicecrafting.invoice or open an issue in the repository.

## Changelog

### Version 1.0.0 (2026)
- Initial release
- Invoice creation and management
- Expense tracking with receipt upload
- Job-based profit calculation
- Client management
- Dashboard with charts
- Email notifications
- PDF generation
- Mobile-responsive design

---

Built with ❤️ for tradespeople and freelancers everywhere.
