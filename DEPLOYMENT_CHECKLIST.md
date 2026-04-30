# InvoiceCrafting Invoice - Deployment Checklist

## Pre-Deployment Verification

### Code Quality
- [ ] Run verification script: `python verify_app.py`
- [ ] All checks pass ✓
- [ ] No import errors
- [ ] No syntax errors

### Database
- [ ] SQLite database created (local development)
- [ ] Run: `python -c "from app import db; print('Database OK')"`
- [ ] For production, PostgreSQL configured

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` is set and secure
- [ ] `DEBUG=False` for production
- [ ] Email settings configured (if needed)
- [ ] Database URL correct

### Dependencies
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] No version conflicts
- [ ] Virtual environment active

### Security
- [ ] CSRF protection enabled
- [ ] Password hashing configured
- [ ] Session security enabled
- [ ] File upload validation in place
- [ ] SQL injection prevention verified

---

## Local Testing

### Test Authentication
- [ ] Register new account works
- [ ] Login works
- [ ] Logout works
- [ ] Session persists correctly
- [ ] Demo account accessible

### Test Invoicing
- [ ] Can create invoice
- [ ] Can add line items
- [ ] Can calculate totals
- [ ] Can generate PDF
- [ ] PDF looks professional
- [ ] Can edit invoice
- [ ] Can delete invoice

### Test Clients
- [ ] Can add client
- [ ] Can view client details
- [ ] Can edit client
- [ ] Can delete client
- [ ] Client history shows

### Test Jobs
- [ ] Can create job
- [ ] Can link to client
- [ ] Can add invoices to job
- [ ] Profit calculation works
- [ ] Can edit job
- [ ] Can delete job

### Test Expenses
- [ ] Can add expense
- [ ] Can categorize expense
- [ ] Can upload receipt
- [ ] Can link to job
- [ ] Can edit expense
- [ ] Can delete expense

### Test Dashboard
- [ ] Statistics calculate correctly
- [ ] Charts display properly
- [ ] Recent items show
- [ ] Filters work

### Test Settings
- [ ] Can update profile
- [ ] Can upload logo
- [ ] Can change preferences
- [ ] Can change email
- [ ] Can change password

### Test Email (if configured)
- [ ] Can send invoice via email
- [ ] Can send payment reminder
- [ ] Email arrives in inbox
- [ ] PDF attachment includes
- [ ] Email formatting looks good

---

## Development Server Testing

### Start Server
```bash
python app.py
```

- [ ] Server starts without errors
- [ ] No warnings on startup
- [ ] http://localhost:5000 is accessible
- [ ] Can navigate to login page
- [ ] Static files load (CSS, JS)

### Test All Routes
```bash
python verify_app.py
```

- [ ] All routes registered
- [ ] All models validate
- [ ] All utilities functional
- [ ] Configuration correct

---

## Production Preparation

### Environment Setup
- [ ] Production `.env` created
- [ ] Different SECRET_KEY than development
- [ ] DEBUG=False set
- [ ] MAIL_SERVER configured
- [ ] DATABASE_URL set for PostgreSQL
- [ ] MAIL credentials correct

### Server Setup (Choose One)

#### Option 1: Gunicorn
```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```
- [ ] Gunicorn installed
- [ ] Can start with gunicorn
- [ ] Port 5000 accessible
- [ ] Multi-worker configured if needed

#### Option 2: Docker
```bash
docker build -t invoicecrafting .
docker run -p 5000:5000 invoicecrafting
```
- [ ] Dockerfile created/updated
- [ ] Docker image builds successfully
- [ ] Container runs without errors
- [ ] Port mapping correct

#### Option 3: Heroku
```bash
heroku create app-name
heroku config:set SECRET_KEY=your-key
git push heroku main
```
- [ ] Heroku CLI installed
- [ ] Git initialized
- [ ] Heroku app created
- [ ] PostgreSQL addon added
- [ ] Environment variables set

### Database Migration
- [ ] Database created on production server
- [ ] Tables initialized: `db.create_all()`
- [ ] Admin user created (optional)
- [ ] Connection tested

### Static Files
- [ ] Collect static files (if using production server)
- [ ] CSS loads correctly
- [ ] JavaScript works
- [ ] Images display
- [ ] Uploads folder writable

### Backup
- [ ] Database backup plan established
- [ ] Backup location secure
- [ ] Backup testing done
- [ ] Recovery procedure documented

---

## Production Deployment

### Deploy to Production
- [ ] Pull/upload latest code
- [ ] Update requirements: `pip install -r requirements.txt`
- [ ] Configure production `.env`
- [ ] Initialize database
- [ ] Start application server
- [ ] Configure firewall/security groups

### Post-Deployment Testing
- [ ] Application accessible on production URL
- [ ] All features working
- [ ] Can login with existing accounts
- [ ] Can create new accounts
- [ ] Invoices can be generated
- [ ] Email sending works
- [ ] Error pages display correctly
- [ ] Logging working

### Monitoring & Maintenance
- [ ] Application logs monitored
- [ ] Error monitoring setup (optional)
- [ ] Database backups scheduled
- [ ] SSL certificate valid (HTTPS)
- [ ] Regular security updates planned
- [ ] Performance monitoring setup (optional)

---

## Post-Deployment

### User Onboarding
- [ ] Help documentation available
- [ ] Setup guide provided to users
- [ ] Support contact provided
- [ ] FAQ prepared

### Ongoing Maintenance
- [ ] Monitor server logs daily
- [ ] Check database backups
- [ ] Monitor disk space
- [ ] Monitor memory/CPU usage
- [ ] Update dependencies monthly
- [ ] Security patches applied promptly

### Feature Requests
- [ ] Feedback channel established
- [ ] Issue tracking system setup
- [ ] Priority list maintained
- [ ] Roadmap shared with stakeholders

---

## Troubleshooting During Deployment

### Application Won't Start
```bash
# Check for Python errors
python app.py

# Check imports
python -c "from app import create_app; app = create_app(); print('OK')"

# Check database
python -c "from app import db; print(db)"
```

### Database Connection Issues
```bash
# Verify DATABASE_URL
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"

# Test connection
python
>>> from app import db
>>> db.engine.execute("SELECT 1")
```

### Email Not Working
```bash
# Test SMTP settings
python
>>> from flask_mail import Message
>>> from app import app, mail
>>> with app.app_context():
...     msg = Message("Test", recipients=["your-email@example.com"])
...     mail.send(msg)
```

### Port Already in Use
```bash
# Change port in app.py
# Or kill existing process using the port
```

### Permission Issues
```bash
# Ensure upload directories writable
chmod -R 755 static/uploads/

# Ensure database file writable
chmod 666 invoicecrafting.db
```

---

## Success Criteria

✓ Application starts without errors  
✓ All routes accessible and functional  
✓ Database operations work correctly  
✓ User authentication working  
✓ Invoice generation successful  
✓ Email delivery functional  
✓ Static files loading  
✓ Error handling working  
✓ Logging active  
✓ Performance acceptable  
✓ Security measures in place  

---

## Final Checklist Before Going Live

- [ ] All tests pass
- [ ] Documentation complete
- [ ] Backup system working
- [ ] Monitoring setup
- [ ] Security audit complete
- [ ] Performance tested
- [ ] Load tested
- [ ] User acceptance testing done
- [ ] Support staff trained
- [ ] Disaster recovery plan ready

---

## Contact & Support

**If deployment issues occur:**

1. Check SETUP.md for common issues
2. Run verify_app.py for diagnostics
3. Review application logs
4. Check error messages in console
5. Verify environment configuration

---

**Status:** Ready for Deployment ✓  
**Version:** 1.0.0  
**Date:** 2024
