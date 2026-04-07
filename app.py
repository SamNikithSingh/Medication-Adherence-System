import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from models import db, Patient, Doctor
from auth import auth
from routes_doctor import doctor_bp
from routes_patient import patient_bp
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smart-health-secret-key-default')
# Update this with your PostgreSQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg://postgres:samnoelsingh@localhost:5432/healthcare_db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.patient_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('patient_'):
        return Patient.query.get(int(user_id.replace('patient_', '')))
    elif user_id.startswith('doctor_'):
        return Doctor.query.get(int(user_id.replace('doctor_', '')))
    return None

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(patient_bp, url_prefix='/patient')

@app.route('/')
def index():
    return render_template('index.html')

# Remove placeholders as they are now in blueprints

if __name__ == '__main__':
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            # Test connection
            db.session.execute(db.text('SELECT 1'))
            print("\n" + "="*40)
            print("DATABASE CONNECTION: SUCCESSFUL ✅")
            print("="*40 + "\n")
        except Exception as e:
            print("\n" + "="*40)
            print("DATABASE CONNECTION: FAILED ❌")
            print(f"Error: {e}")
            print("="*40 + "\n")
            
    app.run(debug=True)
