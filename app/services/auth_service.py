"""
Authentication service
"""
from app import db
from app.models.user import User
from app.utils.validators import validate_username, validate_password, validate_email, sanitize_input


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register_user(username, password, role='student', email=None, full_name=None):
        """
        Register a new user
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        # Validate input
        is_valid, msg = validate_username(username)
        if not is_valid:
            return False, msg, None
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            return False, msg, None
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            return False, 'Username already exists', None
        
        # Check email if provided
        if email:
            is_valid, msg = validate_email(email)
            if not is_valid:
                return False, msg, None
            if User.query.filter_by(email=email).first():
                return False, 'Email already exists', None
        
        try:
            user = User(
                username=sanitize_input(username),
                email=email,
                full_name=sanitize_input(full_name) if full_name else None,
                role=role,
                is_approved=True if role == 'student' else False
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, 'User registered successfully', user
        except Exception as e:
            db.session.rollback()
            return False, f'Error registering user: {str(e)}', None
    
    @staticmethod
    def login_user(username, password):
        """
        Authenticate user
        
        Returns:
            tuple: (success: bool, message: str, user: User or None)
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, 'Invalid username or password', None
        
        if not user.check_password(password):
            return False, 'Invalid username or password', None
        
        if not user.is_active:
            return False, 'Your account is inactive', None
        
        if user.role == 'teacher' and not user.is_approved:
            return False, 'Your teacher account is not approved yet', None
        
        return True, 'Login successful', user
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not user.check_password(old_password):
            return False, 'Current password is incorrect'
        
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return False, msg
        
        try:
            user.set_password(new_password)
            db.session.commit()
            return True, 'Password changed successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error changing password: {str(e)}'
