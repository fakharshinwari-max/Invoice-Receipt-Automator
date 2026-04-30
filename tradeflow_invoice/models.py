from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    """User model for authentication and account management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Freemium tracking
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    invoice_count_current_month = db.Column(db.Integer, default=0)
    invoice_limit = db.Column(db.Integer, default=10)
    last_invoice_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Trade type
    trade_type = db.Column(db.String(50), default='other')
    
    # Relationships
    business_profile = db.relationship('BusinessProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    clients = db.relationship('Client', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    settings = db.relationship('Settings', backref='user', uselist=False, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def reset_invoice_count(self):
        """Reset monthly invoice count."""
        self.invoice_count_current_month = 0
        self.last_invoice_reset = datetime.utcnow()
    
    def can_create_invoice(self):
        """Check if user can create more invoices this month."""
        now = datetime.utcnow()
        # Reset if new month
        if self.last_invoice_reset.month != now.month or self.last_invoice_reset.year != now.year:
            self.reset_invoice_count()
        
        if self.is_premium:
            return True
        
        return self.invoice_count_current_month < self.invoice_limit
    
    def increment_invoice_count(self):
        """Increment the invoice count for the current month."""
        now = datetime.utcnow()
        if self.last_invoice_reset.month != now.month or self.last_invoice_reset.year != now.year:
            self.reset_invoice_count()
        
        self.invoice_count_current_month += 1
    
    def __repr__(self):
        return f'<User {self.email}>'


class BusinessProfile(db.Model):
    """Business profile with branding information."""
    __tablename__ = 'business_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    logo_path = db.Column(db.String(500), nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    default_tax_rate = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.Integer, default=30)  # Net 30 days
    bank_details = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<BusinessProfile {self.business_name}>'


class Client(db.Model):
    """Client/Customer model."""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.name}>'


class Job(db.Model):
    """Job/Project model for tracking work by project."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, on_hold, cancelled
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='job', lazy='dynamic')
    expenses = db.relationship('Expense', backref='job', lazy='dynamic')
    
    @property
    def total_revenue(self):
        """Calculate total revenue from invoices linked to this job."""
        return sum(inv.total for inv in self.invoices if inv.status == 'paid')
    
    @property
    def total_expenses(self):
        """Calculate total expenses linked to this job."""
        return sum(exp.amount for exp in self.expenses)
    
    @property
    def profit(self):
        """Calculate profit for this job."""
        return self.total_revenue - self.total_expenses
    
    def __repr__(self):
        return f'<Job {self.name}>'


class Invoice(db.Model):
    """Invoice model for billing clients."""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    invoice_number = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, partially_paid, overdue, cancelled
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    due_date = db.Column(db.Date, nullable=False)
    paid_date = db.Column(db.Date, nullable=True)
    
    # Amounts
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)
    balance_due = db.Column(db.Float, default=0.0)
    
    # Content
    notes = db.Column(db.Text, nullable=True)
    terms = db.Column(db.Text, nullable=True)
    template_type = db.Column(db.String(50), default='default')
    
    # Files and sending
    pdf_path = db.Column(db.String(500), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    reminded_at = db.Column(db.DateTime, nullable=True)
    reminder_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_totals(self):
        """Calculate all totals based on line items."""
        self.subtotal = sum(item.amount for item in self.items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_due = self.total - self.amount_paid
        
        # Update status based on payment
        if self.amount_paid >= self.total and self.total > 0:
            self.status = 'paid'
            self.paid_date = datetime.utcnow().date()
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        elif self.status == 'paid':
            self.status = 'sent'
    
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.status in ['paid', 'cancelled']:
            return False
        return datetime.utcnow().date() > self.due_date
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceItem(db.Model):
    """Line items for invoices."""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    
    def calculate_amount(self):
        """Calculate line item amount."""
        self.amount = (self.quantity * self.unit_price) - self.discount
    
    def __repr__(self):
        return f'<InvoiceItem {self.description}>'


class Expense(db.Model):
    """Expense model for tracking business expenses."""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    receipt_path = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), default='other')
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    vendor = db.Column(db.String(200), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # cash, credit_card, bank_transfer
    notes = db.Column(db.Text, nullable=True)
    mileage = db.Column(db.Float, nullable=True)  # For travel expenses
    linked_invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.description}>'


class Settings(db.Model):
    """User settings and preferences."""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    dark_mode_enabled = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    reminder_frequency = db.Column(db.Integer, default=7)  # Days before due date
    late_fee_percentage = db.Column(db.Float, default=0.0)
    custom_fields = db.Column(db.Text, nullable=True)  # JSON string for custom fields
    invoice_prefix = db.Column(db.String(10), default='INV')
    auto_send_reminders = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Settings for User {self.user_id}>'


class ActivityLog(db.Model):
    """Activity log for auditing user actions."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)  # invoice, client, expense, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.action}>'
