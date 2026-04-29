"""Client management routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Client, Invoice
from forms import ClientForm
from utils import log_activity

clients_bp = Blueprint('clients', __name__, template_folder='../templates/clients')


@clients_bp.route('/clients')
@login_required
def index():
    """List all clients."""
    search = request.args.get('search', '')
    
    query = Client.query.filter_by(user_id=current_user.id)
    
    if search:
        query = query.filter(
            (Client.name.ilike(f'%{search}%')) |
            (Client.email.ilike(f'%{search}%')) |
            (Client.phone.ilike(f'%{search}%'))
        )
    
    clients = query.order_by(Client.name).all()
    
    return render_template('clients/list.html', clients=clients, search=search)


@clients_bp.route('/clients/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new client."""
    form = ClientForm()
    
    if form.validate_on_submit():
        client = Client(
            user_id=current_user.id,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            notes=form.notes.data
        )
        
        db.session.add(client)
        db.session.commit()
        
        log_activity(current_user.id, 'create_client', 
                    entity_type='client', entity_id=client.id,
                    details=f'Created client {client.name}')
        
        flash('Client created successfully!', 'success')
        return redirect(url_for('clients.index'))
    
    return render_template('clients/create.html', form=form)


@clients_bp.route('/clients/<int:client_id>')
@login_required
def view(client_id):
    """View client details and history."""
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    
    # Get client's invoices
    invoices = Invoice.query.filter_by(client_id=client.id)\
        .order_by(Invoice.created_at.desc()).all()
    
    # Calculate totals
    total_invoiced = sum(inv.total for inv in invoices)
    total_paid = sum(inv.amount_paid for inv in invoices)
    
    return render_template('clients/view.html', 
                         client=client,
                         invoices=invoices,
                         total_invoiced=total_invoiced,
                         total_paid=total_paid)


@clients_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    """Edit client."""
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        client.name = form.name.data
        client.email = form.email.data
        client.phone = form.phone.data
        client.address = form.address.data
        client.notes = form.notes.data
        
        db.session.commit()
        
        log_activity(current_user.id, 'update_client', 
                    entity_type='client', entity_id=client.id)
        
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients.view', client_id=client.id))
    
    return render_template('clients/create.html', form=form, client=client)


@clients_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete(client_id):
    """Delete client."""
    client = Client.query.filter_by(id=client_id, user_id=current_user.id).first_or_404()
    
    client_name = client.name
    db.session.delete(client)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_client', 
                entity_type='client', entity_id=client_id,
                details=f'Deleted client {client_name}')
    
    flash('Client deleted successfully!', 'success')
    return redirect(url_for('clients.index'))
