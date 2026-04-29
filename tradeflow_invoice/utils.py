import os
import uuid
from datetime import datetime
from flask import current_app, render_template
from flask_mail import Message
from extensions import mail
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_RIGHT, TA_CENTER


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file, folder='receipts'):
    """Save uploaded file securely and return the path."""
    if file and allowed_file(file.filename):
        # Create unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Determine folder
        if folder == 'receipts':
            upload_folder = current_app.config['RECEIPT_UPLOAD_FOLDER']
        elif folder == 'logos':
            upload_folder = current_app.config['LOGO_UPLOAD_FOLDER']
        else:
            upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Ensure folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Return relative path for database storage
        return f"uploads/{folder}/{filename}"
    
    return None


def generate_invoice_pdf(invoice, output_path=None):
    """Generate a professional PDF invoice using ReportLab."""
    from models import BusinessProfile
    
    # Get business profile
    profile = BusinessProfile.query.filter_by(user_id=invoice.user_id).first()
    
    # Create output path if not provided
    if output_path is None:
        filename = f"invoice_{invoice.invoice_number}.pdf"
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'invoices', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=12
    )
    
    normal_style = styles['Normal']
    right_style = ParagraphStyle('RightAlign', parent=normal_style, alignment=TA_RIGHT)
    center_style = ParagraphStyle('CenterAlign', parent=normal_style, alignment=TA_CENTER)
    
    # Header with logo and business info
    header_data = []
    
    # Left side - Business info
    business_info = f"<b>{profile.business_name if profile else 'Business Name'}</b><br/>"
    if profile:
        if profile.address:
            business_info += f"{profile.address.replace(chr(10), '<br/>')}<br/>"
        if profile.phone:
            business_info += f"Phone: {profile.phone}<br/>"
        if profile.email:
            business_info += f"Email: {profile.email}<br/>"
    
    header_data.append([business_info, ""])
    
    # Right side - Invoice title and number
    invoice_title = f"<b style='color: #2563EB; font-size: 20px;'>INVOICE</b><br/>"
    invoice_title += f"Invoice #: {invoice.invoice_number}<br/>"
    invoice_title += f"Date: {invoice.issue_date.strftime('%B %d, %Y')}<br/>"
    invoice_title += f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}"
    
    header_data[0][1] = invoice_title
    
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Client information
    client_info = f"<b>Bill To:</b><br/>"
    client_info += f"<b>{invoice.client.name}</b><br/>"
    if invoice.client.address:
        client_info += f"{invoice.client.address.replace(chr(10), '<br/>')}<br/>"
    if invoice.client.email:
        client_info += f"{invoice.client.email}<br/>"
    if invoice.client.phone:
        client_info += f"{invoice.client.phone}"
    
    elements.append(Paragraph(client_info, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Invoice items table
    items_data = [['Description', 'Qty', 'Unit Price', 'Amount']]
    
    for item in invoice.items:
        items_data.append([
            item.description,
            str(item.quantity),
            f"${item.unit_price:,.2f}",
            f"${item.amount:,.2f}"
        ])
    
    # Add subtotal, tax, discount, total
    items_data.append(['', '', 'Subtotal:', f"${invoice.subtotal:,.2f}"])
    
    if invoice.discount_amount > 0:
        items_data.append(['', '', 'Discount:', f"-${invoice.discount_amount:,.2f}"])
    
    if invoice.tax_rate > 0:
        items_data.append(['', '', f'Tax ({invoice.tax_rate}%):', f"${invoice.tax_amount:,.2f}"])
    
    items_data.append(['', '', '<b>Total:</b>', f"<b>${invoice.total:,.2f}</b>"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F3F4F6')]),
        ('ALIGN', (2, -4), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BACKGROUND', (2, -1), (3, -1), colors.HexColor('#DBEAFE')),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment summary
    payment_summary = f"<b>Amount Paid:</b> ${invoice.amount_paid:,.2f}<br/>"
    payment_summary += f"<b>Balance Due:</b> <span style='color: #DC2626; font-size: 16px;'>${invoice.balance_due:,.2f}</span>"
    
    elements.append(Paragraph(payment_summary, right_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Notes and terms
    if invoice.notes:
        elements.append(Paragraph("<b>Notes:</b>", heading_style))
        elements.append(Paragraph(invoice.notes.replace('\n', '<br/>'), normal_style))
        elements.append(Spacer(1, 0.2*inch))
    
    if invoice.terms:
        elements.append(Paragraph("<b>Terms & Conditions:</b>", heading_style))
        elements.append(Paragraph(invoice.terms.replace('\n', '<br/>'), normal_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = "<i>Thank you for your business!</i>"
    if profile and profile.bank_details:
        footer_text += f"<br/><b>Payment Instructions:</b><br/>{profile.bank_details}"
    
    elements.append(Paragraph(footer_text, center_style))
    
    # Build PDF
    doc.build(elements)
    
    # Update invoice pdf_path
    invoice.pdf_path = f"uploads/invoices/{os.path.basename(output_path)}"
    
    return output_path


def send_invoice_email(invoice, recipient_email, subject=None, template='emails/invoice_email.html'):
    """Send invoice via email."""
    try:
        if not subject:
            subject = f"Invoice #{invoice.invoice_number} from {invoice.user.business_profile.business_name if invoice.user.business_profile else 'Our Business'}"
        
        # Create message
        msg = Message(subject, recipients=[recipient_email])
        
        # Render HTML body
        html_body = render_template(template, invoice=invoice)
        msg.html = html_body
        
        # Attach PDF if available
        if invoice.pdf_path:
            pdf_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], invoice.pdf_path.replace('uploads/', ''))
            if os.path.exists(pdf_full_path):
                with current_app.open_resource(pdf_full_path) as fp:
                    msg.attach(f"Invoice_{invoice.invoice_number}.pdf", "application/pdf", fp.read())
        
        # Send email
        mail.send(msg)
        
        # Update invoice sent_at
        invoice.sent_at = datetime.utcnow()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending invoice email: {str(e)}")
        return False


def send_reminder_email(invoice, days_overdue=0):
    """Send payment reminder email for overdue invoice."""
    try:
        if not invoice.client.email:
            return False
        
        subject = f"Payment Reminder: Invoice #{invoice.invoice_number} is {'overdue' if days_overdue > 0 else 'due soon'}"
        
        msg = Message(subject, recipients=[invoice.client.email])
        html_body = render_template('emails/reminder_email.html', 
                                   invoice=invoice, 
                                   days_overdue=days_overdue)
        msg.html = html_body
        
        # Attach PDF
        if invoice.pdf_path:
            pdf_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], invoice.pdf_path.replace('uploads/', ''))
            if os.path.exists(pdf_full_path):
                with current_app.open_resource(pdf_full_path) as fp:
                    msg.attach(f"Invoice_{invoice.invoice_number}.pdf", "application/pdf", fp.read())
        
        mail.send(msg)
        
        # Update invoice
        invoice.reminded_at = datetime.utcnow()
        invoice.reminder_count += 1
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending reminder email: {str(e)}")
        return False


def log_activity(user_id, action, entity_type=None, entity_id=None, details=None, ip_address=None):
    """Log user activity for auditing."""
    from models import ActivityLog
    from extensions import db
    
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address
    )
    
    db.session.add(log)
    db.session.commit()


def generate_invoice_number(user_id):
    """Generate a unique invoice number."""
    from models import Invoice, Settings
    
    # Get user's invoice prefix
    settings = Settings.query.filter_by(user_id=user_id).first()
    prefix = settings.invoice_prefix if settings else 'INV'
    
    # Get count of invoices this year
    year = datetime.utcnow().year
    count = Invoice.query.filter(
        Invoice.user_id == user_id,
        Invoice.created_at.year == year
    ).count()
    
    # Generate invoice number: INV-2024-001
    invoice_number = f"{prefix}-{year}-{count + 1:03d}"
    
    return invoice_number


def calculate_dashboard_stats(user_id):
    """Calculate dashboard statistics for a user."""
    from models import Invoice, Expense
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # This month's stats
    invoices_this_month = Invoice.query.filter(
        Invoice.user_id == user_id,
        Invoice.created_at >= first_day_of_month
    ).all()
    
    expenses_this_month = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= first_day_of_month.date()
    ).all()
    
    # Calculate totals
    total_invoiced = sum(inv.total for inv in invoices_this_month)
    total_received = sum(inv.amount_paid for inv in invoices_this_month)
    total_pending = sum(inv.balance_due for inv in invoices_this_month)
    total_expenses = sum(exp.amount for exp in expenses_this_month)
    profit = total_received - total_expenses
    
    # Overdue invoices
    overdue_invoices = Invoice.query.filter(
        Invoice.user_id == user_id,
        Invoice.status.notin_(['paid', 'cancelled']),
        Invoice.due_date < now.date()
    ).count()
    
    return {
        'total_invoiced': total_invoiced,
        'total_received': total_received,
        'total_pending': total_pending,
        'total_expenses': total_expenses,
        'profit': profit,
        'overdue_count': overdue_invoices,
        'invoice_count': len(invoices_this_month)
    }
