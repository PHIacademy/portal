from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import Subject, User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page route showing login page"""
    return render_template('auth/login.html')

@bp.route('/dashboard')
def dashboard():
    """Dashboard page showing all subjects"""
    # Check if user is logged in
    if not session.get('user_id'):
        flash('You need to login to access the dashboard.', 'warning')
        return redirect(url_for('auth.login'))
        
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('index.html', subjects=subjects,
                         user={'first_name': session.get('user_name').split()[0],
                               'last_name': ' '.join(session.get('user_name').split()[1:])})