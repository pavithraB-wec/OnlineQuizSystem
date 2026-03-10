"""
Teacher routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.course import Course
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.result import Result
from app.services.quiz_service import QuizService
from app.utils.decorators import teacher_required
from app.utils.validators import sanitize_input, validate_course_name, validate_question_text

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    """Teacher dashboard"""
    courses = Course.query.filter_by(created_by_id=current_user.id).all()
    total_courses = len(courses)
    total_questions = sum(c.get_total_questions() for c in courses)
    total_quizzes = sum(c.get_total_quizzes() for c in courses)
    
    # Get student results for teacher's courses
    course_ids = [c.id for c in courses]
    total_results = Result.query.filter(Result.course_id.in_(course_ids)).count() if course_ids else 0
    
    return render_template('teacher/dashboard.html',
                         total_courses=total_courses,
                         total_questions=total_questions,
                         total_quizzes=total_quizzes,
                         total_results=total_results,
                         courses=courses)


@teacher_bp.route('/courses')
@login_required
@teacher_required
def courses():
    """Teacher's courses"""
    page = request.args.get('page', 1, type=int)
    courses_paginated = Course.query.filter_by(created_by_id=current_user.id).paginate(page=page, per_page=10)
    return render_template('teacher/courses.html', courses=courses_paginated.items, pagination=courses_paginated)


@teacher_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_course():
    """Create a new course"""
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        description = sanitize_input(request.form.get('description', ''))
        
        is_valid, message = validate_course_name(name)
        if not is_valid:
            flash(message, 'danger')
            return redirect(url_for('teacher.create_course'))
        
        try:
            course = Course(
                name=name,
                description=description,
                created_by_id=current_user.id
            )
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully', 'success')
            return redirect(url_for('teacher.courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating course: {str(e)}', 'danger')
    
    return render_template('teacher/course_form.html')


@teacher_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_course(course_id):
    """Edit a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check authorization
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    if request.method == 'POST':
        course.name = sanitize_input(request.form.get('name', course.name))
        course.description = sanitize_input(request.form.get('description', ''))
        
        try:
            db.session.commit()
            flash('Course updated successfully', 'success')
            return redirect(url_for('teacher.courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'danger')
    
    return render_template('teacher/course_form.html', course=course)


@teacher_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_course(course_id):
    """Delete a course"""
    course = Course.query.get_or_404(course_id)
    
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
    
    return redirect(url_for('teacher.courses'))


@teacher_bp.route('/courses/<int:course_id>/questions')
@login_required
@teacher_required
def course_questions(course_id):
    """Manage questions for a course"""
    course = Course.query.get_or_404(course_id)
    
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    page = request.args.get('page', 1, type=int)
    questions_paginated = Question.query.filter_by(course_id=course_id).paginate(page=page, per_page=10)
    
    return render_template('teacher/questions.html',
                         course=course,
                         questions=questions_paginated.items,
                         pagination=questions_paginated)


@teacher_bp.route('/courses/<int:course_id>/questions/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_question(course_id):
    """Add a question"""
    course = Course.query.get_or_404(course_id)
    
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    if request.method == 'POST':
        question_text = sanitize_input(request.form.get('question_text', ''))
        option_a = sanitize_input(request.form.get('option_a', ''))
        option_b = sanitize_input(request.form.get('option_b', ''))
        option_c = sanitize_input(request.form.get('option_c', ''))
        option_d = sanitize_input(request.form.get('option_d', ''))
        correct_option = request.form.get('correct_option', 'A')
        marks = int(request.form.get('marks', 1))
        difficulty_level = request.form.get('difficulty_level', 'medium')
        explanation = sanitize_input(request.form.get('explanation', ''))
        
        is_valid, message = validate_question_text(question_text)
        if not is_valid:
            flash(message, 'danger')
            return redirect(url_for('teacher.add_question', course_id=course_id))
        
        try:
            question = Question(
                course_id=course_id,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                marks=marks,
                difficulty_level=difficulty_level,
                explanation=explanation
            )
            db.session.add(question)
            db.session.commit()
            flash('Question added successfully', 'success')
            return redirect(url_for('teacher.course_questions', course_id=course_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding question: {str(e)}', 'danger')
    
    return render_template('teacher/question_form.html', course=course)


@teacher_bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_question(question_id):
    """Edit a question"""
    question = Question.query.get_or_404(question_id)
    course = question.course
    
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    if request.method == 'POST':
        question.question_text = sanitize_input(request.form.get('question_text', question.question_text))
        question.option_a = sanitize_input(request.form.get('option_a', question.option_a))
        question.option_b = sanitize_input(request.form.get('option_b', question.option_b))
        question.option_c = sanitize_input(request.form.get('option_c', question.option_c))
        question.option_d = sanitize_input(request.form.get('option_d', question.option_d))
        question.correct_option = request.form.get('correct_option', question.correct_option)
        question.marks = int(request.form.get('marks', question.marks))
        question.difficulty_level = request.form.get('difficulty_level', question.difficulty_level)
        question.explanation = sanitize_input(request.form.get('explanation', ''))
        
        try:
            db.session.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('teacher.course_questions', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'danger')
    
    return render_template('teacher/question_form.html', course=course, question=question)


@teacher_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_question(question_id):
    """Delete a question"""
    question = Question.query.get_or_404(question_id)
    course = question.course
    
    if course.created_by_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('teacher.courses'))
    
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'danger')
    
    return redirect(url_for('teacher.course_questions', course_id=course.id))


@teacher_bp.route('/results')
@login_required
@teacher_required
def results():
    """View student results for teacher's courses"""
    courses = Course.query.filter_by(created_by_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    
    page = request.args.get('page', 1, type=int)
    results_paginated = Result.query.filter(Result.course_id.in_(course_ids)).order_by(
        Result.taken_at.desc()
    ).paginate(page=page, per_page=20) if course_ids else None
    
    return render_template('teacher/results.html',
                         courses=courses,
                         results_paginated=results_paginated)
