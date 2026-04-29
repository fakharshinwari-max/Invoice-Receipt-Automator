"""Job/Project management routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Job, Client, Invoice, Expense
from forms import JobForm
from utils import log_activity

jobs_bp = Blueprint('jobs', __name__, template_folder='../templates/jobs')


@jobs_bp.route('/jobs')
@login_required
def index():
    """List all jobs."""
    status = request.args.get('status', 'all')
    client_id = request.args.get('client_id', type=int)
    
    query = Job.query.filter_by(user_id=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    jobs = query.order_by(Job.created_at.desc()).all()
    
    # Get clients for filter
    clients = Client.query.filter_by(user_id=current_user.id).all()
    
    return render_template('jobs/list.html', 
                         jobs=jobs,
                         clients=clients,
                         current_status=status,
                         current_client=client_id)


@jobs_bp.route('/jobs/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new job."""
    form = JobForm()
    
    # Populate client choices
    clients = Client.query.filter_by(user_id=current_user.id).all()
    form.client_id.choices = [(c.id, c.name) for c in clients]
    
    if form.validate_on_submit():
        job = Job(
            user_id=current_user.id,
            client_id=form.client_id.data,
            name=form.name.data,
            description=form.description.data,
            status=form.status.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data
        )
        
        db.session.add(job)
        db.session.commit()
        
        log_activity(current_user.id, 'create_job', 
                    entity_type='job', entity_id=job.id,
                    details=f'Created job {job.name}')
        
        flash('Job created successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job.id))
    
    return render_template('jobs/create.html', form=form, clients=clients)


@jobs_bp.route('/jobs/<int:job_id>')
@login_required
def view(job_id):
    """View job details with profit calculation."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    # Get linked invoices and expenses
    invoices = Invoice.query.filter_by(job_id=job.id).all()
    expenses = Expense.query.filter_by(job_id=job.id).all()
    
    # Calculate totals
    total_revenue = sum(inv.total for inv in invoices if inv.status == 'paid')
    total_expenses = sum(exp.amount for exp in expenses)
    profit = total_revenue - total_expenses
    
    # Profit margin
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return render_template('jobs/view.html', 
                         job=job,
                         invoices=invoices,
                         expenses=expenses,
                         total_revenue=total_revenue,
                         total_expenses=total_expenses,
                         profit=profit,
                         profit_margin=profit_margin)


@jobs_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(job_id):
    """Edit job."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    form = JobForm(obj=job)
    
    # Populate client choices
    clients = Client.query.filter_by(user_id=current_user.id).all()
    form.client_id.choices = [(c.id, c.name) for c in clients]
    
    if form.validate_on_submit():
        job.client_id = form.client_id.data
        job.name = form.name.data
        job.description = form.description.data
        job.status = form.status.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.budget = form.budget.data
        
        db.session.commit()
        
        log_activity(current_user.id, 'update_job', 
                    entity_type='job', entity_id=job.id)
        
        flash('Job updated successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job.id))
    
    return render_template('jobs/create.html', form=form, job=job, clients=clients)


@jobs_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete(job_id):
    """Delete job."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    job_name = job.name
    db.session.delete(job)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_job', 
                entity_type='job', entity_id=job_id,
                details=f'Deleted job {job_name}')
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('jobs.index'))


@jobs_bp.route('/jobs/<int:job_id>/complete', methods=['POST'])
@login_required
def complete(job_id):
    """Mark job as completed."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    job.status = 'completed'
    job.end_date = datetime.utcnow().date()
    db.session.commit()
    
    log_activity(current_user.id, 'complete_job', 
                entity_type='job', entity_id=job.id)
    
    flash('Job marked as completed!', 'success')
    return redirect(url_for('jobs.view', job_id=job.id))


@jobs_bp.route('/api/job-profit/<int:job_id>')
@login_required
def api_job_profit(job_id):
    """API endpoint for job profit data."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    
    invoices = Invoice.query.filter_by(job_id=job.id).all()
    expenses = Expense.query.filter_by(job_id=job.id).all()
    
    total_revenue = sum(inv.total for inv in invoices if inv.status == 'paid')
    total_expenses = sum(exp.amount for exp in expenses)
    profit = total_revenue - total_expenses
    
    return jsonify({
        'job_id': job.id,
        'job_name': job.name,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': profit,
        'profit_margin': (profit / total_revenue * 100) if total_revenue > 0 else 0
    })
