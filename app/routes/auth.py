from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import re
from app.models import User
from app import db
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[@$!%*#?&]", password):
        return False, "Password must contain at least one special character"
    return True, ""

def validate_username(username):
    """Validate username format"""
    if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
        return False, "Username must be 3-20 characters and contain only letters, numbers, and underscores"
    return True, ""

def validate_name(name, field="Name"):
    """Validate first/last name format"""
    if not name or len(name.strip()) < 2:
        return False, f"{field} must be at least 2 characters long"
    if not re.match(r"^[A-Za-z ]+$", name):
        return False, f"{field} must contain only letters and spaces"
    return True, ""

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').lower().strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        terms = request.form.get('terms')

        # Validate required fields
        if not all([email, username, password, confirm_password, first_name, last_name, terms]):
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[a-zA-Z]{2,}", email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/signup.html')

        # Validate first name
        valid, message = validate_name(first_name, "First name")
        if not valid:
            flash(message, 'danger')
            return render_template('auth/signup.html')

        # Validate last name
        valid, message = validate_name(last_name, "Last name")
        if not valid:
            flash(message, 'danger')
            return render_template('auth/signup.html')

        # Validate username
        valid, message = validate_username(username)
        if not valid:
            flash(message, 'danger')
            return render_template('auth/signup.html')

        # Validate password
        valid, message = validate_password(password)
        if not valid:
            flash(message, 'danger')
            return render_template('auth/signup.html')

        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')

        try:
            # Create new user
            user = User()
            user.email = email
            user.username = username
            user.password_hash = generate_password_hash(password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError:
            db.session.rollback()
            # Check if email exists
            if User.query.filter_by(email=email).first():
                flash('Email address already registered.', 'danger')
            # Check if username exists
            elif User.query.filter_by(username=username).first():
                flash('Username already taken.', 'danger')
            else:
                flash('Registration failed. Please try again.', 'danger')
            return render_template('auth/signup.html')
            
    return render_template('auth/signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is inactive. Please contact support.', 'warning')
                return render_template('auth/login.html')
                
            # Store user info in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.full_name
            
            # Update last login timestamp
            user.update_last_login()
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('main.dashboard'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    """Log out the current user."""
    # Remove specific session keys instead of clear
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
@auth.route('/profile', methods=['GET', 'POST'])
def profile():
    """Display and update user profile."""
    if not session.get('user_id'):
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        abort(404)

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        user.first_name = first_name
        user.last_name = last_name
        db.session.commit()
        
        # Update session name
        session['user_name'] = user.full_name
        
        flash('Your name has been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', user=user)
