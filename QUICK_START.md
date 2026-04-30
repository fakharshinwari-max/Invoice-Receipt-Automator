# InvoiceCrafting Invoice - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites
- Python 3.8+
- pip

## Installation

### 1. Setup Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` and update:
- `SECRET_KEY` - Generate a random string or use default for testing
- `MAIL_USERNAME` and `MAIL_PASSWORD` - Email credentials (optional for testing)

### 4. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     print("Database initialized!")
>>> exit()
```

### 5. Run Application

```bash
python app.py
```

### 6. Access Application

Open browser and go to: **http://localhost:5000**

### 7. Demo Login

- **Email:** admin@example.com
- **Password:** password123

---

## What You Can Do

### 📋 Create Invoices
1. Click "Create Invoice"
2. Select client
3. Add line items
4. Generate PDF
5. Send via email

### 👥 Manage Clients
1. Add new clients with contact info
2. View client invoice history
3. Track total revenue per client
4. Edit/delete clients

### 💼 Track Jobs
1. Create projects/jobs
2. Link invoices and expenses
3. Calculate profit per job
4. View job profitability

### 📊 Track Expenses
1. Add business expenses
2. Upload receipts
3. Categorize expenses
4. Link to jobs

### 📈 View Dashboard
- Monthly revenue/expense overview
- Top clients by revenue
- Overdue invoices
- Quick statistics

### ⚙️ Manage Settings
- Business profile customization
- Invoice preferences
- User preferences
- Account management

---

## File Structure

```
invoicecrafting_invoice/
├── app.py              # Main app
├── requirements.txt    # Dependencies
├── .env               # Configuration (create from .env.example)
├── invoicecrafting.db # SQLite database (auto-created)
├── models.py          # Database models
├── forms.py           # Forms
├── routes/            # All routes
│   ├── auth.py
│   ├── invoices.py
│   ├── clients.py
│   ├── jobs.py
│   ├── expenses.py
│   ├── dashboard.py
│   └── settings.py
├── templates/         # HTML templates
└── static/            # CSS, JS, uploads
```

---

## Troubleshooting

### Application Won't Start
```bash
# Check if port 5000 is in use
# Edit app.py and change port:
app.run(debug=True, port=5001)
```

### Database Issues
```bash
# Delete and recreate database
rm invoicecrafting.db
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Email Not Working
- Update MAIL settings in `.env`
- For Gmail: Use App Password (not regular password)
- Check credentials: `python -c "from app import mail; print(mail)"`

### Can't Log In
- Check database was created: should see `invoicecrafting.db` file
- Demo account: admin@example.com / password123
- Create new account via Register button

---

## Key Features

✓ Professional PDF invoices  
✓ Client management  
✓ Project/job tracking  
✓ Expense management  
✓ Receipt uploads  
✓ Email delivery  
✓ Payment tracking  
✓ Dashboard analytics  
✓ User authentication  
✓ Freemium model (10 invoices/month free)  

---

## Next Steps

1. **Create your business profile** in Settings
2. **Add your clients** in Clients
3. **Create your first invoice**
4. **Generate and send PDF**

---

## Support

For detailed setup instructions, see `SETUP.md`  
For audit report, see `AUDIT_REPORT.md`  
For verification, run `python verify_app.py`

---

## Production Deployment

Before deploying:

1. Change `DEBUG=False` in `.env`
2. Generate secure `SECRET_KEY`
3. Use PostgreSQL instead of SQLite
4. Configure proper email service
5. Set up HTTPS
6. Use `gunicorn` instead of Flask dev server

```bash
# Production start
gunicorn app:app --bind 0.0.0.0:5000
```

---

**Enjoy using InvoiceCrafting Invoice! 🚀**
