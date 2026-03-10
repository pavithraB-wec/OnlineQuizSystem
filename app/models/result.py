"""
Result model for quiz scores and analytics
"""
from app import db
from datetime import datetime


class Result(db.Model):
    """
    Result model - stores quiz results and scores
    """
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=True)
    
    # Scoring
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    incorrect_answers = db.Column(db.Integer, nullable=False, default=0)
    unattempted = db.Column(db.Integer, nullable=False, default=0)
    
    # Marks
    obtained_marks = db.Column(db.Float, nullable=False, default=0)
    total_marks = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False, default=0)
    is_passed = db.Column(db.Boolean, default=False)
    
    # Time statistics
    time_spent_seconds = db.Column(db.Integer, default=0)
    
    # Timestamps
    taken_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Result {self.id}>'
    
    def calculate_percentage(self):
        """Calculate percentage score"""
        if self.total_marks > 0:
            self.percentage = (self.obtained_marks / self.total_marks) * 100
        return self.percentage
    
    def get_grade(self):
        """Get grade based on percentage"""
        percentage = self.percentage
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_result_status(self):
        """Get result status"""
        return 'Pass' if self.is_passed else 'Fail'
    
    def get_time_spent_formatted(self):
        """Get formatted time spent"""
        minutes = self.time_spent_seconds // 60
        seconds = self.time_spent_seconds % 60
        return f'{int(minutes):02d}:{int(seconds):02d}'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'obtained_marks': self.obtained_marks,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'grade': self.get_grade(),
            'is_passed': self.is_passed,
            'time_spent': self.get_time_spent_formatted(),
            'taken_at': self.taken_at.isoformat()
        }
