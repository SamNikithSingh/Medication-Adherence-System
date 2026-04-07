from datetime import datetime, timedelta
from models import db, MedicationLog, Notification, Medicine, Prescription

def generate_medication_logs(prescription_id):
    """
    Automatically generate medication logs for each day and time slot
    based on the medicines in a prescription.
    """
    prescription = Prescription.query.get(prescription_id)
    if not prescription:
        return

    for medicine in prescription.medicines:
        # Time slots map to deadline hours
        slots = [s.strip() for s in medicine.time_slot.split(',')]
        deadline_map = {
            'Morning': 10,   # 10:00 AM
            'Afternoon': 14, # 02:00 PM
            'Night': 24      # Midnight
        }

        # Start from today
        start_date = datetime.utcnow().date()
        
        for day in range(medicine.duration_days):
            current_date = start_date + timedelta(days=day)
            for slot in slots:
                if slot in deadline_map:
                    # Deadline timestamp
                    scheduled_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=deadline_map[slot])
                    
                    log = MedicationLog(
                        medicine_id=medicine.medicine_id,
                        scheduled_time=scheduled_time,
                        time_slot=slot,
                        log_date=current_date,
                        taken_status='Pending'
                    )
                    db.session.add(log)
    
    db.session.commit()

def check_missed_doses():
    """
    Check for doses that were not marked 'Taken' before their deadline.
    Update status to 'Missed' and create a notification.
    """
    now = datetime.utcnow()
    
    pending_logs = MedicationLog.query.filter(
        MedicationLog.scheduled_time < now,
        MedicationLog.taken_status == 'Pending'
    ).all()

    for log in pending_logs:
        # Ignore legacy Night logs that expire at 21:00 until 24:00
        if log.time_slot == 'Night' and log.scheduled_time.hour == 21:
            if now < log.scheduled_time + timedelta(hours=3):
                continue
                
        log.taken_status = 'Missed'
        # Get patient_id from medicine -> prescription
        patient_id = log.medicine.prescription.patient_id
        
        # Create notification
        notif = Notification(
            patient_id=patient_id,
            message=f"You missed your {log.time_slot} medicine: {log.medicine.medicine_name}"
        )
        db.session.add(notif)
    
    db.session.commit()

def get_adherence_percentage(patient_id):
    """
    Calculate adherence percentage for a patient.
    (Taken / Total logs that are not Pending)
    """
    logs = MedicationLog.query.join(Medicine).join(Prescription).filter(
        Prescription.patient_id == patient_id
    ).all()
    
    total = len([l for l in logs if l.taken_status != 'Pending'])
    taken = len([l for l in logs if l.taken_status == 'Taken'])
    
    if total == 0:
        return 100.0
    return round((taken / total) * 100, 2)
