from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Patient, Doctor

auth = Blueprint('auth', __name__)

@auth.route('/login/patient', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        patient = Patient.query.filter_by(email=email).first()
        if patient and check_password_hash(patient.password, password):
            login_user(patient)
            return redirect(url_for('patient.dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login_patient.html')

@auth.route('/login/doctor', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.password, password):
            login_user(doctor)
            return redirect(url_for('doctor.dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login_doctor.html')

@auth.route('/register/patient', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        
        if Patient.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        else:
            new_patient = Patient(
                name=name,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                age=int(age) if age else None
            )
            db.session.add(new_patient)
            db.session.commit()
            return redirect(url_for('auth.patient_login'))
    return render_template('register_patient.html')

@auth.route('/register/doctor', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        spec = request.form.get('specialization')
        
        if Doctor.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        else:
            new_doctor = Doctor(
                name=name,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
                specialization=spec
            )
            db.session.add(new_doctor)
            db.session.commit()
            return redirect(url_for('auth.doctor_login'))
    return render_template('register_doctor.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
