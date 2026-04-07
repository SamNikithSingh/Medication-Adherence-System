from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Appointment, Doctor, Prescription, MedicationLog, Notification
from logic import check_missed_doses, get_adherence_percentage
from datetime import datetime, timedelta

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'patient_id'):
        return redirect(url_for('index'))
    
    check_missed_doses() # Check for missed doses on each load
    
    appointments = Appointment.query.filter_by(patient_id=current_user.patient_id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.patient_id).all()
    
    # Daily schedule: Pending logs for today
    today_date = datetime.utcnow().date()
    
    logs = MedicationLog.query.join(MedicationLog.medicine).join(Prescription).filter(
        Prescription.patient_id == current_user.patient_id,
        MedicationLog.log_date == today_date
    ).order_by(MedicationLog.scheduled_time).all()
    
    daily_schedule = {
        'Morning': [l for l in logs if l.time_slot == 'Morning'],
        'Afternoon': [l for l in logs if l.time_slot == 'Afternoon'],
        'Night': [l for l in logs if l.time_slot == 'Night']
    }
    
    notifications = Notification.query.filter_by(patient_id=current_user.patient_id).order_by(Notification.created_at.desc()).all()
    adherence = get_adherence_percentage(current_user.patient_id)
    
    doctors = Doctor.query.all()
    
    return render_template('patient_dashboard.html', 
                           appointments=appointments, 
                           daily_schedule=daily_schedule,
                           notifications=notifications,
                           adherence=adherence,
                           doctors=doctors,
                           current_time=datetime.now().time())

@patient_bp.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    doctor_id = request.form.get('doctor_id')
    date_str = request.form.get('date') # Expecting YYYY-MM-DDTHH:MM
    
    new_appt = Appointment(
        patient_id=current_user.patient_id,
        doctor_id=int(doctor_id),
        appointment_date=datetime.strptime(date_str, '%Y-%m-%dT%H:%M'),
        status='Pending'
    )
    db.session.add(new_appt)
    db.session.commit()
    flash('Appointment booked successfully!', 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/mark_taken/<int:log_id>')
@login_required
def mark_taken(log_id):
    log = MedicationLog.query.get_or_404(log_id)
    # Check if log belongs to patient
    if log.medicine.prescription.patient_id == current_user.patient_id:
        log.taken_status = 'Taken'
        db.session.commit()
        flash(f'Marked {log.medicine.medicine_name} as Taken!', 'success')
    return redirect(url_for('patient.dashboard'))
