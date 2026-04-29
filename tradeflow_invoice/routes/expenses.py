"""Expense and receipt tracking routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Expense, Job
from forms import ExpenseForm
from utils import save_uploaded_file, log_activity
import os

expenses_bp = Blueprint('expenses', __name__, template_folder='../templates/expenses')


@expenses_bp.route('/expenses')
@login_required
def index():
    """List all expenses."""
    # Get filter parameters
    category = request.args.get('category', 'all')
    job_id = request.args.get('job_id', type=int)
    search = request.args.get('search', '')
    
    # Build query
    query = Expense.query.filter_by(user_id=current_user.id)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if job_id:
        query = query.filter_by(job_id=job_id)
    
    if search:
        query = query.filter(
            (Expense.description.ilike(f'%{search}%')) |
            (Expense.vendor.ilike(f'%{search}%'))
        )
    
    # Order by date descending
    expenses = query.order_by(Expense.date.desc()).all()
    
    # Get jobs for filter
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals
    total_expenses = sum(exp.amount for exp in expenses)
    
    return render_template('expenses/list.html', 
                         expenses=expenses,
                         jobs=jobs,
                         current_category=category,
                         current_job=job_id,
                         search=search,
                         total_expenses=total_expenses)


@expenses_bp.route('/expenses/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new expense."""
    form = ExpenseForm()
    
    # Populate job choices
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    form.job_id.choices = [(0, 'No Job')] + [(j.id, j.name) for j in jobs]
    
    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            category=form.category.data,
            description=form.description.data,
            amount=form.amount.data,
            date=form.date.data,
            vendor=form.vendor.data,
            payment_method=form.payment_method.data,
            job_id=form.job_id.data if form.job_id.data else None,
            notes=form.notes.data,
            mileage=form.mileage.data
        )
        
        db.session.add(expense)
        db.session.commit()
        
        log_activity(current_user.id, 'create_expense', 
                    entity_type='expense', entity_id=expense.id,
                    details=f'Created expense: {expense.description}')
        
        flash('Expense created successfully!', 'success')
        return redirect(url_for('expenses.index'))
    
    return render_template('expenses/create.html', form=form)


@expenses_bp.route('/expenses/upload-receipt', methods=['GET', 'POST'])
@login_required
def upload_receipt():
    """Upload receipt(s) for expenses."""
    if request.method == 'POST':
        files = request.files.getlist('receipts')
        descriptions = request.form.getlist('descriptions')
        amounts = request.form.getlist('amounts')
        categories = request.form.getlist('categories')
        dates = request.form.getlist('dates')
        vendors = request.form.getlist('vendors')
        job_ids = request.form.getlist('job_ids')
        
        uploaded_count = 0
        
        for i, file in enumerate(files):
            if file and file.filename:
                # Save file
                receipt_path = save_uploaded_file(file, folder='receipts')
                
                if receipt_path:
                    # Create expense
                    expense = Expense(
                        user_id=current_user.id,
                        category=categories[i] if i < len(categories) else 'other',
                        description=descriptions[i] if i < len(descriptions) else 'Receipt upload',
                        amount=float(amounts[i]) if i < len(amounts) and amounts[i] else 0.0,
                        date=dates[i] if i < len(dates) and dates[i] else None,
                        vendor=vendors[i] if i < len(vendors) else None,
                        job_id=int(job_ids[i]) if i < len(job_ids) and job_ids[i] else None,
                        receipt_path=receipt_path
                    )
                    
                    db.session.add(expense)
                    uploaded_count += 1
        
        if uploaded_count > 0:
            db.session.commit()
            log_activity(current_user.id, 'upload_receipts', 
                        details=f'Uploaded {uploaded_count} receipts')
            flash(f'{uploaded_count} receipt(s) uploaded successfully!', 'success')
        else:
            flash('No valid receipts uploaded.', 'error')
        
        return redirect(url_for('expenses.index'))
    
    # GET request - show upload form
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    return render_template('expenses/receipt_upload.html', jobs=jobs)


@expenses_bp.route('/expenses/<int:expense_id>')
@login_required
def view(expense_id):
    """View expense details."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    return render_template('expenses/view.html', expense=expense)


@expenses_bp.route('/expenses/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    """Edit expense."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    
    form = ExpenseForm(obj=expense)
    
    # Populate job choices
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    form.job_id.choices = [(0, 'No Job')] + [(j.id, j.name) for j in jobs]
    
    if form.validate_on_submit():
        expense.category = form.category.data
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.date = form.date.data
        expense.vendor = form.vendor.data
        expense.payment_method = form.payment_method.data
        expense.job_id = form.job_id.data if form.job_id.data else None
        expense.notes = form.notes.data
        expense.mileage = form.mileage.data
        
        db.session.commit()
        
        log_activity(current_user.id, 'update_expense', 
                    entity_type='expense', entity_id=expense.id)
        
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses.view', expense_id=expense.id))
    
    return render_template('expenses/create.html', form=form, expense=expense)


@expenses_bp.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete expense."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    
    description = expense.description
    db.session.delete(expense)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_expense', 
                entity_type='expense', entity_id=expense_id,
                details=f'Deleted expense: {description}')
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/expenses/<int:expense_id>/receipt')
@login_required
def view_receipt(expense_id):
    """View/download receipt image."""
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    
    if not expense.receipt_path:
        flash('No receipt attached.', 'error')
        return redirect(url_for('expenses.view', expense_id=expense_id))
    
    receipt_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                               expense.receipt_path.replace('uploads/', ''))
    
    if os.path.exists(receipt_path):
        return send_file(receipt_path, as_attachment=False)
    else:
        flash('Receipt file not found.', 'error')
        return redirect(url_for('expenses.view', expense_id=expense_id))


@expenses_bp.route('/expenses/export')
@login_required
def export_expenses():
    """Export expenses to CSV."""
    from io import StringIO
    import csv
    from flask import make_response
    
    expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Date', 'Category', 'Description', 'Vendor', 'Amount', 
                    'Payment Method', 'Job', 'Notes'])
    
    # Data
    for expense in expenses:
        job_name = expense.job.name if expense.job else ''
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category,
            expense.description,
            expense.vendor,
            f'{expense.amount:.2f}',
            expense.payment_method,
            job_name,
            expense.notes
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=expenses_export.csv'
    
    log_activity(current_user.id, 'export_expenses')
    
    return response
