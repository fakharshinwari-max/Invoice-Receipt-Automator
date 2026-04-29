# TradeFlow Invoice - Complete Project Structure

## Folder Structure
```
tradeflow_invoice/
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration settings
├── models.py               # SQLAlchemy database models
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
├── .env.example           # Environment variables template
├── README.md              # Setup and deployment instructions
├── extensions.py          # Flask extensions initialization
├── forms.py               # WTForms form classes
├── decorators.py          # Custom decorators (freemium limits, etc.)
├── utils.py               # Helper functions (PDF generation, email, etc.)
│
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles + Tailwind utilities
│   ├── js/
│   │   └── main.js        # Main JavaScript functionality
│   └── uploads/
│       ├── receipts/      # Uploaded receipt images/PDFs
│       └── logos/         # Business logo uploads
│
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Landing page
│   ├── pricing.html       # Pricing page
│   ├── features.html      # Features page
│   │
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── forgot_password.html
│   │
│   ├── dashboard/
│   │   └── index.html     # Main dashboard
│   │
│   ├── invoices/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── pdf_template.html
│   │
│   ├── clients/
│   │   ├── list.html
│   │   ├── create.html
│   │   └── view.html
│   │
│   ├── expenses/
│   │   ├── list.html
│   │   ├── create.html
│   │   └── receipt_upload.html
│   │
│   ├── jobs/
│   │   ├── list.html
│   │   ├── create.html
│   │   └── view.html
│   │
│   ├── settings/
│   │   ├── profile.html
│   │   ├── branding.html
│   │   └── preferences.html
│   │
│   └── emails/
│       ├── invoice_email.html
│       └── reminder_email.html
│
└── tests/
    └── test_app.py        # Basic tests
```

## Database Models Overview

### User Model
- id, email, password_hash, created_at
- is_premium, premium_expires_at
- invoice_count_current_month, invoice_limit
- trade_type (plumber, electrician, tutor, etc.)

### BusinessProfile Model
- user_id (FK), business_name, logo_path
- address, phone, tax_id, currency
- default_tax_rate, payment_terms

### Client Model
- id, user_id (FK), name, email, phone, address
- notes, created_at

### Job Model
- id, user_id (FK), client_id (FK)
- name, description, status (active/completed)
- start_date, end_date, budget

### Invoice Model
- id, user_id (FK), client_id (FK), job_id (FK nullable)
- invoice_number, status (draft/sent/paid/overdue)
- issue_date, due_date, paid_date
- subtotal, tax_amount, discount_amount, total
- amount_paid, balance_due
- notes, terms, template_type
- pdf_path, sent_at, reminded_at

### InvoiceItem Model
- id, invoice_id (FK), description
- quantity, unit_price, amount
- tax_rate, discount

### Expense Model
- id, user_id (FK), job_id (FK nullable)
- receipt_path, category (fuel/materials/tools/travel/labor)
- description, amount, date
- vendor, payment_method, notes
- linked_invoice_id (FK nullable)

### Settings Model
- user_id (FK), dark_mode_enabled
- email_notifications, reminder_frequency
- late_fee_percentage, custom_fields

### ActivityLog Model
- id, user_id (FK), action, timestamp
- entity_type, entity_id, details
