"""
Main/home routes
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page - redirects based on user role"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Generic dashboard route"""
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_teacher():
        return redirect(url_for('teacher.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')


@main_bp.route('/help')
def help():
    """Help page"""
    return render_template('main/help.html')
