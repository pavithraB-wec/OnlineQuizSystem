# 🚀 Deployment Guide

This guide covers deployment of the Online Quiz System to production platforms.

---

## Pre-Deployment Checklist

- [ ] Change admin password from `admin/admin@123`
- [ ] Generate new `SECRET_KEY`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set secure cookies (`SESSION_COOKIE_SECURE=True`)
- [ ] Enable HTTPS/SSL
- [ ] Test locally with production settings
- [ ] Create `.env` with production values

---

## 1. Render Deployment

### Step 1: Push to GitHub
```bash
cd OnlineQuizSystem
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/OnlineQuizSystem.git
git branch -M main
git push -u origin main
```

### Step 2: Create Procfile
```bash
# Create Procfile in root directory
web: gunicorn run:app
```

### Step 3: Update requirements.txt
```bash
# Add gunicorn for production server
pip install gunicorn
pip freeze > requirements.txt
```

### Step 4: On Render Dashboard
1. Login to [render.com](https://render.com)
2. Click "New Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: quiz-system
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
5. Add Environment Variables:
   ```
   FLASK_ENV = production
   SECRET_KEY = (generate strong key)
   DATABASE_URL = (PostgreSQL provided by Render)
   FLASK_APP = run.py
   ```
6. Click "Create Web Service"

### Step 5: Initialize Database on Render
```bash
# SSH into Render or use dashboard terminal
python run.py  # Creates tables and admin user
```

✅ **Your app is live at**: `https://quiz-system.onrender.com`

---

## 2. Railway Deployment

### Step 1: Create Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "GitHub Repo"
3. Choose your OnlineQuizSystem repository
4. Click "Deploy Now"

### Step 3: Add PostgreSQL
1. In dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Auto-configured connection string

### Step 4: Configure Environment
In Railway dashboard, add variables:
```
FLASK_ENV = production
SECRET_KEY = (generate strong key)
DATABASE_URL = (Railway PostgreSQL URL)
DEBUG = False
```

### Step 5: Deploy
Railway auto-deploys on push:
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

✅ **Your app is live at**: `https://<project-name>.railway.app`

---

## 3. PythonAnywhere Deployment

### Step 1: Create PythonAnywhere Account
- Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- Sign up (free tier available)

### Step 2: Clone Repository
In PythonAnywhere bash console:
```bash
cd /home/username
git clone https://github.com/yourusername/OnlineQuizSystem.git
cd OnlineQuizSystem
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Step 4: Create WSGI File
In `/var/www/username_pythonanywhere_com_wsgi.py`:
```python
import sys
path = '/home/username/OnlineQuizSystem'
if path not in sys.path:
    sys.path.append(path)

from run import app as application
```

### Step 5: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Select "Manual configuration"
4. Choose Python 3.10
5. Set WSGI file to path above
6. Configure virtualenv: `/home/username/OnlineQuizSystem/venv`

### Step 6: Configure Environment Variables
In "Virtualenv" section, create `.env`:
```bash
FLASK_ENV=production
SECRET_KEY=(generate key)
DATABASE_URL=mysql://user:pass@host/dbname
```

### Step 7: Reload & Test
- Click "Reload" in Web tab
- Visit `https://username.pythonanywhere.com`

✅ **Your app is live**

---

## Database Configuration

### Using PostgreSQL (Recommended for Production)

1. **Install psycopg2**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Update requirements.txt**:
   ```bash
   pip freeze > requirements.txt
   ```

3. **Configure DATABASE_URL**:
   ```
   postgresql://user:password@host:5432/dbname
   ```

4. **Update config.py**:
   ```python
   class ProductionConfig(Config):
       SQLALCHEMY_DATABASE_URI = os.getenv(
           'DATABASE_URL',
           'postgresql://user:password@localhost/quiz_db'
       )
       SQLALCHEMY_ECHO = False
       DEBUG = False
   ```

### Using SQLite (Not Recommended for Production)
- Maximum 1-5 concurrent users
- Use only for testing
- Not suitable for multiple servers

---

## SSL/HTTPS Setup

### On Render
- **Auto-enabled**: HTTPS automatically configured
- **Certificate**: Let's Encrypt (free)
- Status: ✅ Ready

### On Railway
- **Auto-enabled**: HTTPS included
- **Custom Domain**: Available in Pro plan
- Status: ✅ Ready

### On PythonAnywhere
1. Go to "Web" tab
2. Scroll to "Security"
3. Click "Force HTTPS"
4. Certificate auto-generated

---

## Security Hardening

### 1. Update Configurations
```python
# In config.py:
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
```

### 2. Environment Variables
Create `.env.production`:
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://...
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

### 3. IP Whitelisting (if available)
- Restrict admin panel to known IPs
- Use VPN for sensitive operations

### 4. Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install --upgrade package_name
```

---

## Monitoring & Debugging

### Render
- Dashboard: Monitor CPU, Memory, Requests
- Logs: Real-time error viewing
- Alerts: Email on failures

### Railway
- Metrics: CPU, Memory, Network
- Logs: Searchable log history
- Deployments: Track all versions

### PythonAnywhere
- Web logs: Error and access logs
- CPU usage: Real-time monitoring
- Database: Query analysis

---

## Custom Domain Setup

### Render
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS CNAME record
4. Auto-verified with SSL

### Railway
1. Settings → Custom Domain (Pro)
2. Add domain
3. Update DNS records
4. SSL auto-enabled

### PythonAnywhere
1. Web tab → Custom Domain
2. Add domain
3. Configure DNS
4. Update WSGI config

---

## Environment Variables Reference

```bash
# Flask Configuration
FLASK_ENV=production           # production/development
FLASK_APP=run.py              # Entry point
DEBUG=False                   # Disable debug mode

# Secret & Security
SECRET_KEY=your-secret-key    # Change me!
SESSION_COOKIE_SECURE=True    # HTTPS only
SESSION_COOKIE_HTTPONLY=True  # No JavaScript access

# Database
DATABASE_URL=postgresql://... # Production database

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=app-specific-password

# Admin
DEFAULT_ADMIN_PASSWORD=ChangeMe123!
```

---

## Troubleshooting Deployments

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Check requirements.txt, reinstall packages |
| DATABASE_URL not found | Add environment variable in dashboard |
| 502 Bad Gateway | Check logs, restart dyno |
| Static files not loading | Run `flask collect-static` |
| Timezone issues | Set `TZ=UTC` environment variable |
| Memory limit exceeded | Upgrade plan or optimize queries |

---

## Performance Optimization

### 1. Database Indexing
```python
# Already tuned in models with indexed columns
```

### 2. Query Optimization
```python
# Use relationships efficiently
student = User.query.options(
    db.joinedload('attempts')
).get(student_id)
```

### 3. Caching Strategy
```python
# Add Flask-Caching for leaderboards
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/leaderboard/<course_id>')
@cache.cached(timeout=300)
def leaderboard(course_id):
    # Cached for 5 minutes
    pass
```

### 4. CDN for Static Files
- Upload CSS/JS to CDN
- Use `STATIC_URL` configuration
- Reduces server load

---

## Backup & Recovery

### Database Backups
```bash
# PostgreSQL backup
pg_dump dbname > backup.sql

# Restore
psql dbname < backup.sql
```

### File Backups
- Regular Git commits
- .env files (secure location)
- Database snapshots (weekly)

---

## Rollback Procedure

### On Render
```bash
# View deployments
# Click "Previous Versions"
# Select & redeploy
```

### On Railway
```bash
# View deployments in dashboard
# Select previous version
# Automatic rollback available
```

### On PythonAnywhere
```bash
# Keep multiple Python environments
# Switch virtualenv path in web configuration
```

---

## Post-Deployment

✅ **Verify Deployment:**
1. Access home page
2. Login with admin account
3. Create test course
4. Take test quiz
5. Verify results display

📊 **Monitor Performance:**
- Check dashboard metrics daily
- Monitor error logs
- Track user activity
- Review database performance

🔄 **Maintenance Schedule:**
- Weekly: Check logs and errors
- Monthly: Update dependencies
- Quarterly: Security audit
- Annually: Architecture review

---

## Support & Resources

- **Documentation**: See COMPREHENSIVE_README.md
- **Quick Start**: See QUICK_START.md
- **Issues**: Check GitHub issues
- **Community**: Flask documentation

---

**Version 2.0** | Production Ready ✅
