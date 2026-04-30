from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from models import User
from config import Config


def login_required(f):
    """Custom login decorator that checks if user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Decorator to restrict access to premium features."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_premium:
            flash('This feature requires a premium subscription.', 'error')
            return redirect(url_for('pricing'))
        return f(*args, **kwargs)
    return decorated_function


def check_invoice_limit(f):
    """Decorator to check if user has reached invoice limit."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Premium users have no limit
        if current_user.is_premium:
            return f(*args, **kwargs)
        
        # Check free user invoice count
        from models import Invoice
        from extensions import db
        invoice_count = Invoice.query.filter_by(user_id=current_user.id).count()
        
        if invoice_count >= Config.FREE_INVOICE_LIMIT:
            flash(f'You have reached the free limit of {Config.FREE_INVOICE_LIMIT} invoices. Please upgrade to continue creating invoices.', 'error')
            return redirect(url_for('pricing'))
        
        return f(*args, **kwargs)
    return decorated_function
