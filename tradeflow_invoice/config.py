import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///invoicecrafting.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    RECEIPT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'receipts')
    LOGO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'logos')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Freemium limits
    FREE_INVOICE_LIMIT = 10
    PREMIUM_PRICE_MONTHLY = 9.99
    PREMIUM_PRICE_YEARLY = 99.99
    
    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    WTF_CSRF_ENABLED = True
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Trade types
    TRADE_TYPES = [
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('hvac', 'HVAC Technician'),
        ('tutor', 'Tutor'),
        ('consultant', 'Consultant'),
        ('photographer', 'Photographer'),
        ('cleaner', 'Cleaner'),
        ('handyman', 'Handyman'),
        ('landscaper', 'Landscaper'),
        ('painter', 'Painter'),
        ('carpenter', 'Carpenter'),
        ('mechanic', 'Mechanic'),
        ('designer', 'Designer'),
        ('developer', 'Developer'),
        ('writer', 'Writer'),
        ('coach', 'Coach'),
        ('therapist', 'Therapist'),
        ('other', 'Other')
    ]
    
    # Expense categories
    EXPENSE_CATEGORIES = [
        ('fuel', 'Fuel'),
        ('materials', 'Materials'),
        ('tools', 'Tools'),
        ('travel', 'Travel'),
        ('labor', 'Labor/Subcontractor'),
        ('equipment', 'Equipment Rental'),
        ('insurance', 'Insurance'),
        ('advertising', 'Advertising'),
        ('office', 'Office Supplies'),
        ('meals', 'Meals'),
        ('other', 'Other')
    ]
    
    # Invoice templates per trade
    INVOICE_TEMPLATES = {
        'plumber': ['Service Call', 'Installation', 'Repair', 'Maintenance'],
        'electrician': ['Service Call', 'Installation', 'Repair', 'Inspection'],
        'hvac': ['Service Call', 'Installation', 'Maintenance', 'Repair'],
        'tutor': ['Hourly Session', 'Package Deal', 'Assessment', 'Test Prep'],
        'consultant': ['Hourly Consulting', 'Project-Based', 'Retainer', 'Analysis'],
        'photographer': ['Photo Session', 'Event Coverage', 'Print Package', 'Editing'],
        'cleaner': ['Standard Clean', 'Deep Clean', 'Move-In/Out', 'Commercial'],
        'handyman': ['Repair', 'Installation', 'Assembly', 'Maintenance'],
        'landscaper': ['Lawn Care', 'Landscaping', 'Maintenance', 'Design'],
        'default': ['Service', 'Product', 'Labor', 'Materials']
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
