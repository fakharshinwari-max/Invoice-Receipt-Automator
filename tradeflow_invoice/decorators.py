from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=kwargs.get('next', None)))
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Decorator to require premium subscription for a route."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_premium:
            flash('This feature requires a premium subscription. Upgrade to unlock!', 'warning')
            return redirect(url_for('main.pricing'))
        return f(*args, **kwargs)
    return decorated_function


def check_invoice_limit(f):
    """Decorator to check if user has reached their invoice limit."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.can_create_invoice():
            flash(f'You have reached your invoice limit of {current_user.invoice_limit} per month. Upgrade to Premium for unlimited invoices!', 'warning')
            return redirect(url_for('main.pricing'))
        return f(*args, **kwargs)
    return decorated_function


def owner_or_404(f):
    """Decorator to ensure user owns the resource they're accessing."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # This is a simplified version - actual implementation would check
        # if the resource belongs to the current user
        from models import User
        
        user_id = kwargs.get('user_id') or current_user.id
        if user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function
