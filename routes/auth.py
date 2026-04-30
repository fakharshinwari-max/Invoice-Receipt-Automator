"""Authentication routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, BusinessProfile, Settings
from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from utils import log_activity

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            log_activity(user.id, 'login', ip_address=request.remote_addr)
            
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please login or use a different email.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data,
            trade_type=form.trade_type.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create business profile
        profile = BusinessProfile(
            user_id=user.id,
            business_name=form.business_name.data,
            currency='USD'
        )
        db.session.add(profile)
        
        # Create default settings
        settings = Settings(user_id=user.id)
        db.session.add(settings)
        
        db.session.commit()
        
        log_activity(user.id, 'register', ip_address=request.remote_addr)
        
        flash('Account created successfully! Welcome to InvoiceCrafting Invoice.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    log_activity(current_user.id, 'logout', ip_address=request.remote_addr)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password request."""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # In production, send password reset email here
            # For now, just show a success message
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        else:
            # Don't reveal if email exists or not
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password (simplified - in production would use token)."""
    # This is a simplified version - in production you'd use secure tokens
    flash('Password reset functionality requires email configuration. Please contact support.', 'warning')
    return redirect(url_for('auth.login'))
