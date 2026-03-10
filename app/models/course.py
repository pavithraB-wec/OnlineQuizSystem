"""
Course model for quiz organization
"""
from app import db
from datetime import datetime


class Course(db.Model):
    """
    Course model - a collection of quizzes
    """
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('Result', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.name}>'
    
    def get_total_questions(self):
        """Get total questions in this course"""
        return Question.query.filter_by(course_id=self.id).count()
    
    def get_total_quizzes(self):
        """Get total quizzes in this course"""
        return Quiz.query.filter_by(course_id=self.id).count()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by_id': self.created_by_id,
            'total_questions': self.get_total_questions(),
            'total_quizzes': self.get_total_quizzes(),
            'created_at': self.created_at.isoformat()
        }


# Import here to avoid circular imports
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.result import Result
