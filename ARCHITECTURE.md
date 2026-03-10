# 🏗️ Architecture Overview

## System Design Principles

This system follows enterprise-grade Flask patterns:

- **Modularity**: Separated concerns (models, services, routes)
- **Scalability**: Service layer handles business logic
- **Security**: RBAC, input validation, CSRF protection
- **Maintainability**: Clear structure and naming conventions
- **Testability**: Service layer easily mocked for testing

---

## Architectural Layers

### 1. **Presentation Layer** (Frontend)
**Responsibility**: User interface and interaction

Components:
- HTML Templates (Jinja2 templating)
- CSS Styling (Bootstrap + Custom)
- JavaScript (Client-side logic)

Files:
```
app/templates/
├── base.html                # Navigation, layout
├── auth/                    # Login, register
├── admin/                   # Admin interface
├── teacher/                 # Teacher interface
└── student/                 # Student interface
```

Technologies:
- Bootstrap 5.3 (Responsive framework)
- Font Awesome 6.4 (Icons)
- jQuery (DOM manipulation)
- Vanilla JavaScript (Timer, navigation)

---

### 2. **Application Layer** (Routes/Controllers)
**Responsibility**: Request handling, routing, authorization

Components:
- Route blueprints (Flask blueprints)
- Request validation
- Authorization decorators
- Response formatting

Files:
```
app/routes/
├── auth.py          # Authentication endpoints
├── main.py          # Home, dashboard
├── admin.py         # Admin operations
├── teacher.py       # Teacher operations
└── student.py       # Student operations
```

Key Pattern:
```python
@bp.route('/quiz/start/<quiz_id>')
@login_required
@student_required
def start_quiz(quiz_id):
    # Authorization → Service call → Template render
    quiz = QuizService.get_quiz(quiz_id)
    return render_template('quiz.html', quiz=quiz)
```

---

### 3. **Business Logic Layer** (Services)
**Responsibility**: Core application logic, calculations, validations

Components:
- Authentication service
- Admin operations service
- Quiz management service
- Utility validators

Files:
```
app/services/
├── auth_service.py          # Login, registration
├── admin_service.py         # User/course management
└── quiz_service.py          # Quiz logic, scoring

app/utils/
├── decorators.py            # Authorization decorators
└── validators.py            # Input validation
```

Key Pattern:
```python
class QuizService:
    @staticmethod
    def submit_attempt(attempt_id, responses):
        """
        1. Validate responses
        2. Calculate score
        3. Generate result
        4. Update analytics
        5. Return result
        """
        attempt = Attempt.query.get(attempt_id)
        questions = Question.query.filter_by(quiz_id=attempt.quiz_id)
        score = QuizService._calculate_score(attempt, questions, responses)
        return Result.create(attempt_id, score)
```

---

### 4. **Data Layer** (Models/ORM)
**Responsibility**: Database representation and operations

Components:
- SQLAlchemy models
- Database relationships
- Data validation
- Query methods

Files:
```
app/models/
├── user.py          # User account & auth
├── course.py        # Course container
├── quiz.py          # Quiz configuration
├── question.py      # MCQ questions
├── attempt.py       # Quiz attempt tracking
└── result.py        # Quiz results
```

Entity Relationship Diagram:
```
User (1) ───────────── (N) Course
  │                        │
  │                        ├─── (N) Question
  │                        └─── (N) Quiz
  │
  ├─── (N) Attempt
  └─── (N) Result

Attempt ────→ Quiz ────→ Question
   │                        │
   └──────────────→ Result ←┘
```

Database Relationships:
- **User → Course**: Teacher creates courses
- **Course → Quiz**: Each course has quizzes
- **Quiz → Question**: Each quiz contains questions
- **User → Attempt**: Student attempts quiz
- **Attempt → Result**: Attempt generates result

---

## Authentication Flow

```
1. User submits credentials (login.html)
                ↓
2. Route receives POST request (/login)
                ↓
3. AuthService.login_user() called
   - Validate username exists
   - Check password hash
   - Verify account status
                ↓
4. Success: Create session, redirect to dashboard
   Failure: Return error, stay on login
                ↓
5. @login_required decorator protects routes
   - Checks session.user_id
   - Allows access if authenticated
   - Redirects to login if not
```

**Key Files:**
- Route: `app/routes/auth.py`
- Service: `app/services/auth_service.py`
- Model: `app/models/user.py`
- Template: `app/templates/auth/login.html`

---

## Authorization Flow (RBAC)

```
1. User authenticated (in session)
                ↓
2. Route decorated with @admin_required (or @teacher_required)
                ↓
3. Decorator checks user.role == 'admin'
                ↓
4. Access granted: Continue to route handler
   Access denied: Redirect 403 Forbidden
```

**Decorator Implementation:**
```python
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

---

## Quiz Taking Flow

```
┌─ Student clicks "Take Quiz"
│               ↓
├─ Route: /student/quizzes/<id>/start
│  └─ Check: Student eligible?
│  └─ Service: QuizService.start_attempt()
│  └─ Database: Create Attempt record
│               ↓
├─ Render: quiz.html with questions
│  └─ JavaScript: Start timer countdown
│  └─ UI: One question per page
│               ↓
├─ Student answers and navigates
│  └─ JavaScript: Store responses in form
│               ↓
├─ Student clicks "Submit"
│  └─ Route: POST /student/attempts/<id>/submit
│  └─ Service: QuizService.submit_attempt()
│               ├─ Validate all responses
│               ├─ Calculate score per question
│               ├─ Apply negative marking
│               ├─ Determine grade
│               ├─ Create Result record
│               └─ Database: Save result
│               ↓
└─ Redirect: View result page (result.html)
   └─ Display: Score, grade, answer analysis
```

---

## Database Design

### Normalization
- **1NF**: Atomic columns (no repeating groups)
- **2NF**: No partial dependencies
- **3NF**: No transitive dependencies

### Indexes (Performance)
```python
# Indexed columns in models
user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
email = db.Column(db.String(120), unique=True, index=True)
created_at = db.Column(db.DateTime, index=True)
```

### Constraints
```python
# Foreign keys with cascading deletes
questions = db.relationship('Question', cascade='all, delete-orphan')

# Unique constraints
__table_args__ = (
    db.UniqueConstraint('user_id', 'quiz_id', name='unique_attempt'),
)

# Check constraints
percentage = db.Column(db.Float, default=0)
# CHECK (percentage >= 0 AND percentage <= 100)
```

---

## Configuration Management

### Three Environment Levels

```
Development (config.py - DevelopmentConfig)
├─ Debug: True
├─ SQLite: Local file
├─ Logging: Verbose
└─ CSRF: Disabled (optional)

Testing (config.py - TestingConfig)
├─ Debug: False
├─ SQLite: In-memory
├─ Logging: Minimal
└─ CSRF: Disabled

Production (config.py - ProductionConfig)
├─ Debug: False
├─ PostgreSQL: Remote
├─ Logging: Essential only
├─ CSRF: Enabled
└─ HTTPS: Required
```

**Switching Environments:**
```bash
# Development (default)
FLASK_ENV=development python run.py

# Testing
FLASK_ENV=testing pytest

# Production
FLASK_ENV=production python run.py
```

---

## Security Architecture

### 1. **Authentication**
- Password hashing: werkzeug.security
- Session management: Flask-Login
- Cookie security: HttpOnly, Secure, SameSite

### 2. **Authorization**
- Role-based access control (RBAC)
- Route decorators enforce access
- Three roles: admin, teacher, student

### 3. **Data Protection**
- CSRF tokens on all forms (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (Jinja2 escaping)

### 4. **Input Validation**
```python
# app/utils/validators.py
validate_username()      # Not empty, alphanumeric
validate_password()      # Min 8 chars, complexity
validate_email()         # RFC 5322 format
validate_question_text() # Not empty, length
sanitize_input()         # Remove dangerous chars
```

---

## Performance Optimization

### Query Optimization
```python
# ✅ Good: Eager loading with relationships
student = User.query.options(
    db.joinedload('attempts'),
    db.joinedload('results')
).get(student_id)

# ❌ Bad: N+1 query problem
for attempt in Attempt.query.all():
    quiz = Quiz.query.get(attempt.quiz_id)  # Query per row!
```

### Caching Strategy
```python
# Future: Flask-Caching implementation
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/leaderboard/<course_id>')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_leaderboard(course_id):
    return QuizService.get_quiz_leaderboard(course_id)
```

### Database Indexing
- All foreign keys are indexed
- User email indexed for login
- Timestamps indexed for sorting
- Quiz status indexed for queries

---

## Error Handling

### Exception Hierarchy
```
Exception
├── ValidationError
│   ├── InvalidUsername
│   ├── InvalidPassword
│   └── InvalidQuestion
├── AuthorizationError
│   └── InsufficientPermissions
└── DataError
    ├── UserNotFound
    └── QuizNotFound
```

### Error Response Pattern
```python
try:
    user = AuthService.login_user(username, password)
    return redirect('/dashboard')
except ValidationError as e:
    flash(f'Validation error: {str(e)}', 'danger')
    return redirect('/login')
except Exception as e:
    logger.error(f'Unexpected error: {str(e)}')
    flash('An unexpected error occurred', 'danger')
    return redirect('/login')
```

---

## Frontend Architecture

### Template Hierarchy
```
base.html (Navbar, Layout)
├── auth/login.html
├── auth/register.html
├── admin/
│   ├── dashboard.html (extends base.html)
│   ├── users.html
│   └── courses.html
├── teacher/
│   ├── dashboard.html
│   └── course_form.html
└── student/
    ├── quiz.html (Interactive)
    ├── result.html (Results display)
    └── leaderboard.html

JavaScript Modules:
└── app/static/
    ├── quiz-timer.js      (Timer logic)
    ├── quiz-navigation.js (Question nav)
    ├── analytics.js       (Charts/graphs)
    └── utils.js           (Helpers)
```

### State Management (Frontend)
```javascript
// Quiz state in JavaScript
const quizState = {
    currentQuestion: 0,
    totalQuestions: 10,
    responses: {},          // question_id: answer
    timeRemaining: 1800,    // seconds
    isSubmitted: false
};

// Update on question navigation
function nextQuestion() {
    quizState.currentQuestion++;
    renderQuestion(quizState.currentQuestion);
}
```

---

## API Contracts (Routes)

### RESTful Conventions Used
```
GET  /resource           → List resources
GET  /resource/<id>      → Get single resource
POST /resource           → Create resource
POST /resource/<id>      → Update resource (convention)
GET  /resource/<id>/delete → Delete resource (web form compatible)
```

### JSON API Endpoints (Future)
```
GET  /api/v1/courses
GET  /api/v1/courses/<id>
POST /api/v1/quizzes/<id>/attempt
GET  /api/v1/results/<id>
```

---

## Testing Architecture (Future)

```
tests/
├── unit/
│   ├── test_models.py          # Model logic
│   ├── test_services.py        # Service logic
│   └── test_validators.py      # Validation
├── integration/
│   ├── test_auth_flow.py       # Full auth
│   ├── test_quiz_flow.py       # Full quiz
│   └── test_database.py        # DB operations
└── conftest.py                 # Pytest fixtures
```

---

## Deployment Architecture

### Single Machine (Development)
```
localhost:5000
├── Python Flask app
├── SQLite database
└── Static files
```

### Scalable Deployment (Production)
```
Load Balancer
├── App Server 1 (Flask + Gunicorn)
├── App Server 2 (Flask + Gunicorn)
└── App Server 3 (Flask + Gunicorn)
        ↓
PostgreSQL Database (Primary + Replica)
        ↓
Redis Cache (Optional)
        ↓
CDN for Static Files
```

---

## Data Flow Diagram

```
User Request (Browser)
        ↓
URL Routing (Flask)
        ↓
Route Handler (Blueprint)
        ↓
Authorization Check (@decorators)
        ↓
Business Logic (Services)
        ↓
Database Query (Models/SQLAlchemy)
        ↓
Database (SQLite/PostgreSQL)
        ↓
Response Processing (Services)
        ↓
Template Rendering (Jinja2)
        ↓
HTML Response (Browser)
        ↓
Client-side JavaScript (Enhancement)
```

---

## Scalability Considerations

### Current Capacity
- **Single server**: ~100 concurrent users
- **Database**: SQLite supports basic operations
- **Sessions**: In-memory Flask sessions

### Scaling Strategies

#### Horizontal Scaling
1. Load balancer (Nginx/HAProxy)
2. Multiple app servers
3. Shared session store (Redis)
4. Shared database (PostgreSQL)

#### Vertical Scaling
1. Larger server instances
2. More memory for caching
3. Database optimization
4. Query result caching

#### Database Scaling
1. Read replicas for analytics queries
2. Indexing strategy
3. Query optimization
4. Connection pooling

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Bootstrap | 5.3 | UI Framework |
| Frontend | jQuery | 3.6+ | DOM manipulation |
| Frontend | Font Awesome | 6.4 | Icons |
| Backend | Flask | 3.0.0 | Web framework |
| Backend | SQLAlchemy | 2.0+ | ORM |
| Auth | Flask-Login | 0.6.3 | Session management |
| Forms | Flask-WTF | 1.2.0+ | CSRF, forms |
| Database | SQLite/PostgreSQL | Latest | Persistence |
| Server | Gunicorn | Latest | Production WSGI |
| Deployment | Docker | (Optional) | Containerization |

---

## Future Enhancements

### Short Term (v2.1)
- Email notifications
- CSV import for questions
- Quiz scheduling enforcement
- Advanced analytics dashboard

### Medium Term (v2.5)
- Mobile app (React Native)
- Real-time notifications (WebSockets)
- Question versioning
- Bulk operations API

### Long Term (v3.0)
- AI-powered question generation
- Proctoring integration
- Certificate generation
- Advanced LMS integration

---

**Version 2.0** | Production Ready ✅
