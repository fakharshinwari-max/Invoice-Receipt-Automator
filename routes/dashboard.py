"""Dashboard routes."""

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Invoice, Expense, Client, Job
from utils import calculate_dashboard_stats
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with statistics and charts."""
    # Calculate stats
    stats = calculate_dashboard_stats(current_user.id)
    
    # Get recent invoices
    recent_invoices = Invoice.query.filter_by(user_id=current_user.id)\
        .order_by(Invoice.created_at.desc()).limit(5).all()
    
    # Get recent expenses
    recent_expenses = Expense.query.filter_by(user_id=current_user.id)\
        .order_by(Expense.date.desc()).limit(5).all()
    
    # Get active jobs
    active_jobs = Job.query.filter_by(user_id=current_user.id, status='active')\
        .order_by(Job.created_at.desc()).limit(5).all()
    
    # Get top clients by revenue
    top_clients = db.session.query(
        Client,
        db.func.sum(Invoice.total).label('total_revenue')
    ).join(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == 'paid'
    ).group_by(Client.id).order_by(db.desc('total_revenue')).limit(5).all()
    
    # Monthly revenue vs expenses data (last 6 months)
    monthly_data = get_monthly_data(current_user.id)
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_invoices=recent_invoices,
                         recent_expenses=recent_expenses,
                         active_jobs=active_jobs,
                         top_clients=top_clients,
                         monthly_data=monthly_data)


def get_monthly_data(user_id, months=6):
    """Get monthly revenue and expenses data for charts."""
    now = datetime.utcnow()
    data = {
        'labels': [],
        'revenue': [],
        'expenses': []
    }
    
    for i in range(months - 1, -1, -1):
        # Calculate month start and end
        if now.month - i <= 0:
            month = now.month - i + 12
            year = now.year - 1
        else:
            month = now.month - i
            year = now.year
        
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        # Get revenue (paid invoices)
        revenue = db.session.query(db.func.sum(Invoice.amount_paid)).filter(
            Invoice.user_id == user_id,
            Invoice.status == 'paid',
            Invoice.paid_date >= month_start.date(),
            Invoice.paid_date < month_end.date()
        ).scalar() or 0
        
        # Get expenses
        expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= month_start.date(),
            Expense.date < month_end.date()
        ).scalar() or 0
        
        # Format label
        label = month_start.strftime('%b %Y')
        
        data['labels'].append(label)
        data['revenue'].append(float(revenue))
        data['expenses'].append(float(expenses))
    
    return data


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard stats."""
    stats = calculate_dashboard_stats(current_user.id)
    return jsonify(stats)


@dashboard_bp.route('/api/monthly-data')
@login_required
def api_monthly_data():
    """API endpoint for monthly chart data."""
    data = get_monthly_data(current_user.id)
    return jsonify(data)
