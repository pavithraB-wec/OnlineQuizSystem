# Online Quiz System - Professional Edition

## 🎓 Project Overview

**QuizMaster** is a professional, production-ready online quiz system built with Python Flask, featuring a modern backend architecture, responsive UI, and comprehensive quiz management capabilities.

### Key Features

#### 👥 User Roles
- **Admin**: Full system control, user management, analytics
- **Teacher**: Create courses, manage questions, view student results
- **Student**: Take quizzes, view results, track progress, access leaderboard

#### 📚 Quiz Management
- Create and manage quizzes with custom settings
- Support for MCQ (Multiple Choice Questions)
- Question difficulty levels (Easy, Medium, Hard)
- Question explanations
- Customizable time limits per quiz
- Randomize questions option
- Negative marking support
- Auto-submit on timer end

#### 📊 Student Features
- Take quizzes with timer and progress bar
- One-question-per-page navigation
- Instant score calculation
- View detailed results with answer analysis
- Track attempt history
- Course-wise analytics
- Leaderboard rankings
- Score percentage and grades

#### 👨‍🏫 Teacher Features
- Create and manage courses
- Add/edit/delete questions
- View student results and analytics
- Export student performance data (future)

#### 🔒 Security Features
- Password hashing with werkzeug
- CSRF protection (Flask-WTF)
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- Session management
- Secure cookies

---

## 📁 Project Structure

```
OnlineQuizSystem/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── course.py            # Course model
│   │   ├── quiz.py              # Quiz model
│   │   ├── question.py          # Question model
│   │   ├── attempt.py           # Attempt tracking
│   │   └── result.py            # Quiz results
│   ├── routes/                  # Route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Main routes
│   │   ├── admin.py             # Admin routes
│   │   ├── teacher.py           # Teacher routes
│   │   └── student.py           # Student routes
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication service
│   │   ├── admin_service.py     # Admin operations
│   │   └── quiz_service.py      # Quiz logic
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── decorators.py        # Auth decorators
│   │   └── validators.py        # Input validators
│   ├── templates/               # HTML templates
│   │   ├── base.html            # Base template
│   │   ├── auth/                # Auth templates
│   │   ├── admin/               # Admin templates
│   │   ├── teacher/             # Teacher templates
│   │   ├── student/             # Student templates
│   │   └── main/                # Main templates
│   └── static/                  # Static files
│       └── style.css            # Custom CSS
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OnlineQuizSystem.git
   cd OnlineQuizSystem
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env.example` to `.env`
   - Update settings as needed

5. **Initialize database**
   ```bash
   python run.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open browser: `http://localhost:5000`
   - Admin Login: `admin` / `admin@123`

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin@123 |

⚠️ **Change these credentials in production!**

---

## 📊 Database Schema

### Users Table
- Stores user information with roles and approval status
- Passwords hashed with werkzeug
- Timestamps for tracking

### Courses Table
- Course information created by teachers/admins
- Contains questions and quizzes

### Questions Table
- MCQ questions with 4 options
- Difficulty levels and marks
- Explanations for correct answers

### Quizzes Table
- Quiz configuration and settings
- Time limits and scoring options
- Ability to randomize questions

### Attempts Table
- Student quiz attempts
- Response tracking
- Time spent calculation

### Results Table
- Quiz scores and analytics
- Grade calculation
- Performance metrics

---

## 🎨 Modern UI/UX Features

- **Bootstrap 5**: Responsive design framework
- **Font Awesome**: Professional icon library
- **Custom CSS**: Modern animations and transitions
- **Mobile Responsive**: Works on all devices
- **Animated Dashboards**: Interactive stat cards
- **Progress Bars**: Visual progress indication
- **Quiz Timer**: Real-time countdown
- **Answer Analysis**: Detailed result breakdowns

---

## 🔧 Configuration

### config.py
```python
FLASK_ENV = 'development'  # development, testing, production
DEBUG = True
SECRET_KEY = 'your-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///quizdb.db'
```

### .env File
```bash
FLASK_ENV=development
DATABASE_URL=sqlite:///quizdb.db
SECRET_KEY=change-this-in-production
SESSION_COOKIE_SECURE=False
```

---

## 📝 Key Routes

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Create account
- `GET /logout` - Logout

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/courses` - Manage courses
- `GET /admin/analytics` - System analytics

### Teacher
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/courses` - My courses
- `POST /teacher/courses/create` - Create course
- `GET /teacher/courses/<id>/questions` - Manage questions
- `POST /teacher/courses/<id>/questions/add` - Add question

### Student
- `GET /student/dashboard` - Student dashboard
- `GET /student/courses` - Browse courses
- `GET /student/quizzes/<id>/start` - Start quiz
- `GET /student/attempts/<id>` - Take quiz
- `POST /student/attempts/<id>/submit` - Submit quiz
- `GET /student/results` - View all results

---

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Migrations
```bash
# Initialize database
python run.py

# Create new tables
flask db upgrade
```

### CLI Commands
```bash
# Initialize database
python run.py init-db

# Create admin user
python run.py create-admin

# Shell access
flask shell
```

---

## 🚢 Deployment

### Environment Setup
1. Set `FLASK_ENV=production`
2. Use strong `SECRET_KEY`
3. Update database URI
4. Configure production email settings

### Deployment Platforms

#### Render
```bash
# Create Procfile
web: gunicorn run:app
```

#### Railway
```bash
# Deploy directly from GitHub
```

#### PythonAnywhere
```bash
# Upload files and configure WSGI
```

---

## 🔒 Security Best Practices

1. **Change Default Credentials**: Update admin password immediately
2. **Use Strong SECRET_KEY**: Generate cryptographically secure key
3. **Enable HTTPS**: Use SSL certificates in production
4. **Input Validation**: All user inputs are sanitized
5. **SQL Injection Prevention**: Use SQLAlchemy ORM
6. **CSRF Protection**: Enabled by default
7. **Session Security**: Secure and HttpOnly cookies
8. **Rate Limiting**: Implement for production

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in config.py or use
python run.py --port 5001
```

### Database Locked Error
```bash
# Delete database and reinitialize
rm quizdb.db
python run.py
```

### Import Errors
```bash
# Verify virtual environment activation
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## 📈 Future Enhancements

- [ ] CSV import for questions
- [ ] Quiz scheduling
- [ ] Email notifications
- [ ] Certificates generation
- [ ] Video hosting integration
- [ ] Mobile app
- [ ] API documentation
- [ ] Advanced analytics
- [ ] Real-time collaboration
- [ ] Question bank sharing

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

Created as a professional online quiz platform for educational institutions.

---

## ⭐ Support

If you find this project helpful, please give it a star!

For issues and questions:
- Open an issue on GitHub
- Check existing issues first
- Provide detailed error messages

---

## 🎯 Version History

### v2.0 (Current)
- ✅ Complete refactoring with modern Flask structure
- ✅ Professional UI with Bootstrap 5
- ✅ Enhanced security (CSRF, validation, RBAC)
- ✅ Quiz timer and progress tracking
- ✅ Answer analysis and grading
- ✅ Leaderboard and analytics
- ✅ Multi-role support

### v1.0
- Initial release with basic functionality

---

**Last Updated**: March 10, 2024
**Status**: Production Ready ✅
