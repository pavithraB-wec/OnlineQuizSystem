# ⚡ Quick Start Guide

## 30-Second Setup

### Windows
```bash
cd c:\TURBOC3\BIN\PAVI\OnlineQuizSystem
venv\Scripts\activate
python run.py
```

### macOS/Linux
```bash
cd OnlineQuizSystem
source venv/bin/activate
python run.py
```

## Access Points

| Role | URL | Username | Password |
|------|-----|----------|----------|
| Admin | http://localhost:5000 | admin | admin@123 |
| Student | http://localhost:5000/register | (create account) | - |
| Teacher | http://localhost:5000/register | (create account) | - |

## First Steps

### 1. Login as Admin
- Click "Login" or go to `/login`
- Use: `admin` / `admin@123`
- View dashboard with system statistics

### 2. Create a Course (as Teacher/Admin)
- Go to "Teacher" → "My Courses"
- Click "Create Course"
- Enter course details
- Submit

### 3. Add Questions
- Click "Manage Questions" for a course
- Click "Add Question"
- Fill MCQ details (question, options A-B-C-D, correct answer)
- Set marks and difficulty
- Save

### 4. Create a Quiz
- Go to "My Courses"
- Click "Create Quiz"
- Assign questions
- Set time limit (e.g., 30 minutes)
- Publish

### 5. Take a Quiz (as Student)
- Register as student
- Go to "Courses"
- Click "Take Quiz"
- Answer questions
- Submit
- View results with analysis

## Key Features to Try

✅ **Quiz Timer** - Watch countdown in quiz interface
✅ **Progress Bar** - See % of questions answered
✅ **Result Analysis** - View correct answers with explanations
✅ **Leaderboard** - Check rankings per course
✅ **Dashboard** - See analytics and statistics
✅ **Mobile Responsive** - Open on phone/tablet

## Database

- **Type**: SQLite (development)
- **File**: `instance/quizdb.db`
- **Auto-created**: On first run

## Tips & Tricks

💡 **Create Multiple Students**: Register different accounts to test leaderboard

💡 **Test Timer**: Set 2-minute limit for quick testing

💡 **Check Analytics**: Admin dashboard shows real-time statistics

💡 **Role Switching**: Register as different roles to compare interfaces

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Kill process or change port in `config.py` |
| Database locked | Delete `instance/quizdb.db` and restart |
| Module not found | Run `pip install -r requirements.txt` |
| Permission denied | Run terminal as administrator |

## Reset Everything

```bash
# Delete database
rm instance/quizdb.db
# Restart app
python run.py
# Login with admin/admin@123
```

## Next: Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Render deployment
- Railway deployment
- PythonAnywhere setup
- PostgreSQL configuration
- SSL/HTTPS setup

---

**Version 2.0** | Production Ready ✅
