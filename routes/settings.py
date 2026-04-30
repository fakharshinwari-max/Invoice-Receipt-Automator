"""Settings and profile management routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Settings, BusinessProfile, User
from forms import SettingsForm, BusinessProfileForm
from utils import save_uploaded_file, log_activity
import os

settings_bp = Blueprint('settings', __name__, template_folder='../templates/settings')


@settings_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Manage business profile."""
    profile = BusinessProfile.query.filter_by(user_id=current_user.id).first()
    
    # Create profile if it doesn't exist
    if not profile:
        profile = BusinessProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.flush()
    
    form = BusinessProfileForm(obj=profile)
    
    if form.validate_on_submit():
        profile.business_name = form.business_name.data
        profile.email = form.email.data
        profile.address = form.address.data
        profile.phone = form.phone.data
        profile.tax_id = form.tax_id.data
        profile.currency = form.currency.data
        profile.default_tax_rate = form.default_tax_rate.data
        profile.payment_terms = form.payment_terms.data
        profile.bank_details = form.bank_details.data
        profile.website = form.website.data
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                # Delete old logo if exists
                if profile.logo_path:
                    old_logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                                profile.logo_path.replace('uploads/', ''))
                    if os.path.exists(old_logo_path):
                        os.remove(old_logo_path)
                
                # Save new logo
                logo_path = save_uploaded_file(file, folder='logos')
                if logo_path:
                    profile.logo_path = logo_path
        
        db.session.commit()
        
        log_activity(current_user.id, 'update_profile', 
                    entity_type='business_profile', entity_id=profile.id)
        
        flash('Business profile updated successfully!', 'success')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html', form=form, profile=profile)


@settings_bp.route('/settings/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Manage user preferences."""
    settings = Settings.query.filter_by(user_id=current_user.id).first()
    
    # Create settings if they don't exist
    if not settings:
        settings = Settings(user_id=current_user.id)
        db.session.add(settings)
        db.session.flush()
    
    form = SettingsForm(obj=settings)
    
    if form.validate_on_submit():
        settings.dark_mode_enabled = form.dark_mode_enabled.data
        settings.email_notifications = form.email_notifications.data
        settings.reminder_frequency = form.reminder_frequency.data
        settings.late_fee_percentage = form.late_fee_percentage.data
        settings.invoice_prefix = form.invoice_prefix.data
        settings.auto_send_reminders = form.auto_send_reminders.data
        
        db.session.commit()
        
        log_activity(current_user.id, 'update_preferences', 
                    entity_type='settings', entity_id=settings.id)
        
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('settings.preferences'))
    
    return render_template('settings/preferences.html', form=form, settings=settings)


@settings_bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    """Manage account settings (email, password)."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_email':
            new_email = request.form.get('new_email')
            
            if new_email and new_email != current_user.email:
                # Check if email already exists
                if User.query.filter_by(email=new_email).first():
                    flash('Email already in use.', 'error')
                else:
                    current_user.email = new_email
                    db.session.commit()
                    log_activity(current_user.id, 'change_email', 
                                details=f'Changed email to {new_email}')
                    flash('Email updated successfully!', 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
            elif len(new_password) < 8:
                flash('New password must be at least 8 characters.', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                log_activity(current_user.id, 'change_password')
                flash('Password changed successfully!', 'success')
        
        return redirect(url_for('settings.account'))
    
    return render_template('settings/account.html')


@settings_bp.route('/settings/subscription')
@login_required
def subscription():
    """View subscription status."""
    return render_template('settings/subscription.html',
                         is_premium=current_user.is_premium,
                         invoice_count=current_user.invoice_count_current_month,
                         invoice_limit=current_user.invoice_limit)


@settings_bp.route('/settings/activity-log')
@login_required
def activity_log():
    """View user activity log."""
    from models import ActivityLog
    
    logs = ActivityLog.query.filter_by(user_id=current_user.id)\
        .order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    return render_template('settings/activity_log.html', logs=logs)


@settings_bp.route('/settings/export-data')
@login_required
def export_data():
    """Export all user data."""
    from models import Client, Invoice, Expense, Job
    import csv
    from io import StringIO
    from flask import make_response
    
    export_type = request.args.get('type', 'all')
    
    if export_type == 'clients':
        data = Client.query.filter_by(user_id=current_user.id).all()
        filename = 'clients_export.csv'
        headers = ['ID', 'Name', 'Email', 'Phone', 'Address', 'Notes', 'Created At']
        rows = [[c.id, c.name, c.email or '', c.phone or '', c.address or '', 
                c.notes or '', c.created_at.strftime('%Y-%m-%d %H:%M:%S')] for c in data]
    
    elif export_type == 'invoices':
        data = Invoice.query.filter_by(user_id=current_user.id).all()
        filename = 'invoices_export.csv'
        headers = ['Invoice #', 'Client', 'Status', 'Issue Date', 'Due Date', 
                  'Total', 'Amount Paid', 'Balance Due']
        rows = [[i.invoice_number, i.client.name, i.status, 
                i.issue_date.strftime('%Y-%m-%d'), i.due_date.strftime('%Y-%m-%d'),
                f'{i.total:.2f}', f'{i.amount_paid:.2f}', f'{i.balance_due:.2f}'] 
               for i in data]
    
    elif export_type == 'expenses':
        data = Expense.query.filter_by(user_id=current_user.id).all()
        filename = 'expenses_export.csv'
        headers = ['Date', 'Category', 'Description', 'Vendor', 'Amount', 'Job']
        rows = [[e.date.strftime('%Y-%m-%d'), e.category, e.description, 
                e.vendor or '', f'{e.amount:.2f}', e.job.name if e.job else ''] 
               for e in data]
    
    else:
        # Export all - simplified version
        flash('Full export coming soon. Please export individual sections.', 'info')
        return redirect(url_for('settings.profile'))
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    log_activity(current_user.id, 'export_data', details=f'Exported {export_type}')
    
    return response
