"""
Admin service for admin operations
"""
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.question import Question
from app.models.result import Result
from app.models.quiz import Quiz
from sqlalchemy import func


class AdminService:
    """Service for admin operations"""
    
    @staticmethod
    def create_default_admin():
        """Create default admin if not exists"""
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@quizsystem.local',
                role='admin',
                is_approved=True,
                full_name='System Administrator'
            )
            admin.set_password('admin@123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Default admin created: username=admin, password=admin@123')
            return admin
        return None
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        return {
            'total_users': User.query.count(),
            'total_students': User.query.filter_by(role='student').count(),
            'total_teachers': User.query.filter_by(role='teacher').count(),
            'total_courses': Course.query.count(),
            'total_questions': Question.query.count(),
            'total_quizzes': Quiz.query.count(),
            'pending_teachers': User.query.filter_by(role='teacher', is_approved=False).count(),
            'total_attempts': 0,  # From Attempt model
            'total_results': Result.query.count()
        }
    
    @staticmethod
    def approve_teacher(user_id):
        """Approve a teacher"""
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found'
        if user.role != 'teacher':
            return False, 'User is not a teacher'
        
        try:
            user.is_approved = True
            db.session.commit()
            return True, 'Teacher approved successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error approving teacher: {str(e)}'
    
    @staticmethod
    def reject_teacher(user_id):
        """Reject/delete a teacher"""
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found'
        if user.role != 'teacher':
            return False, 'User is not a teacher'
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True, 'Teacher rejected and deleted'
        except Exception as e:
            db.session.rollback()
            return False, f'Error rejecting teacher: {str(e)}'
    
    @staticmethod
    def get_pending_teachers():
        """Get pending teacher approvals"""
        return User.query.filter_by(role='teacher', is_approved=False).all()
    
    @staticmethod
    def get_all_users(role=None):
        """Get all users, optionally filtered by role"""
        query = User.query
        if role:
            query = query.filter_by(role=role)
        return query.all()
    
    @staticmethod
    def get_user_statistics():
        """Get detailed user statistics"""
        return {
            'users_by_role': {
                'admin': User.query.filter_by(role='admin').count(),
                'teacher': User.query.filter_by(role='teacher').count(),
                'student': User.query.filter_by(role='student').count()
            },
            'approved_teachers': User.query.filter_by(role='teacher', is_approved=True).count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'inactive_users': User.query.filter_by(is_active=False).count()
        }
    
    @staticmethod
    def get_course_statistics():
        """Get course statistics"""
        courses = Course.query.all()
        return {
            'total_courses': len(courses),
            'total_questions': Question.query.count(),
            'average_questions_per_course': Question.query.count() / len(courses) if courses else 0,
            'average_course_size': sum(c.get_total_questions() for c in courses) / len(courses) if courses else 0
        }
    
    @staticmethod
    def get_quiz_statistics():
        """Get quiz statistics"""
        quizzes = Quiz.query.all()
        return {
            'total_quizzes': len(quizzes),
            'published_quizzes': Quiz.query.filter_by(is_published=True).count(),
            'active_quizzes': Quiz.query.filter_by(is_active=True).count(),
            'average_time_limit': sum(q.time_limit_minutes for q in quizzes) / len(quizzes) if quizzes else 0
        }
