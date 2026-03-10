"""
Admin routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.question import Question
from app.models.result import Result
from app.services.admin_service import AdminService
from app.utils.decorators import admin_required
from app.utils.validators import sanitize_input, validate_course_name, validate_question_text

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = AdminService.get_dashboard_stats()
    pending_teachers = AdminService.get_pending_teachers()
    return render_template('admin/dashboard.html', stats=stats, pending_teachers=pending_teachers)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', None)
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    
    users_paginated = query.paginate(page=page, per_page=10)
    return render_template('admin/users.html', users=users_paginated.items, pagination=users_paginated)


@admin_bp.route('/teachers/pending')
@login_required
@admin_required
def pending_teachers():
    """Pending teacher approvals"""
    pending = AdminService.get_pending_teachers()
    return render_template('admin/pending_teachers.html', pending_teachers=pending)


@admin_bp.route('/teachers/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_teacher(user_id):
    """Approve a teacher"""
    success, message = AdminService.approve_teacher(user_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.pending_teachers'))


@admin_bp.route('/teachers/reject/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_teacher(user_id):
    """Reject a teacher"""
    success, message = AdminService.reject_teacher(user_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.pending_teachers'))


@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    """Manage all courses"""
    page = request.args.get('page', 1, type=int)
    courses_paginated = Course.query.paginate(page=page, per_page=10)
    return render_template('admin/courses.html', courses=courses_paginated.items, pagination=courses_paginated)


@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete a course"""
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
    
    return redirect(url_for('admin.courses'))


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """System analytics"""
    user_stats = AdminService.get_user_statistics()
    course_stats = AdminService.get_course_statistics()
    quiz_stats = AdminService.get_quiz_statistics()
    
    # Top performers
    top_results = Result.query.order_by(Result.percentage.desc()).limit(5).all()
    
    return render_template('admin/analytics.html',
                         user_stats=user_stats,
                         course_stats=course_stats,
                         quiz_stats=quiz_stats,
                         top_results=top_results)


@admin_bp.route('/api/dashboard-stats')
@login_required
@admin_required
def api_dashboard_stats():
    """API endpoint for dashboard stats"""
    stats = AdminService.get_dashboard_stats()
    return jsonify(stats)
