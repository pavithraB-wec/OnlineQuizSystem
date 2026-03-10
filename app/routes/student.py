"""
Student routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.course import Course
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.attempt import Attempt
from app.models.result import Result
from app.services.quiz_service import QuizService
from app.utils.decorators import student_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    courses = Course.query.filter_by(is_active=True).all()
    total_courses = len(courses)
    
    # Get student's results
    results = Result.query.filter_by(student_id=current_user.id).all()
    total_attempts = len(results)
    average_score = sum(r.percentage for r in results) / len(results) if results else 0
    
    # Get recent results
    recent_results = Result.query.filter_by(student_id=current_user.id).order_by(
        Result.taken_at.desc()
    ).limit(5).all()
    
    return render_template('student/dashboard.html',
                         total_courses=total_courses,
                         total_attempts=total_attempts,
                         average_score=average_score,
                         recent_results=recent_results,
                         courses=courses[:6])  # Show first 6 courses


@student_bp.route('/courses')
@login_required
@student_required
def courses():
    """Browse all courses"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Course.query.filter_by(is_active=True)
    if search:
        query = query.filter(Course.name.icontains(search))
    
    courses_paginated = query.paginate(page=page, per_page=10)
    return render_template('student/courses.html',
                         courses=courses_paginated.items,
                         pagination=courses_paginated,
                         search=search)


@student_bp.route('/courses/<int:course_id>')
@login_required
@student_required
def course_detail(course_id):
    """View course details"""
    course = Course.query.get_or_404(course_id)
    quizzes = Quiz.query.filter_by(course_id=course_id, is_active=True).all()
    
    # Get student's results for this course
    student_results = Result.query.filter_by(
        student_id=current_user.id,
        course_id=course_id
    ).all()
    
    best_score = max(r.percentage for r in student_results) if student_results else 0
    total_attempts = len(student_results)
    average_score = sum(r.percentage for r in student_results) / len(student_results) if student_results else 0
    
    return render_template('student/course_detail.html',
                         course=course,
                         quizzes=quizzes,
                         best_score=best_score,
                         total_attempts=total_attempts,
                         average_score=average_score)


@student_bp.route('/quizzes/<int:quiz_id>/start')
@login_required
@student_required
def start_quiz(quiz_id):
    """Start a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not quiz.is_available():
        flash('This quiz is not available', 'danger')
        return redirect(url_for('student.courses'))
    
    success, message, attempt = QuizService.start_attempt(current_user.id, quiz_id)
    
    if success:
        return redirect(url_for('student.take_quiz', attempt_id=attempt.id))
    else:
        flash(message, 'danger')
        return redirect(url_for('student.courses'))


@student_bp.route('/attempts/<int:attempt_id>')
@login_required
@student_required
def take_quiz(attempt_id):
    """Take a quiz"""
    attempt = Attempt.query.get_or_404(attempt_id)
    
    # Check authorization
    if attempt.student_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Check if already submitted
    if attempt.is_submitted:
        flash('This quiz attempt has already been submitted', 'info')
        return redirect(url_for('student.view_result', result_id=attempt.results[0].id))
    
    quiz = attempt.quiz
    questions = QuizService.get_quiz_questions(quiz.id, randomize=quiz.randomize_questions)
    
    return render_template('student/quiz.html',
                         attemptid=attempt,
                         quiz=quiz,
                         questions=questions)


@student_bp.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@login_required
@student_required
def submit_quiz(attempt_id):
    """Submit quiz answers"""
    attempt = Attempt.query.get_or_404(attempt_id)
    
    if attempt.student_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('student.dashboard'))
    
    if attempt.is_submitted:
        flash('Quiz already submitted', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # Get responses from form
    responses = {}
    for key, value in request.form.items():
        if key.startswith('q_'):
            question_id = key.replace('q_', '')
            responses[question_id] = value
    
    # Submit attempt
    success, message, result = QuizService.submit_attempt(attempt_id, responses)
    
    if success:
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('student.view_result', result_id=result.id))
    else:
        flash(message, 'danger')
        return redirect(url_for('student.take_quiz', attempt_id=attempt_id))


@student_bp.route('/results/<int:result_id>')
@login_required
@student_required
def view_result(result_id):
    """View quiz result"""
    result = Result.query.get_or_404(result_id)
    
    if result.student_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get attempt details for answers
    attempt = Attempt.query.get(result.attempt_id) if result.attempt_id else None
    
    # Get questions and prepare detailed analysis
    questions = Question.query.filter_by(course_id=result.course_id).all()
    questions_analysis = []
    
    if attempt:
        for question in questions:
            selected_option = attempt.responses.get(str(question.id))
            is_correct = selected_option == question.correct_option
            
            questions_analysis.append({
                'question': question,
                'selected': selected_option,
                'is_correct': is_correct,
                'marks_obtained': question.marks if is_correct else 0
            })
    
    return render_template('student/result.html',
                         result=result,
                         questions_analysis=questions_analysis)


@student_bp.route('/results')
@login_required
@student_required
def results():
    """View all attempts/results"""
    page = request.args.get('page', 1, type=int)
    
    results_paginated = Result.query.filter_by(
        student_id=current_user.id
    ).order_by(Result.taken_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('student/results.html',
                         results_paginated=results_paginated)


@student_bp.route('/leaderboard/<int:course_id>')
@login_required
@student_required
def leaderboard(course_id):
    """View course leaderboard"""
    course = Course.query.get_or_404(course_id)
    leaderboard_data = QuizService.get_quiz_leaderboard(course_id, limit=50)
    
    return render_template('student/leaderboard.html',
                         course=course,
                         leaderboard=leaderboard_data)


@student_bp.route('/api/progress/<int:attempt_id>')
@login_required
@student_required
def api_quiz_progress(attempt_id):
    """API endpoint for quiz progress"""
    attempt = Attempt.query.get_or_404(attempt_id)
    
    if attempt.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quiz = attempt.quiz
    elapsed_seconds = (datetime.utcnow() - attempt.started_at).total_seconds()
    remaining_seconds = max(0, quiz.time_limit_minutes * 60 - elapsed_seconds)
    
    return jsonify({
        'elapsed': int(elapsed_seconds),
        'remaining': int(remaining_seconds),
        'is_submitted': attempt.is_submitted
    })


from datetime import datetime
