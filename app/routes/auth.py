"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.validators import sanitize_input

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        success, message, user = AuthService.login_user(username, password)
        
        if success:
            login_user(user, remember=bool(remember))
            flash(message, 'success')
            next_page = request.args.get('next')
            if not next_page or next_page.startswith('/'):
                return redirect(next_page or url_for('main.home'))
            return redirect(url_for('main.home'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')
        full_name = sanitize_input(request.form.get('full_name', ''))
        
        # Validate inputs
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if role not in ['student', 'teacher']:
            flash('Invalid role', 'danger')
            return redirect(url_for('auth.register'))
        
        # Register user
        success, message, user = AuthService.register_user(
            username=username,
            password=password,
            role=role,
            email=email if email else None,
            full_name=full_name if full_name else None
        )
        
        if success:
            flash(message, 'success')
            if role == 'teacher':
                flash('Teacher registration successful. Wait for admin approval.', 'info')
            else:
                flash('You can now log in.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile view"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        success, message = AuthService.change_password(current_user, old_password, new_password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/change_password.html')
