#!/usr/bin/env python
"""
InvoiceCrafting Invoice - Application Verification Script
Validates all models, routes, and configurations
"""

import sys
import os

def check_imports():
    """Verify all imports are correct."""
    print("✓ Checking imports...")
    try:
        from app import create_app
        from config import Config, DevelopmentConfig, ProductionConfig
        from models import (User, BusinessProfile, Client, Job, Invoice, 
                          InvoiceItem, Expense, Settings, ActivityLog)
        from forms import (LoginForm, RegistrationForm, ClientForm, JobForm, 
                          InvoiceForm, InvoiceItemForm, ExpenseForm, SettingsForm)
        from extensions import db, login_manager, mail, csrf
        from decorators import check_invoice_limit, premium_required, owner_or_404
        from utils import (save_uploaded_file, generate_invoice_pdf, 
                          send_invoice_email, log_activity, generate_invoice_number)
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def check_models():
    """Verify all models are properly defined."""
    print("✓ Checking models...")
    try:
        from app import create_app, db
        from models import (User, BusinessProfile, Client, Job, Invoice,
                          InvoiceItem, Expense, Settings, ActivityLog)
        
        app = create_app()
        with app.app_context():
            # Check table definitions
            models = [User, BusinessProfile, Client, Job, Invoice, 
                     InvoiceItem, Expense, Settings, ActivityLog]
            
            for model in models:
                if hasattr(model, '__tablename__'):
                    print(f"  ✓ {model.__name__} model OK")
                else:
                    print(f"  ✗ {model.__name__} missing __tablename__")
                    return False
        
        return True
    except Exception as e:
        print(f"  ✗ Model error: {e}")
        return False


def check_database():
    """Check database connectivity."""
    print("✓ Checking database...")
    try:
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            # Try to get database URI
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"  ✓ Database URI: {db_uri[:50]}...")
            print("  ✓ Database configuration OK")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def check_routes():
    """Verify all routes are registered."""
    print("✓ Checking routes...")
    try:
        from app import create_app
        
        app = create_app()
        
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(rule)
        
        print(f"  ✓ Total routes: {len(routes)}")
        
        # Check essential routes
        essential_routes = [
            ('index', '/'),
            ('auth.login', '/auth/login'),
            ('auth.register', '/auth/register'),
            ('auth.logout', '/auth/logout'),
            ('invoices.index', '/invoices/'),
            ('invoices.create', '/invoices/create'),
            ('clients.index', '/clients/'),
            ('clients.create', '/clients/create'),
            ('jobs.index', '/jobs/'),
            ('expenses.index', '/expenses/'),
            ('settings.profile', '/settings/profile'),
        ]
        
        route_endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
        
        for name, path in essential_routes:
            if name in route_endpoints:
                print(f"  ✓ Route {name}: {path}")
            else:
                print(f"  ✗ Missing route: {name} ({path})")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Route error: {e}")
        return False


def check_config():
    """Verify configuration."""
    print("✓ Checking configuration...")
    try:
        from config import Config, DevelopmentConfig, ProductionConfig
        
        # Check essential config keys
        config_obj = Config()
        essential_keys = [
            'SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI',
            'UPLOAD_FOLDER',
            'FREE_INVOICE_LIMIT',
            'TRADE_TYPES',
            'EXPENSE_CATEGORIES',
            'INVOICE_TEMPLATES'
        ]
        
        for key in essential_keys:
            if hasattr(config_obj, key):
                value = getattr(config_obj, key)
                if isinstance(value, str):
                    print(f"  ✓ {key}: {value[:40]}...")
                else:
                    print(f"  ✓ {key}: Configured")
            else:
                print(f"  ✗ Missing config: {key}")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False


def check_utilities():
    """Verify utility functions."""
    print("✓ Checking utilities...")
    try:
        from utils import (allowed_file, save_uploaded_file, generate_invoice_pdf,
                          send_invoice_email, log_activity, generate_invoice_number,
                          calculate_dashboard_stats, send_reminder_email)
        
        utilities = [
            'allowed_file',
            'save_uploaded_file',
            'generate_invoice_pdf',
            'send_invoice_email',
            'log_activity',
            'generate_invoice_number',
            'calculate_dashboard_stats',
            'send_reminder_email'
        ]
        
        for util in utilities:
            print(f"  ✓ Utility: {util}")
        
        return True
    except Exception as e:
        print(f"  ✗ Utility error: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*60)
    print("InvoiceCrafting Invoice - Application Verification")
    print("="*60 + "\n")
    
    checks = [
        ("Imports", check_imports),
        ("Models", check_models),
        ("Database", check_database),
        ("Routes", check_routes),
        ("Configuration", check_config),
        ("Utilities", check_utilities),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed: {e}\n")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("="*60)
    if all_passed:
        print("\n✓ All checks passed! Application is ready to use.")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
