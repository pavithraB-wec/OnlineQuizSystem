"""
Application entry point
"""
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Course, Quiz, Question, Attempt, Result

# Load environment variables
load_dotenv()

# Create application
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell"""
    return {
        'db': db,
        'User': User,
        'Course': Course,
        'Quiz': Quiz,
        'Question': Question,
        'Attempt': Attempt,
        'Result': Result
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized')


@app.cli.command()
def create_admin():
    """Create default admin"""
    from app.services.admin_service import AdminService
    AdminService.create_default_admin()


if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', True))
