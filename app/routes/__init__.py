"""
Routes package
"""
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.admin import admin_bp
from app.routes.teacher import teacher_bp
from app.routes.student import student_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'admin_bp',
    'teacher_bp',
    'student_bp'
]
