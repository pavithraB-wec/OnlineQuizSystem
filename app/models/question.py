"""
Question model for quiz questions
"""
from app import db
from datetime import datetime


class Question(db.Model):
    """
    Question model - MCQ questions in a course
    """
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)  # Explanation for correct answer
    
    # Options
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    
    # Correct answer and marks
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    marks = db.Column(db.Integer, default=1)
    
    # Difficulty level
    difficulty_level = db.Column(db.String(20), default='medium')  # easy, medium, hard
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}>'
    
    def get_options_dict(self):
        """Get all options as dictionary"""
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d
        }
    
    def to_dict(self, include_answer=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'question_text': self.question_text,
            'options': self.get_options_dict(),
            'marks': self.marks,
            'difficulty_level': self.difficulty_level
        }
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
        return data
