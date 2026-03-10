"""
Quiz service for quiz-related operations
"""
from app import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt
from app.models.result import Result
from datetime import datetime
import random


class QuizService:
    """Service for quiz operations"""
    
    @staticmethod
    def create_quiz(course_id, title, description='', time_limit_minutes=60):
        """Create a new quiz"""
        try:
            quiz = Quiz(
                course_id=course_id,
                title=title,
                description=description,
                time_limit_minutes=time_limit_minutes
            )
            db.session.add(quiz)
            db.session.commit()
            return True, 'Quiz created successfully', quiz
        except Exception as e:
            db.session.rollback()
            return False, f'Error creating quiz: {str(e)}', None
    
    @staticmethod
    def update_quiz(quiz_id, **kwargs):
        """Update quiz settings"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return False, 'Quiz not found'
        
        try:
            for key, value in kwargs.items():
                if hasattr(quiz, key):
                    setattr(quiz, key, value)
            db.session.commit()
            return True, 'Quiz updated successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error updating quiz: {str(e)}'
    
    @staticmethod
    def publish_quiz(quiz_id):
        """Publish a quiz for students"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return False, 'Quiz not found'
        
        # Check if quiz has questions
        if quiz.get_total_questions() == 0:
            return False, 'Quiz must have at least one question'
        
        try:
            quiz.is_published = True
            db.session.commit()
            return True, 'Quiz published successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error publishing quiz: {str(e)}'
    
    @staticmethod
    def get_quiz_questions(quiz_id, randomize=False):
        """Get questions for a quiz"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return []
        
        questions = Question.query.filter_by(course_id=quiz.course_id, is_active=True).all()
        
        if randomize or quiz.randomize_questions:
            random.shuffle(questions)
        
        return questions
    
    @staticmethod
    def start_attempt(student_id, quiz_id):
        """Start a quiz attempt"""
        try:
            attempt = Attempt(
                student_id=student_id,
                quiz_id=quiz_id
            )
            db.session.add(attempt)
            db.session.commit()
            return True, 'Attempt started', attempt
        except Exception as e:
            db.session.rollback()
            return False, f'Error starting attempt: {str(e)}', None
    
    @staticmethod
    def submit_attempt(attempt_id, responses):
        """
        Submit a quiz attempt and calculate score
        
        Args:
            attempt_id: Attempt ID
            responses: Dict of {question_id: selected_option}
        
        Returns:
            tuple: (success, message, result)
        """
        attempt = Attempt.query.get(attempt_id)
        if not attempt:
            return False, 'Attempt not found', None
        
        quiz = attempt.quiz
        
        try:
            # Store responses
            attempt.responses = responses
            attempt.submitted_at = datetime.utcnow()
            attempt.is_submitted = True
            
            # Calculate score
            questions = Question.query.filter_by(course_id=quiz.course_id).all()
            correct_count = 0
            total_marks = 0
            marks_obtained = 0
            
            for question in questions:
                total_marks += question.marks
                question_id_str = str(question.id)
                
                if question_id_str in responses:
                    selected_option = responses[question_id_str]
                    if selected_option == question.correct_option:
                        correct_count += 1
                        marks_obtained += question.marks
                    elif quiz.enable_negative_marking:
                        marks_obtained -= (question.marks * quiz.negative_mark_percentage)
            
            # Ensure marks don't go below 0
            marks_obtained = max(0, marks_obtained)
            
            # Calculate percentage and pass/fail
            percentage = (marks_obtained / total_marks * 100) if total_marks > 0 else 0
            is_passed = percentage >= quiz.passing_percentage
            
            # Create result
            result = Result(
                student_id=attempt.student_id,
                course_id=quiz.course_id,
                attempt_id=attempt_id,
                total_questions=len(questions),
                correct_answers=correct_count,
                incorrect_answers=len(questions) - correct_count,
                unattempted=len(questions) - len(responses),
                obtained_marks=marks_obtained,
                total_marks=total_marks,
                percentage=percentage,
                is_passed=is_passed,
                time_spent_seconds=int((attempt.submitted_at - attempt.started_at).total_seconds())
            )
            
            db.session.add(result)
            db.session.commit()
            
            return True, 'Attempt submitted successfully', result
        except Exception as e:
            db.session.rollback()
            return False, f'Error submitting attempt: {str(e)}', None
    
    @staticmethod
    def get_student_attempts(student_id, quiz_id=None):
        """Get student's attempts"""
        query = Attempt.query.filter_by(student_id=student_id)
        if quiz_id:
            query = query.filter_by(quiz_id=quiz_id)
        return query.all()
    
    @staticmethod
    def get_quiz_leaderboard(course_id, limit=10):
        """Get quiz leaderboard for a course"""
        results = Result.query.filter_by(course_id=course_id).order_by(
            Result.percentage.desc(),
            Result.taken_at.asc()
        ).limit(limit).all()
        return results
