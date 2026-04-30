# InvoiceCrafting Invoice - Setup & Installation Guide

A professional invoice and receipt automator for freelancers and tradespeople.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation Steps

### 1. Clone or Extract the Repository

```bash
cd path/to/invoicecrafting_invoice
```

### 2. Create a Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `SECRET_KEY`: Generate a random secret key for session security
- `DATABASE_URL`: Database connection string (default is SQLite)
- Email settings: Configure email service for invoice sending

### 5. Initialize the Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     print("Database initialized!")
>>> exit()
```

### 6. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

### 7. Access the Application

- **URL:** http://localhost:5000
- **Demo Account:** 
  - Email: admin@example.com
  - Password: password123

## Database Setup

### Using SQLite (Default)

No additional setup required. SQLite database will be created automatically as `invoicecrafting.db`.

### Using PostgreSQL (Production)

1. Install PostgreSQL
2. Create a database: `createdb invoicecrafting`
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/invoicecrafting
   ```
4. Install psycopg2: Already in requirements.txt

## Email Configuration

### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Update `.env`:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-character-app-password
   ```

### Other Email Providers

Update `MAIL_SERVER`, `MAIL_PORT`, and credentials in `.env` for your provider.

## Project Structure

```
invoicecrafting_invoice/
├── app.py                 # Main application entry point
├── config.py             # Configuration classes
├── models.py             # Database models
├── forms.py              # WTForms form classes
├── extensions.py         # Flask extensions
├── decorators.py         # Custom decorators
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── Procfile              # Heroku deployment
│
├── routes/               # Blueprint routes
│   ├── auth.py          # Authentication
│   ├── invoices.py      # Invoice management
│   ├── clients.py       # Client management
│   ├── jobs.py          # Job tracking
│   ├── expenses.py      # Expense tracking
│   ├── dashboard.py     # Dashboard
│   └── settings.py      # Settings
│
├── static/              # Static files
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/
│       ├── receipts/
│       └── logos/
│
└── templates/           # Jinja2 templates
    ├── base.html
    ├── auth/
    ├── invoices/
    ├── clients/
    ├── jobs/
    ├── expenses/
    ├── dashboard/
    ├── settings/
    └── errors/
```

## Features

### Invoicing
- Professional PDF invoice generation
- Multiple invoice templates per trade type
- Line item management
- Tax and discount calculations
- Payment tracking
- Email delivery

### Client Management
- Client database
- Contact information
- Invoice history
- Revenue tracking

### Job Tracking
- Project-based invoicing
- Budget tracking
- Job profitability analysis
- Expense linking

### Expense Management
- Receipt uploads
- Expense categorization
- Job linkage
- Mileage tracking

### Dashboard
- Monthly revenue/expense overview
- Top clients by revenue
- Overdue invoices tracking
- Quick statistics

### Settings
- Business profile customization
- Invoice preferences
- User preferences
- Account management

## User Roles

### Free Plan
- 10 invoices per month
- Basic features

### Premium Plan
- Unlimited invoices
- All features
- Priority support

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Invoices
- `GET /invoices/` - List invoices
- `POST /invoices/create` - Create invoice
- `GET /invoices/<id>/edit` - Edit invoice
- `POST /invoices/<id>/send` - Send via email
- `GET /invoices/<id>/pdf` - Download PDF

### Clients
- `GET /clients/` - List clients
- `POST /clients/create` - Create client
- `GET /clients/<id>` - View client

### And more...

## Deployment

### Heroku

1. Create Heroku app: `heroku create app-name`
2. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
3. Set environment variables: `heroku config:set SECRET_KEY=your-key`
4. Deploy: `git push heroku main`

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

Build and run:
```bash
docker build -t invoicecrafting .
docker run -p 5000:5000 invoicecrafting
```

## Troubleshooting

### Database Issues
- Delete `invoicecrafting.db` and reinitialize
- Check DATABASE_URL in `.env`

### Email Not Sending
- Verify SMTP credentials in `.env`
- Check "Less secure apps" setting for Gmail
- Review application logs

### Static Files Not Loading
- Run: `python -m flask --app app collect`
- Check static folder permissions

## Development

### Running Tests

```bash
python -m pytest
```

### Database Migrations (if using Alembic)

```bash
flask db init
flask db migrate -m "Description"
flask db upgrade
```

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions, contact support or file an issue in the repository.

## Security Notes

- Always change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Set `DEBUG=False` in production
- Use HTTPS in production
- Regularly backup your database
- Keep dependencies updated

---

**Version:** 1.0.0  
**Last Updated:** 2024
