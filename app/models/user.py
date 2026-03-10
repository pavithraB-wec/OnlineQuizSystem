"""
User model for authentication and role management
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    """
    User model supporting three roles: admin, teacher, student
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, teacher, student
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=True)  # Teachers need approval
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_courses = db.relationship('Course', backref='creator', lazy='dynamic', foreign_keys='Course.created_by_id')
    attempts = db.relationship('Attempt', backref='student', lazy='dynamic', foreign_keys='Attempt.student_id')
    results = db.relationship('Result', backref='student', lazy='dynamic', foreign_keys='Result.student_id')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin' and self.is_active
    
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == 'teacher' and self.is_active and self.is_approved
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student' and self.is_active
    
    def can_edit_course(self, course):
        """Check if user can edit a course"""
        if self.is_admin():
            return True
        return self.id == course.created_by_id
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat()
        }
