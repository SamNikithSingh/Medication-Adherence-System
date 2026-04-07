from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)

    def get_id(self):
        return f"patient_{self.patient_id}"

class Doctor(UserMixin, db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(255))

    def get_id(self):
        return f"doctor_{self.doctor_id}"

class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Pending')

    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    prescription_id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', backref='prescriptions')
    doctor = db.relationship('Doctor', backref='prescriptions')
    patient = db.relationship('Patient', backref='prescriptions')

class Medicine(db.Model):
    __tablename__ = 'medicines'
    medicine_id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.prescription_id'))
    medicine_name = db.Column(db.String(255), nullable=False)
    dosage_mg = db.Column(db.Integer)
    times_per_day = db.Column(db.Integer)
    time_slot = db.Column(db.String(100)) # e.g. "Morning, Evening"
    food_timing = db.Column(db.String(100))
    duration_days = db.Column(db.Integer)

    prescription = db.relationship('Prescription', backref='medicines')

class MedicationLog(db.Model):
    __tablename__ = 'medication_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'))
    scheduled_time = db.Column(db.DateTime, nullable=False) # This will store the deadline
    time_slot = db.Column(db.String(50)) # Morning, Afternoon, Night
    log_date = db.Column(db.Date)
    taken_status = db.Column(db.String(50), default='Pending')

    medicine = db.relationship('Medicine', backref='logs')

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Unseen')

    patient = db.relationship('Patient', backref='notifications')
