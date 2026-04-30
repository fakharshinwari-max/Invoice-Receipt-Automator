"""
InvoiceCrafting Invoice - Main Application Entry Point
A simple, beautiful invoice & receipt automator for freelancers and tradespeople.
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from config import config, Config
from extensions import init_extensions, db, login_manager, mail, csrf
from models import User, BusinessProfile, Client, Job, Invoice, InvoiceItem, Expense, Settings, ActivityLog
from forms import LoginForm, RegistrationForm, BusinessProfileForm, ClientForm, JobForm, InvoiceForm, InvoiceItemForm, ExpenseForm, SettingsForm
from utils import save_uploaded_file, generate_invoice_pdf, send_invoice_email, log_activity, generate_invoice_number, calculate_dashboard_stats, send_reminder_email
from decorators import login_required, check_invoice_limit
from datetime import datetime, timedelta


# Create Flask app
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECEIPT_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOGO_UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.invoices import invoices_bp
    from routes.clients import clients_bp
    from routes.expenses import expenses_bp
    from routes.jobs import jobs_bp
    from routes.settings import settings_bp
    from routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(invoices_bp, url_prefix='/invoices')
    app.register_blueprint(clients_bp, url_prefix='/clients')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(dashboard_bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Routes
    @app.route('/')
    def index():
        """Landing page."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html')
    
    @app.route('/features')
    def features():
        """Features page."""
        return render_template('features.html')
    
    @app.route('/pricing')
    def pricing():
        """Pricing page."""
        return render_template('pricing.html', 
                             monthly_price=Config.PREMIUM_PRICE_MONTHLY,
                             yearly_price=Config.PREMIUM_PRICE_YEARLY,
                             free_limit=Config.FREE_INVOICE_LIMIT)
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    # Context processor to make trade types available in templates
    @app.context_processor
    def inject_globals():
        return {
            'trade_types': Config.TRADE_TYPES,
            'expense_categories': Config.EXPENSE_CATEGORIES,
            'invoice_templates': Config.INVOICE_TEMPLATES
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user for testing (remove in production)
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                email='admin@example.com',
                trade_type='consultant'
            )
            admin.set_password('password123')
            admin.is_premium = True
            
            db.session.add(admin)
            
            # Create business profile
            profile = BusinessProfile(
                user=admin,
                business_name='Demo Consulting',
                address='123 Business St\nCity, State 12345',
                phone='(555) 123-4567',
                currency='USD',
                default_tax_rate=8.5
            )
            db.session.add(profile)
            
            db.session.commit()
            print("Admin user created: admin@example.com / password123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
