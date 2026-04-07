from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Appointment, Patient, Prescription, Medicine, MedicationLog
from logic import generate_medication_logs, get_adherence_percentage
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'doctor_id'):
        return redirect(url_for('index'))
    
    appointments = Appointment.query.filter_by(doctor_id=current_user.doctor_id).all()
    # Adherence for all patients of this doctor
    patients = Patient.query.join(Appointment).filter(Appointment.doctor_id == current_user.doctor_id).distinct().all()
    patient_adherence = {p.patient_id: get_adherence_percentage(p.patient_id) for p in patients}
    
    return render_template('doctor_dashboard.html', 
                           appointments=appointments, 
                           patient_adherence=patient_adherence)

@doctor_bp.route('/appointment/<int:appointment_id>/<string:action>')
@login_required
def manage_appointment(appointment_id, action):
    appt = Appointment.query.get_or_404(appointment_id)
    if action == 'approve':
        appt.status = 'Approved'
    elif action == 'reject':
        appt.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/prescribe/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def prescribe(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        # Create prescription
        prescription = Prescription(
            appointment_id=appt.appointment_id,
            doctor_id=current_user.doctor_id,
            patient_id=appt.patient_id
        )
        db.session.add(prescription)
        db.session.flush() # To get prescription_id
        
        # Get medicines from form (simplified for demo: processing multiple items)
        med_names = request.form.getlist('medicine_name')
        dosages = request.form.getlist('dosage')
        frequencies = request.form.getlist('times_per_day')
        slots = request.form.getlist('time_slots')
        durations = request.form.getlist('duration')
        food_timings = request.form.getlist('food_timing')
        
        for i in range(len(med_names)):
            med = Medicine(
                prescription_id=prescription.prescription_id,
                medicine_name=med_names[i],
                dosage_mg=int(dosages[i]),
                times_per_day=int(frequencies[i]),
                time_slot=slots[i],
                duration_days=int(durations[i]),
                food_timing=food_timings[i] if i < len(food_timings) else 'After Food'
            )
            db.session.add(med)
        
        db.session.commit()
        generate_medication_logs(prescription.prescription_id)
        flash('Prescription created and logs generated!', 'success')
        return redirect(url_for('doctor.dashboard'))
    
    return render_template('prescription_form.html', appointment=appt)
