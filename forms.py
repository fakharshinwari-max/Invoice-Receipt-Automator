from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, \
    DecimalField, TextAreaField, DateField, IntegerField, FloatField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from config import Config


class InvoiceForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    job_id = SelectField('Job/Project', coerce=int, validators=[Optional()])
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    issue_date = DateField('Issue Date', format='%Y-%m-%d', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    tax_rate = DecimalField('Tax Rate (%)', places=2, default=0.0)
    discount_amount = DecimalField('Discount', places=2, default=0.0)
    notes = TextAreaField('Notes')
    terms = TextAreaField('Terms & Conditions')
    
    # ✅ FIX: Add choices for template_type
    template_type = SelectField('Template Type', choices=[
        ('default', 'Default'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal')
    ], default='default')
    
    # ✅ FIX: Ensure status choices are correct
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], default='draft')
    
    amount_paid = DecimalField('Amount Paid', places=2, default=0.0)
    
# Authentication Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    trade_type = SelectField('Trade/Profession', choices=Config.TRADE_TYPES)
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=200)])


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])


# Business Profile Forms
class BusinessProfileForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=200)])
    email = StringField('Business Email', validators=[Optional(), Email()])
    address = TextAreaField('Address')
    phone = StringField('Phone')
    tax_id = StringField('Tax ID / EIN')
    currency = StringField('Currency', default='USD')
    default_tax_rate = DecimalField('Default Tax Rate (%)', places=2, default=0.0)
    payment_terms = IntegerField('Payment Terms (Net Days)', default=30)
    bank_details = TextAreaField('Bank Details / Payment Instructions')
    website = StringField('Website')


# Client Forms
class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone')
    address = TextAreaField('Address')
    notes = TextAreaField('Notes')
    submit = SubmitField('Create Client')   # Add submit button


# Job Forms
class JobForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    name = StringField('Job Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled')
    ])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    budget = DecimalField('Budget', places=2, validators=[Optional()])


# Invoice Forms
class InvoiceForm(FlaskForm):
    client_id = SelectField('Client', coerce=int, validators=[DataRequired()])
    job_id = SelectField('Job/Project', coerce=int, validators=[Optional()])
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    issue_date = DateField('Issue Date', format='%Y-%m-%d', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    tax_rate = DecimalField('Tax Rate (%)', places=2, default=0.0)
    discount_amount = DecimalField('Discount', places=2, default=0.0)
    notes = TextAreaField('Notes')
    terms = TextAreaField('Terms & Conditions')
    template_type = SelectField('Template Type')
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ])
    amount_paid = DecimalField('Amount Paid', places=2, default=0.0)


class InvoiceItemForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=500)])
    quantity = DecimalField('Quantity/Hours', places=2, default=1.0)
    unit_price = DecimalField('Unit Price', places=2, default=0.0)
    tax_rate = DecimalField('Tax Rate (%)', places=2, default=0.0)
    discount = DecimalField('Discount', places=2, default=0.0)


# Expense Forms
class ExpenseForm(FlaskForm):
    category = SelectField('Category', choices=Config.EXPENSE_CATEGORIES)
    description = StringField('Description', validators=[DataRequired(), Length(max=500)])
    amount = DecimalField('Amount', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    vendor = StringField('Vendor')
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('other', 'Other')
    ])
    job_id = SelectField('Link to Job', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes')
    mileage = DecimalField('Mileage (miles/km)', places=2, validators=[Optional()])


# Settings Forms
class SettingsForm(FlaskForm):
    dark_mode_enabled = BooleanField('Enable Dark Mode')
    email_notifications = BooleanField('Email Notifications')
    reminder_frequency = IntegerField('Reminder Frequency (Days Before Due)', default=7)
    late_fee_percentage = DecimalField('Late Fee Percentage (%)', places=2, default=0.0)
    invoice_prefix = StringField('Invoice Prefix', default='INV')
    auto_send_reminders = BooleanField('Auto-Send Reminders')


# Search Form
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search In', choices=[
        ('all', 'All'),
        ('invoices', 'Invoices'),
        ('clients', 'Clients'),
        ('expenses', 'Expenses'),
        ('jobs', 'Jobs')
    ])
