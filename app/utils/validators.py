"""
Input validation utilities
"""
import re
from urllib.parse import urlparse


def validate_username(username):
    """Validate username"""
    if not username or len(username) < 3:
        return False, 'Username must be at least 3 characters'
    if len(username) > 80:
        return False, 'Username must be less than 80 characters'
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, 'Username can only contain letters, numbers, underscores, and hyphens'
    return True, 'Valid'


def validate_password(password):
    """Validate password"""
    if not password or len(password) < 6:
        return False, 'Password must be at least 6 characters'
    if len(password) > 200:
        return False, 'Password is too long'
    return True, 'Valid'


def validate_email(email):
    """Validate email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(pattern, email):
        return False, 'Invalid email format'
    return True, 'Valid'


def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ''
    # Remove potentially dangerous characters
    text = text.strip()
    # This is basic sanitization - consider using bleach library for production
    return text


def validate_course_name(name):
    """Validate course name"""
    if not name or len(name) < 3:
        return False, 'Course name must be at least 3 characters'
    if len(name) > 200:
        return False, 'Course name must be less than 200 characters'
    return True, 'Valid'


def validate_question_text(text):
    """Validate question text"""
    if not text or len(text) < 10:
        return False, 'Question must be at least 10 characters'
    if len(text) > 2000:
        return False, 'Question must be less than 2000 characters'
    return True, 'Valid'


def is_safe_url(target):
    """Check if URL is safe for redirect"""
    ref_url = urlparse('http://localhost')
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
