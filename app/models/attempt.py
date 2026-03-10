"""
Attempt model for tracking quiz attempts
"""
from app import db
from datetime import datetime


class Attempt(db.Model):
    """
    Attempt model - tracks when students attempt quizzes
    """
    __tablename__ = 'attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
    
    # Attempt details
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    time_spent_seconds = db.Column(db.Integer, default=0)  # Total time spent
    
    # Responses (JSON format)
    responses = db.Column(db.JSON, default={})  # {question_id: selected_option}
    
    # Status
    is_submitted = db.Column(db.Boolean, default=False)
    is_auto_submitted = db.Column(db.Boolean, default=False)  # Auto-submitted due to timeout
    
    # Relationships
    results = db.relationship('Result', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Attempt {self.id}>'
    
    def get_duration(self):
        """Get duration of attempt in minutes"""
        if self.submitted_at:
            elapsed = self.submitted_at - self.started_at
            return elapsed.total_seconds() / 60
        return None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'quiz_id': self.quiz_id,
            'started_at': self.started_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_spent_seconds': self.time_spent_seconds,
            'is_submitted': self.is_submitted,
            'is_auto_submitted': self.is_auto_submitted
        }
