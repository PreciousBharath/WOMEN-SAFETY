# Women Safety Prediction System - Advanced Edition

## 🛡️ Overview
An intelligent machine learning-based system designed to predict women's safety in specific areas by analyzing environmental, social, and location-based factors. The advanced version includes user authentication, personalized dashboards, prediction history, analytics, and emergency alert features.

## ✨ Key Features

### Authentication & User Management
- **Secure Registration**: Email-based registration with password validation
- **Login System**: Session-based authentication with password hashing
- **Profile Management**: Edit personal information and update preferences
- **Password Security**: Secure password change functionality

### Core Prediction Features
- **Safety Analysis**: ML-based safety predictions for different areas
- **Risk Scoring**: Detailed risk assessment with numerical scores
- **Smart Recommendations**: Context-aware safety recommendations
- **Multiple Factors**: Considers time, location, people frequency, police presence, and more

### User Dashboard
- **Statistics Dashboard**: View prediction statistics and safety metrics
- **Recent Predictions**: Track recent area safety predictions
- **Safety Rate Display**: Visual representation of safe vs. unsafe areas
- **Quick Actions**: Easy access to all major features

### Advanced Features
- **Prediction History**: Complete history of all predictions made
- **Analytics & Reports**: Zone-wise and time-wise safety statistics
- **Emergency Alert System**: Report unsafe situations and emergencies
- **User Settings**: Customize preferences and notification settings
- **Risk Assessment Visualization**: Visual risk meters and progress bars

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- SQLite3 (usually included with Python)

### Setup Instructions

1. **Navigate to project directory:**
   ```bash
   cd "ML-WOMEN-SAFETY-master"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   The database will be automatically created when you first run the application.

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your web browser and go to: `http://localhost:5000`

## 📊 Database Structure

### Users Table
- Stores user credentials and account information
- Fields: username, email, password, phone, location, created_at, last_login

### Predictions Table
- Stores all user predictions with results
- Fields: area, zone, time_period, people_frequency, police_nearby, bar_nearby, tier, residence_level, prediction_result, risk_score

### Preferences Table
- User preferences and settings
- Fields: theme, notifications_enabled, default_location, emergency_contacts

### Emergency Alerts Table
- Emergency reports from users
- Fields: location, description, severity, status, timestamp

## 🎯 How to Use

### Making Your First Prediction

1. **Register**: Create a new account with valid credentials
2. **Login**: Use your credentials to log in
3. **Navigate to Predict**: Click on "Predict" in the navigation bar
4. **Fill Details**: Select all required parameters:
   - Area: Choose your area of interest
   - Zone: Select directional zone
   - Time Period: Choose time of day
   - People Frequency: Set crowd level
   - Police Station Nearby: Yes/No
   - Bar Nearby: Yes/No
   - Tier & Residence Level: Set these parameters
5. **Get Results**: View safety assessment and recommendations

### Viewing Your Predictions

- **Dashboard**: See recent predictions and statistics
- **History**: View complete prediction history
- **Reports**: Analyze patterns and trends

### Emergency Features

- **Report Emergency**: Use the emergency alert system to report unsafe situations
- **Emergency Contacts**: Quick access to important contacts

## 🔐 Security Features

- **Password Hashing**: All passwords are hashed using pbkdf2:sha256
- **Session Management**: Secure session handling with Flask
- **Input Validation**: All user inputs are validated
- **SQL Injection Protection**: Using parameterized queries
- **XSS Prevention**: Template escaping with Jinja2

## 📈 Model Information

The system uses a trained Decision Tree classifier:
- **Model File**: `decision.pkl`
- **Features**: 8 environmental and location-based factors
- **Training Data**: Historical women safety data from Chennai City

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern Bootstrap 5**: Clean and professional interface
- **Font Awesome Icons**: Intuitive visual indicators
- **Smooth Animations**: Enhanced user experience with CSS transitions
- **Dark-themed Navigation**: Professional navbar with dropdown menus

## 🚨 Features Overview

### Dashboard
- View key statistics
- Quick access buttons
- Recent predictions table
- Safety metrics visualization

### Predict Page
- Comprehensive form with all parameters
- Helpful information section
- Error handling and validation

### Results Page
- Safety assessment (Safe/Unsafe)
- Risk score visualization
- Detailed recommendations
- Location summary

### History Page
- Complete prediction history table
- Sortable columns
- Risk visualization

### Reports Page
- Zone-wise statistics
- Time-period analytics
- Safety rate analysis
- Overall trend summary

### Profile Page
- Account information display
- Edit profile details
- Change password functionality

### Settings Page
- Theme preferences
- Notification controls
- Default location setup
- Privacy and security info

### Emergency Page
- Report emergency situations
- Severity level selection
- Emergency contact information

## 🔧 Configuration

The application uses the following configuration:
- **SECRET_KEY**: Used for session management (change in production)
- **DATABASE**: SQLite database stored as `users.db`
- **DEBUG**: Enabled for development (disable in production)
- **HOST**: 0.0.0.0 (accessible from all interfaces)
- **PORT**: 5000

## 📝 File Structure

```
ML-WOMEN-SAFETY-master/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── decision.pkl                    # Trained ML model
├── encoder.pkl                     # Feature encoder
├── users.db                        # SQLite database
├── static/
│   └── styles.css                  # Custom CSS styling
└── templates/
    ├── base.html                   # Base template
    ├── login.html                  # Login page
    ├── register.html               # Registration page
    ├── dashboard.html              # User dashboard
    ├── predict.html                # Prediction form
    ├── prediction_result.html       # Results page
    ├── history.html                # Prediction history
    ├── profile.html                # User profile
    ├── settings.html               # User settings
    ├── emergency.html              # Emergency alerts
    ├── reports.html                # Analytics reports
    ├── 404.html                    # Error page
    └── 500.html                    # Server error page
```

## 🧪 Testing the System

### Test User Credentials
You can create test accounts using the registration page.

### Sample Prediction Parameters
- Area: Anna Nagar
- Zone: North
- Time: Evening (5PM-8PM)
- People Frequency: High
- Police: Yes
- Bar: No
- Tier: High
- Residence: High

## 📱 API Endpoints

### Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Main Features
- `GET /dashboard` - User dashboard
- `GET/POST /predict` - Make a prediction
- `GET /history` - View prediction history
- `GET /reports` - View analytics

### User Account
- `GET /profile` - View/edit profile
- `POST /update-profile` - Update profile
- `POST /change-password` - Change password
- `GET /settings` - View settings
- `POST /update-settings` - Update settings

### Emergency
- `GET/POST /emergency` - Report emergency

## 🐛 Troubleshooting

### Issue: Model not loading
- Ensure `decision.pkl` exists in the main directory
- Check file permissions

### Issue: Database errors
- Delete `users.db` to reset the database
- Check SQLite3 installation

### Issue: Port already in use
- Change the port in app.py or kill the process using port 5000

### Issue: Module not found
- Install all requirements: `pip install -r requirements.txt`
- Verify Python version compatibility

## 🚀 Deployment

For production deployment:
1. Set `debug=False` in app.py
2. Use a production WSGI server (gunicorn, waitress)
3. Change the SECRET_KEY to a strong random value
4. Use an external database (MySQL, PostgreSQL)
5. Enable HTTPS/SSL
6. Configure proper logging

## 📞 Support & Feedback

For issues or feedback, please contact the development team.

## 📄 License

This project is licensed under the MIT License.

## 👥 Credits

Developed by: AI/ML Team
Dataset: Women Safety in Chennai City

---

**Stay Safe. Stay Informed. Stay Protected.** 🛡️
