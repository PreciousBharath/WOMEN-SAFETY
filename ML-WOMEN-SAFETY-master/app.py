
import os
import pickle
import sys
import numpy as np
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json

# ==================== FIX NUMPY COMPATIBILITY ====================
# Patch for numpy._core compatibility issue with older pickle files
if not hasattr(np, '_core'):
    np._core = np.core
sys.modules['numpy._core'] = np.core

# ==================== CONFIGURATION ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'women-safety-secret-key-2024'
app.config['DATABASE'] = 'users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ==================== DATABASE FUNCTIONS ====================
def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Predictions history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            area TEXT NOT NULL,
            zone TEXT NOT NULL,
            time_period TEXT NOT NULL,
            people_frequency TEXT NOT NULL,
            police_nearby TEXT NOT NULL,
            bar_nearby TEXT NOT NULL,
            tier TEXT NOT NULL,
            residence_level TEXT NOT NULL,
            prediction_result TEXT NOT NULL,
            risk_score FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            theme TEXT DEFAULT 'light',
            notifications_enabled BOOLEAN DEFAULT 1,
            default_location TEXT,
            emergency_contacts TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Emergency alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            severity TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== FALLBACK MODEL CLASS ====================
class FallbackModel:
    """Fallback model for when pickle loading fails"""
    def predict(self, input_data):
        """Generate prediction based on simple heuristics"""
        # Extract features: [area, zone, time, people, police, bar, tier, residence]
        area, zone, time_period, people, police, bar, tier, residence = input_data[0]
        
        # Simple risk calculation
        risk = 0.0
        risk += 0.3 if time_period == 3 or time_period == 4 else 0  # Late night/midnight
        risk += 0.3 if people == 1 else 0  # Low people frequency
        risk += 0.2 if bar == 1 else 0  # Bar nearby
        risk -= 0.3 if police == 1 else 0  # Police nearby
        risk += 0.2 if tier == 1 or tier == 2 else 0  # Medium/Low tier
        
        # Clamp risk between 0 and 1
        risk = max(0, min(1, risk + 0.3))
        
        # Return 1 for unsafe (risk > 0.5), 0 for safe
        return [1 if risk > 0.5 else 0]

# ==================== LOAD ML MODEL ====================
def load_model():
    """Load the trained ML model with fallback"""
    try:
        with open("decision.pkl", "rb") as file:
            model = pickle.load(file)
        print("✓ ML Model loaded successfully")
        return model
    except FileNotFoundError:
        print("⚠ Warning: Model file (decision.pkl) not found! Using fallback model...")
        return FallbackModel()
    except Exception as e:
        print(f"⚠ Warning: Could not load model ({type(e).__name__}). Using fallback model...")
        return FallbackModel()

model = load_model()

# ==================== FEATURE MAPPINGS ====================
AREA_DICT = {
    # Hyderabad Central Areas
    "Secunderabad": 0,
    "Banjara Hills": 1,
    "Jubilee Hills": 2,
    "Kondapur": 3,
    "HITEC City": 4,
    "Kukatpally": 5,
    "Miyapur": 6,
    "Serilingampally": 7,
    "Gachibowli": 8,
    "Narayanaguda": 9,
    
    # Old City & Historic Areas
    "Charminar": 10,
    "Abids": 11,
    "Old City": 12,
    "Chandrayangutta": 13,
    "Moghalpura": 14,
    "Badangpet": 15,
    
    # Hyderabad South
    "Dilsukhnagar": 16,
    "Rajendranagar": 17,
    "Koti": 18,
    "Hyderabad Fort": 19,
    "Falaknuma": 20,
    "Malakpet": 21,
    "Chaitanyapuri": 22,
    "Jamai Osmania": 23,
    
    # Hyderabad North
    "Ameerpet": 24,
    "Panjagutta": 25,
    "Yousufguda": 26,
    "Mehdipatnam": 27,
    "Somajiguda": 28,
    "Domalguda": 29,
    "Begumpet": 30,
    "RTC X Roads": 31,
    
    # IT & Business Districts
    "Raidurg": 32,
    "Nanakramguda": 33,
    "Madhapur": 34,
    "Gowra Road": 35,
    "Indiranagar": 36,
    "Uppal": 37,
    "Attapur": 38,
    "Saidabad": 39,
    
    # Secunderabad Areas
    "Secunderabad Cantonment": 40,
    "Bowenpally": 41,
    "Champalguda": 42,
    "Karachi": 43,
    "Trimulgherry": 44,
    "Marredpally": 45,
    
    # Western Hyderabad
    "Lakdikapool": 46,
    "Lallaguda": 47,
    "Begum Bazaar": 48,
    "Hyderabad Railway Station": 49,
    "Malkajgiri": 50,
    
    # Telangana Outskirts
    "Alwal": 51,
    "Chandrayangutta": 52,
    "Patancheru": 53,
    "Sangareddy": 54,
    "Ghatkesar": 55,
    "Tandur": 56,
    "Kurnool": 57,
    "Zaheerabad": 58,
    "Nalgonda": 59,
    "Warangal": 60
}

ZONE_DICT = {
    "North": 0,
    "South": 1,
    "East": 2,
    "West": 3,
    "Central": 4
}

TIME_DICT = {
    "Morning (6AM-12PM)": 0,
    "Afternoon (12PM-5PM)": 1,
    "Evening (5PM-8PM)": 2,
    "Night (8PM-12AM)": 3,
    "Late Night (12AM-6AM)": 4
}

PEOPLE_DICT = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

BOOLEAN_DICT = {
    "Yes": 1,
    "No": 0
}

TIER_DICT = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

RESIDENCE_DICT = {
    "Low": 0,
    "Medium": 1,
    "High": 2
}

# ==================== HELPER FUNCTIONS ====================
def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_by_id(user_id):
    """Get user information by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_preferences(user_id):
    """Get user preferences"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,))
    prefs = cursor.fetchone()
    conn.close()
    return prefs

def calculate_risk_score(prediction):
    """Calculate a risk score based on prediction"""
    if prediction == 1:  # Unsafe
        return 0.8 + np.random.uniform(-0.1, 0.1)
    else:  # Safe
        return 0.2 + np.random.uniform(-0.1, 0.1)

def get_risk_level(risk_score):
    """Determine risk level from score"""
    if risk_score >= 0.7:
        return "High Risk"
    elif risk_score >= 0.4:
        return "Medium Risk"
    else:
        return "Low Risk"

def get_recommendations(area, zone, time, people, police, bar, tier, residence, prediction):
    """Generate safety recommendations based on prediction and factors"""
    recommendations = []
    
    if prediction == 1:  # Unsafe
        recommendations.append("Avoid traveling alone in this area during the selected time period.")
        
        if time == "Late Night (12AM-6AM)":
            recommendations.append("Try to avoid this area late at night. Consider traveling during daytime.")
        
        if people == "Low":
            recommendations.append("The area has low foot traffic. Stay alert and keep contact with friends.")
        
        if police == "No":
            recommendations.append("There's no nearby police station. Ensure you have emergency contacts saved.")
        
        if bar == "Yes":
            recommendations.append("There are bars nearby. Be cautious of the area during closing hours.")
        
        recommendations.append("Consider using a safety app or sharing your location with trusted contacts.")
        recommendations.append("Travel with companions when possible.")
    else:  # Safe
        recommendations.append("This area is generally safe based on current parameters.")
        
        if people == "High":
            recommendations.append("The area has good foot traffic and visibility - a positive safety factor.")
        
        if police == "Yes":
            recommendations.append("Nearby police presence provides additional security assurance.")
        
        recommendations.append("However, always practice general safety precautions.")
        recommendations.append("Stay aware of your surroundings at all times.")
    
    return recommendations

# ==================== ROUTES - AUTHENTICATION ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute('''
                INSERT INTO users (username, email, password, phone)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password, phone))
            
            user_id = cursor.lastrowid
            
            # Create default preferences for new user
            cursor.execute('''
                INSERT INTO preferences (user_id, theme, notifications_enabled)
                VALUES (?, 'light', 1)
            ''', (user_id,))
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password required!', 'danger')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Update last login time
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            conn.commit()
            conn.close()
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

# ==================== ROUTES - MAIN FEATURES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = get_user_by_id(session['user_id'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get recent predictions
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''', (session['user_id'],))
    recent_predictions = cursor.fetchall()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total FROM predictions WHERE user_id = ?', (session['user_id'],))
    total_predictions = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as unsafe FROM predictions WHERE user_id = ? AND prediction_result = 'Unsafe'", (session['user_id'],))
    unsafe_count = cursor.fetchone()['unsafe']
    
    cursor.execute("SELECT COUNT(*) as safe FROM predictions WHERE user_id = ? AND prediction_result = 'Safe'", (session['user_id'],))
    safe_count = cursor.fetchone()['safe']
    
    conn.close()
    
    return render_template('dashboard.html', 
                         user=user, 
                         recent_predictions=recent_predictions,
                         total_predictions=total_predictions,
                         unsafe_count=unsafe_count,
                         safe_count=safe_count)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Make a safety prediction"""
    if request.method == 'POST':
        if not model:
            flash('Model not loaded. Please try again later.', 'danger')
            return redirect(url_for('predict'))
        
        # Get form data
        area = request.form.get('area')
        zone = request.form.get('zone')
        time = request.form.get('time')
        people = request.form.get('people')
        police = request.form.get('police')
        bar = request.form.get('bar')
        tier = request.form.get('tier')
        residence = request.form.get('residence')
        
        # Validate input
        if not all([area, zone, time, people, police, bar, tier, residence]):
            flash('Please fill all fields!', 'danger')
            return redirect(url_for('predict'))
        
        try:
            # Prepare input data
            input_data = np.array([[
                AREA_DICT[area],
                ZONE_DICT[zone],
                TIME_DICT[time],
                PEOPLE_DICT[people],
                BOOLEAN_DICT[police],
                BOOLEAN_DICT[bar],
                TIER_DICT[tier],
                RESIDENCE_DICT[residence]
            ]])
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Calculate risk score
            risk_score = calculate_risk_score(prediction)
            risk_level = get_risk_level(risk_score)
            
            # Get recommendations
            recommendations = get_recommendations(
                area, zone, time, people, police, bar, tier, residence, prediction
            )
            
            # Determine prediction result
            prediction_result = "Unsafe" if prediction == 1 else "Safe"
            
            # Save prediction to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (user_id, area, zone, time_period, people_frequency, police_nearby, 
                 bar_nearby, tier, residence_level, prediction_result, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], area, zone, time, people, police, bar, tier, residence, prediction_result, risk_score))
            
            conn.commit()
            conn.close()
            
            return render_template('prediction_result.html',
                                 area=area,
                                 zone=zone,
                                 time=time,
                                 people=people,
                                 police=police,
                                 bar=bar,
                                 tier=tier,
                                 residence=residence,
                                 prediction_result=prediction_result,
                                 risk_score=round(risk_score, 2),
                                 risk_level=risk_level,
                                 recommendations=recommendations)
        
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'danger')
            return redirect(url_for('predict'))
    
    return render_template('predict.html',
                         areas=list(AREA_DICT.keys()),
                         zones=list(ZONE_DICT.keys()),
                         times=list(TIME_DICT.keys()),
                         peoples=list(PEOPLE_DICT.keys()),
                         tiers=list(TIER_DICT.keys()),
                         residences=list(RESIDENCE_DICT.keys()))

@app.route('/history')
@login_required
def history():
    """View prediction history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (session['user_id'],))
    predictions = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', predictions=predictions)

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_user_by_id(session['user_id'])
    preferences = get_user_preferences(session['user_id'])
    
    return render_template('profile.html', user=user, preferences=preferences)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    phone = request.form.get('phone')
    location = request.form.get('location')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET phone = ?, location = ?
        WHERE id = ?
    ''', (phone, location, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    preferences = get_user_preferences(session['user_id'])
    return render_template('settings.html', preferences=preferences)

@app.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
    """Update user settings"""
    theme = request.form.get('theme', 'light')
    notifications = request.form.get('notifications_enabled')
    default_location = request.form.get('default_location')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE preferences 
        SET theme = ?, notifications_enabled = ?, default_location = ?
        WHERE user_id = ?
    ''', (theme, 1 if notifications else 0, default_location, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/emergency', methods=['GET', 'POST'])
@login_required
def emergency():
    """Emergency alert system"""
    if request.method == 'POST':
        location = request.form.get('location')
        description = request.form.get('description')
        severity = request.form.get('severity', 'medium')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emergency_alerts (user_id, location, description, severity)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], location, description, severity))
        conn.commit()
        conn.close()
        
        flash('Emergency alert recorded! Stay safe!', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('emergency.html')

@app.route('/reports')
@login_required
def reports():
    """View analytics and reports"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get zone statistics
    cursor.execute('''
        SELECT zone, COUNT(*) as count, 
               SUM(CASE WHEN prediction_result = 'Unsafe' THEN 1 ELSE 0 END) as unsafe_count
        FROM predictions 
        WHERE user_id = ?
        GROUP BY zone
    ''', (session['user_id'],))
    zone_stats = cursor.fetchall()
    
    # Get time period statistics
    cursor.execute('''
        SELECT time_period, COUNT(*) as count, 
               SUM(CASE WHEN prediction_result = 'Unsafe' THEN 1 ELSE 0 END) as unsafe_count
        FROM predictions 
        WHERE user_id = ?
        GROUP BY time_period
    ''', (session['user_id'],))
    time_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('reports.html', zone_stats=zone_stats, time_stats=time_stats)

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user = get_user_by_id(session['user_id'])
    
    if not check_password_hash(user['password'], current_password):
        flash('Current password is incorrect!', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match!', 'danger')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('New password must be at least 6 characters!', 'danger')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 error"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 error"""
    return render_template('500.html'), 500

# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)

