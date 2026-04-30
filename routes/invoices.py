"""Invoice routes - Core feature of InvoiceCrafting Invoice."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Invoice, InvoiceItem, Client, Job, BusinessProfile
from forms import InvoiceForm
from utils import generate_invoice_pdf, send_invoice_email, send_reminder_email, log_activity, generate_invoice_number
from decorators import check_invoice_limit
from datetime import datetime, timedelta
import os

invoices_bp = Blueprint('invoices', __name__, template_folder='../templates/invoices')


@invoices_bp.route('/')
@login_required
def index():
    """List all invoices."""
    status = request.args.get('status', 'all')
    client_id = request.args.get('client_id', type=int)
    job_id = request.args.get('job_id', type=int)
    search = request.args.get('search', '')
    
    query = Invoice.query.filter_by(user_id=current_user.id)
    if status != 'all':
        query = query.filter_by(status=status)
    if client_id:
        query = query.filter_by(client_id=client_id)
    if job_id:
        query = query.filter_by(job_id=job_id)
    if search:
        query = query.filter(Invoice.invoice_number.ilike(f'%{search}%'))
    invoices = query.order_by(Invoice.created_at.desc()).all()
    
    clients = Client.query.filter_by(user_id=current_user.id).all()
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    
    return render_template('invoices/list.html', 
                         invoices=invoices, clients=clients, jobs=jobs,
                         current_status=status, current_client=client_id,
                         current_job=job_id, search=search)


@invoices_bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_invoice_limit
def create():
    """Create a new invoice."""
    form = InvoiceForm()
    
    # Populate client choices
    clients = Client.query.filter_by(user_id=current_user.id).all()
    form.client_id.choices = [(c.id, c.name) for c in clients]
    
    # Populate job choices
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    form.job_id.choices = [(0, 'No Job')] + [(j.id, j.name) for j in jobs]
    
    # Populate template_type choices (based on user's trade)
    user = current_user
    templates = current_app.config['INVOICE_TEMPLATES'].get(user.trade_type,
                  current_app.config['INVOICE_TEMPLATES']['default'])
    form.template_type.choices = [(t.lower().replace(' ', '_'), t) for t in templates]
    
    # Ensure status choices are set (already defined in form, but assign again for safety)
    form.status.choices = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')
    ]
    
    # Set default values
    form.invoice_number.data = generate_invoice_number(current_user.id)
    form.issue_date.data = datetime.utcnow().date()
    form.due_date.data = datetime.utcnow().date() + timedelta(days=30)
    form.status.default = 'draft'
    form.template_type.default = form.template_type.choices[0][0] if form.template_type.choices else 'default'
    form.process()  # Force default values into the form
    
    # Get default tax rate from business profile
    profile = BusinessProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        form.tax_rate.data = profile.default_tax_rate
    else:
        form.tax_rate.data = 0.0
    
    if form.validate_on_submit():
        invoice = Invoice(
            user_id=current_user.id,
            client_id=form.client_id.data,
            job_id=form.job_id.data if form.job_id.data != 0 else None,
            invoice_number=form.invoice_number.data,
            issue_date=form.issue_date.data,
            due_date=form.due_date.data,
            tax_rate=form.tax_rate.data,
            discount_amount=form.discount_amount.data,
            notes=form.notes.data,
            terms=form.terms.data,
            template_type=form.template_type.data,
            status=form.status.data,
            amount_paid=0.0
        )
        db.session.add(invoice)
        db.session.flush()

        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('unit_price[]')

        num_items = 0
        for i in range(len(descriptions)):
            if descriptions[i] and quantities[i] and prices[i]:
                try:
                    qty = float(quantities[i])
                    price = float(prices[i])
                    item = InvoiceItem(
                        invoice_id=invoice.id,
                        description=descriptions[i],
                        quantity=qty,
                        unit_price=price
                    )
                    item.calculate_amount()
                    db.session.add(item)
                    num_items += 1
                except ValueError:
                    flash(f'Invalid number in line item {i+1}', 'error')
                    return render_template('invoices/create.html', form=form)

        invoice.calculate_totals()
        current_user.increment_invoice_count()
        db.session.commit()

        log_activity(current_user.id, 'create_invoice',
                    entity_type='invoice', entity_id=invoice.id,
                    details=f'Created invoice {invoice.invoice_number}')

        if num_items > 0:
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('invoices.view', invoice_id=invoice.id))
        else:
            flash('Invoice created successfully! Add line items below.', 'success')
            return redirect(url_for('invoices.edit', invoice_id=invoice.id))

    return render_template('invoices/create.html', form=form)


@invoices_bp.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    form = InvoiceForm(obj=invoice)
    
    clients = Client.query.filter_by(user_id=current_user.id).all()
    form.client_id.choices = [(c.id, c.name) for c in clients]
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    form.job_id.choices = [(0, 'No Job')] + [(j.id, j.name) for j in jobs]
    # Set choices for template_type and status again
    user = current_user
    templates = current_app.config['INVOICE_TEMPLATES'].get(user.trade_type,
                  current_app.config['INVOICE_TEMPLATES']['default'])
    form.template_type.choices = [(t.lower().replace(' ', '_'), t) for t in templates]
    form.status.choices = [('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'),
                           ('partially_paid', 'Partially Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')]
    
    if form.validate_on_submit():
        print("=" * 50)
        print("POST data received:", request.form)
        print("Form errors:", form.errors)
        print("=" * 50)
        invoice.client_id = form.client_id.data
        invoice.job_id = form.job_id.data if form.job_id.data != 0 else None
        invoice.invoice_number = form.invoice_number.data
        invoice.issue_date = form.issue_date.data
        invoice.due_date = form.due_date.data
        invoice.tax_rate = form.tax_rate.data
        invoice.discount_amount = form.discount_amount.data
        invoice.notes = form.notes.data
        invoice.terms = form.terms.data
        invoice.status = form.status.data
        invoice.amount_paid = form.amount_paid.data if form.amount_paid.data else 0.0
        invoice.calculate_totals()
        generate_invoice_pdf(invoice)
        db.session.commit()
        
        log_activity(current_user.id, 'update_invoice', entity_type='invoice', entity_id=invoice.id)
        flash('Invoice updated successfully!', 'success')
        return redirect(url_for('invoices.view', invoice_id=invoice.id))
    
    return render_template('invoices/edit.html', form=form, invoice=invoice)


@invoices_bp.route('/<int:invoice_id>')
@login_required
def view(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    return render_template('invoices/view.html', invoice=invoice)


@invoices_bp.route('/<int:invoice_id>/pdf')
@login_required
def download_pdf(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    if not invoice.pdf_path or not os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], invoice.pdf_path.replace('uploads/', ''))):
        generate_invoice_pdf(invoice)
        db.session.commit()
    pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], invoice.pdf_path.replace('uploads/', ''))
    return send_file(pdf_path, as_attachment=True, download_name=f'Invoice_{invoice.invoice_number}.pdf')


@invoices_bp.route('/<int:invoice_id>/send', methods=['POST'])
@login_required
def send(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    if not invoice.client.email:
        flash('Client does not have an email address.', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))
    
    generate_invoice_pdf(invoice)
    db.session.commit()
    if send_invoice_email(invoice, invoice.client.email):
        invoice.status = 'sent'
        db.session.commit()
        log_activity(current_user.id, 'send_invoice', entity_type='invoice', entity_id=invoice.id)
        flash('Invoice sent successfully!', 'success')
    else:
        flash('Failed to send invoice. Please check email configuration.', 'error')
    return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    invoice_number = invoice.invoice_number
    db.session.delete(invoice)
    db.session.commit()
    log_activity(current_user.id, 'delete_invoice', entity_type='invoice', entity_id=invoice_id,
                 details=f'Deleted invoice {invoice_number}')
    flash('Invoice deleted successfully!', 'success')
    return redirect(url_for('invoices.index'))


@invoices_bp.route('/<int:invoice_id>/items/add', methods=['POST'])
@login_required
def add_item(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    item = InvoiceItem(
        invoice_id=invoice.id,
        description=data.get('description', ''),
        quantity=float(data.get('quantity', 1)),
        unit_price=float(data.get('unit_price', 0)),
        tax_rate=float(data.get('tax_rate', 0)),
        discount=float(data.get('discount', 0))
    )
    item.calculate_amount()
    db.session.add(item)
    invoice.calculate_totals()
    db.session.commit()
    return jsonify({
        'success': True,
        'item_id': item.id,
        'subtotal': invoice.subtotal,
        'tax_amount': invoice.tax_amount,
        'total': invoice.total,
        'balance_due': invoice.balance_due
    })


@invoices_bp.route('/<int:invoice_id>/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(invoice_id, item_id):
    item = InvoiceItem.query.filter_by(id=item_id, invoice_id=invoice_id).first_or_404()
    invoice = item.invoice
    db.session.delete(item)
    invoice.calculate_totals()
    db.session.commit()
    return jsonify({
        'success': True,
        'subtotal': invoice.subtotal,
        'tax_amount': invoice.tax_amount,
        'total': invoice.total,
        'balance_due': invoice.balance_due
    })


@invoices_bp.route('/<int:invoice_id>/record-payment', methods=['POST'])
@login_required
def record_payment(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    amount = float(data.get('amount', 0))
    if amount > 0:
        invoice.amount_paid += amount
        invoice.calculate_totals()
        db.session.commit()
        log_activity(current_user.id, 'record_payment', entity_type='invoice', entity_id=invoice.id,
                     details=f'Recorded payment of ${amount:.2f}')
        flash(f'Payment of ${amount:.2f} recorded successfully!', 'success')
    else:
        flash('Invalid payment amount.', 'error')
    return redirect(url_for('invoices.view', invoice_id=invoice_id))


@invoices_bp.route('/<int:invoice_id>/remind', methods=['POST'])
@login_required
def send_reminder(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first_or_404()
    if not invoice.client.email:
        flash('Client does not have an email address.', 'error')
        return redirect(url_for('invoices.view', invoice_id=invoice_id))
    
    days_overdue = (datetime.utcnow().date() - invoice.due_date).days if invoice.is_overdue() else 0
    if send_reminder_email(invoice, days_overdue):
        db.session.commit()
        log_activity(current_user.id, 'send_reminder', entity_type='invoice', entity_id=invoice.id)
        flash('Reminder sent successfully!', 'success')
    else:
        flash('Failed to send reminder.', 'error')
    return redirect(url_for('invoices.view', invoice_id=invoice_id))