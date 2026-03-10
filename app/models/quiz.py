"""
Quiz model for exam configuration
"""
from app import db
from datetime import datetime


class Quiz(db.Model):
    """
    Quiz model - represents an examination
    """
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Quiz settings
    time_limit_minutes = db.Column(db.Integer, default=60)  # Quiz duration
    enable_negative_marking = db.Column(db.Boolean, default=False)
    negative_mark_percentage = db.Column(db.Float, default=0.25)  # 25% of marks for wrong answer
    randomize_questions = db.Column(db.Boolean, default=False)
    show_correct_answers = db.Column(db.Boolean, default=False)  # Show answers after submission
    passing_percentage = db.Column(db.Float, default=50.0)  # Passing score percentage
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    scheduled_at = db.Column(db.DateTime, nullable=True)  # When quiz opens
    closes_at = db.Column(db.DateTime, nullable=True)  # When quiz closes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('Attempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Quiz {self.title}>'
    
    def is_available(self):
        """Check if quiz is available for students to attempt"""
        now = datetime.utcnow()
        if not self.is_published or not self.is_active:
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.closes_at and now > self.closes_at:
            return False
        return True
    
    def get_total_questions(self):
        """Get total questions in this quiz"""
        from app.models.question import Question
        return Question.query.filter_by(course_id=self.course_id).count()
    
    def get_total_marks(self):
        """Get total marks for this quiz"""
        from app.models.question import Question
        questions = Question.query.filter_by(course_id=self.course_id).all()
        return sum(q.marks for q in questions)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'time_limit_minutes': self.time_limit_minutes,
            'total_questions': self.get_total_questions(),
            'total_marks': self.get_total_marks(),
            'is_published': self.is_published,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat()
        }
