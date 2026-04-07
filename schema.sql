-- Smart Healthcare & Medication Adherence System Database Schema

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    age INTEGER
);

-- Doctors table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    specialization VARCHAR(255)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending' -- Pending, Approved, Rejected
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id SERIAL PRIMARY KEY,
    prescription_id INTEGER REFERENCES prescriptions(prescription_id) ON DELETE CASCADE,
    medicine_name VARCHAR(255) NOT NULL,
    dosage_mg INTEGER,
    times_per_day INTEGER,
    time_slot VARCHAR(100), -- Morning, Afternoon, Evening, Night (comma separated or JSON)
    food_timing VARCHAR(100), -- Before Food / After Food
    duration_days INTEGER
);

-- Medication Logs table
CREATE TABLE IF NOT EXISTS medication_logs (
    log_id SERIAL PRIMARY KEY,
    medicine_id INTEGER REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    time_slot VARCHAR(50), -- Morning, Afternoon, Night
    log_date DATE,
    taken_status VARCHAR(50) DEFAULT 'Pending' -- Taken, Missed, Pending
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Unseen' -- Seen, Unseen
);
