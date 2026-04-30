from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Job, Client
from forms import JobForm

# Define the blueprint FIRST
jobs_bp = Blueprint('jobs', __name__, template_folder='../templates/jobs')

# Then define routes
@jobs_bp.route('/')
@login_required
def index():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    return render_template('jobs/list.html', jobs=jobs)


@jobs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = JobForm()
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
        flash('Job created successfully!', 'success')
        return redirect(url_for('jobs.index'))
    return render_template('jobs/create.html', form=form, clients=clients)


# Add the missing 'view' route that your template expects
@jobs_bp.route('/<int:job_id>')
@login_required
def view(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    return render_template('jobs/view.html', job=job)


# Also add 'edit' route (optional but used in your template)
@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    form = JobForm(obj=job)
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
        flash('Job updated successfully.', 'success')
        return redirect(url_for('jobs.view', job_id=job.id))
    return render_template('jobs/create.html', form=form, clients=clients)
