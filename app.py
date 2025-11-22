from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'change_this_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oqs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------- MODELS ---------------- #

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', 'student'
    is_approved = db.Column(db.Boolean, default=True)  # teachers need approval

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref='courses')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A','B','C','D'
    marks = db.Column(db.Integer, default=1)

    course = db.relationship('Course', backref='questions')


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='results')
    course = db.relationship('Course')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------- UTILITY FUNCTIONS -------------- #

def create_default_admin():
    """Create default admin if not exists."""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            role='admin',
            is_approved=True
        )
        admin.set_password('admin123')  # default password
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: username=admin, password=admin123")


def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'


def is_teacher():
    return current_user.is_authenticated and current_user.role == 'teacher'


def is_student():
    return current_user.is_authenticated and current_user.role == 'student'


# ---------------- AUTH ROUTES ---------------- #

@app.route('/')
def home():
    if current_user.is_authenticated:
        if is_admin():
            return redirect(url_for('admin_dashboard'))
        elif is_teacher():
            return redirect(url_for('teacher_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Student or Teacher registration
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # 'student' or 'teacher'

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            role=role,
            is_approved=True if role == 'student' else False  # teacher needs approval
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == 'teacher':
            flash('Teacher registration successful. Wait for admin approval.', 'info')
        else:
            flash('Student registration successful. You can login now.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        if user.role == 'teacher' and not user.is_approved:
            flash('Your teacher account is not approved yet.', 'warning')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


# ---------------- ADMIN ROUTES ---------------- #

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    total_students = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_courses = Course.query.count()
    total_questions = Question.query.count()
    pending_teachers = User.query.filter_by(role='teacher', is_approved=False).all()

    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_courses=total_courses,
                           total_questions=total_questions,
                           pending_teachers=pending_teachers)


@app.route('/admin/approve_teacher/<int:user_id>')
@login_required
def approve_teacher(user_id):
    if not is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    teacher = User.query.get_or_404(user_id)
    teacher.is_approved = True
    db.session.commit()
    flash('Teacher approved.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/courses')
@login_required
def admin_courses():
    if not is_admin():
        flash('Access denied', 'danger')
    courses = Course.query.all()
    return render_template('course_form.html', courses=courses, mode='list', role='admin')


@app.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def admin_add_course():
    if not is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        course = Course(name=name, description=description, created_by=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Course added.', 'success')
        return redirect(url_for('admin_courses'))

    return render_template('course_form.html', mode='add', role='admin')


@app.route('/admin/courses/delete/<int:course_id>')
@login_required
def admin_delete_course(course_id):
    if not is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'info')
    return redirect(url_for('admin_courses'))


# ---------------- TEACHER ROUTES ---------------- #

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if not is_teacher():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    total_students = User.query.filter_by(role='student').count()
    total_courses = Course.query.count()
    total_questions = Question.query.count()
    return render_template('teacher_dashboard.html',
                           total_students=total_students,
                           total_courses=total_courses,
                           total_questions=total_questions)


@app.route('/teacher/courses')
@login_required
def teacher_courses():
    if not is_teacher():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    courses = Course.query.filter_by(created_by_id=current_user.id).all()
    return render_template('course_form.html', courses=courses, mode='list', role='teacher')


@app.route('/teacher/courses/add', methods=['GET', 'POST'])
@login_required
def teacher_add_course():
    if not is_teacher():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        course = Course(name=name, description=description, created_by=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Course added.', 'success')
        return redirect(url_for('teacher_courses'))

    return render_template('course_form.html', mode='add', role='teacher')


@app.route('/teacher/courses/delete/<int:course_id>')
@login_required
def teacher_delete_course(course_id):
    if not is_teacher():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)
    if course.created_by_id != current_user.id and not is_admin():
        flash('You can only delete your own courses.', 'danger')
        return redirect(url_for('teacher_courses'))

    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'info')
    return redirect(url_for('teacher_courses'))


# -------------- QUESTION MANAGEMENT (ADMIN + TEACHER) -------------- #

@app.route('/questions/<int:course_id>')
@login_required
def view_questions(course_id):
    course = Course.query.get_or_404(course_id)
    questions = Question.query.filter_by(course_id=course_id).all()
    return render_template('question_form.html', mode='list', course=course, questions=questions)


@app.route('/questions/add/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_question(course_id):
    course = Course.query.get_or_404(course_id)

    # Only admin or course creator teacher
    if is_teacher() and course.created_by_id != current_user.id:
        flash('You can only add questions to your own courses.', 'danger')
        return redirect(url_for('view_questions', course_id=course_id))

    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        marks = int(request.form['marks'])

        q = Question(
            course_id=course_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            marks=marks
        )
        db.session.add(q)
        db.session.commit()
        flash('Question added.', 'success')
        return redirect(url_for('view_questions', course_id=course_id))

    return render_template('question_form.html', mode='add', course=course)


@app.route('/questions/delete/<int:question_id>')
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    course = question.course

    if is_teacher() and course.created_by_id != current_user.id:
        flash('You can only delete questions from your own courses.', 'danger')
        return redirect(url_for('view_questions', course_id=course.id))

    db.session.delete(question)
    db.session.commit()
    flash('Question deleted.', 'info')
    return redirect(url_for('view_questions', course_id=course.id))


# ---------------- STUDENT ROUTES ---------------- #

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if not is_student():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    courses = Course.query.all()
    total_courses = len(courses)
    total_questions = Question.query.count()
    return render_template('student_dashboard.html',
                           courses=courses,
                           total_courses=total_courses,
                           total_questions=total_questions)


@app.route('/exam/<int:course_id>', methods=['GET', 'POST'])
@login_required
def exam(course_id):
    if not is_student():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)
    questions = Question.query.filter_by(course_id=course_id).all()

    if request.method == 'POST':
        score = 0
        total_marks = 0

        for q in questions:
            selected = request.form.get(f'q_{q.id}')
            total_marks += q.marks
            if selected == q.correct_option:
                score += q.marks

        result = Result(
            student_id=current_user.id,
            course_id=course_id,
            score=score,
            total_marks=total_marks
        )
        db.session.add(result)
        db.session.commit()

        flash(f'Exam submitted. You scored {score}/{total_marks}.', 'success')
        return redirect(url_for('view_results'))

    return render_template('exam.html', course=course, questions=questions)


@app.route('/results')
@login_required
def view_results():
    if not is_student():
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    results = Result.query.filter_by(student_id=current_user.id).order_by(Result.taken_at.desc()).all()
    return render_template('results.html', results=results)


# ...all routes above...

def init_database():
    with app.app_context():
        db.create_all()
        create_default_admin()

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
