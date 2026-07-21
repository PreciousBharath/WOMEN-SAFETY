# Installation & Setup Guide

## Quick Start Guide

### Step 1: Clone/Extract Project
Extract the project to your desired location.

### Step 2: Open Terminal/Command Prompt
Navigate to the project directory:
```bash
cd path/to/ML-WOMEN-SAFETY-master
```

### Step 3: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python app.py
```

### Step 6: Access the Application
Open your browser and go to: **http://localhost:5000**

---

## Detailed Configuration

### Environment Setup

#### Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Run application
python app.py
```

#### Mac/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run application
python3 app.py
```

### First-Time Setup

1. **Database Initialization**
   - The database (`users.db`) will be automatically created when you first run the app
   - Tables will be created automatically

2. **Create a Test Account**
   - Go to http://localhost:5000/register
   - Create a new account with test credentials
   - Example:
     - Username: testuser
     - Email: test@example.com
     - Phone: +91-9876543210
     - Password: Test@123

3. **Make Your First Prediction**
   - Log in with your account
   - Navigate to "Predict" section
   - Fill in the form with sample data
   - Click "Analyze Safety"

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
pip install Flask==2.3.0
```

### Problem: "sqlite3 error"
**Solution:**
- Ensure Python is properly installed
- SQLite3 comes with Python, no additional installation needed

### Problem: Port 5000 already in use
**Solution:**
```bash
# Change port in app.py (line with app.run)
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Problem: "decision.pkl not found"
**Solution:**
- Ensure the model file exists in the project root
- Check file permissions
- Download the model if missing

### Problem: Database locked
**Solution:**
- Close any other instances of the application
- Delete `users.db` and restart (fresh database)

---

## Project File Checklist

Make sure you have these files:
- [ ] `app.py` - Main Flask application
- [ ] `requirements.txt` - Dependencies
- [ ] `decision.pkl` - ML Model
- [ ] `encoder.pkl` - Feature encoder
- [ ] `templates/` folder with all HTML files
- [ ] `static/styles.css` - CSS styling

---

## Features Configuration

### Changing Application Secret Key
Edit `app.py` line 14:
```python
app.config['SECRET_KEY'] = 'your-new-secret-key-here'
```

### Changing Database Location
Edit `app.py` line 15:
```python
app.config['DATABASE'] = 'path/to/your/database.db'
```

### Changing Port
Edit `app.py` last line:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## Running on Different Ports

### Using port 5001:
```bash
# Edit app.py and change port to 5001
python app.py
# Access at http://localhost:5001
```

### Using port 8000:
```bash
# Edit app.py and change port to 8000
python app.py
# Access at http://localhost:8000
```

---

## Database Reset

If you need to reset the database:
1. Delete `users.db` file
2. Run the application again
3. Database will be recreated automatically

---

## Performance Tips

1. **Enable Caching**: For production, enable browser caching
2. **Optimize Images**: Compress any images used
3. **Use CDN**: For static files in production
4. **Database Indexing**: Added for faster queries
5. **Connection Pooling**: Configured for better performance

---

## Security Recommendations

1. **Change SECRET_KEY** before deployment
2. **Use HTTPS** in production
3. **Enable CSRF Protection** for forms
4. **Validate Inputs** - Already implemented
5. **Use strong passwords** - Minimum 6 characters
6. **Regular backups** of database
7. **Update dependencies** regularly

---

## Development vs Production

### Development Mode:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Production Mode:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Testing the Application

### Test Account 1:
- Username: admin
- Password: admin123

### Sample Prediction:
- Area: Anna Nagar
- Zone: North
- Time: Evening (5PM-8PM)
- People: High
- Police: Yes
- Bar: No
- Tier: High
- Residence: High

Expected Result: Safe area with low risk score

---

## Getting Help

### Common Issues & Solutions:

1. **App crashes on startup**
   - Check if port is available
   - Verify all dependencies are installed
   - Check file paths

2. **Login page shows error**
   - Clear browser cache
   - Check database connection
   - Verify database file exists

3. **Predictions not saving**
   - Check database permissions
   - Ensure database is writable
   - Check available disk space

---

## Upgrade Guide

To upgrade dependencies:
```bash
pip install --upgrade -r requirements.txt
```

---

## Next Steps

1. ✅ Install and run the application
2. 📝 Create a user account
3. 🔍 Make sample predictions
4. 📊 View your prediction history
5. 📈 Check analytics and reports
6. 🆘 Test emergency features
7. ⚙️ Customize your settings

---

**Happy predicting! Stay safe!** 🛡️
