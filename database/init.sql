-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For GIN indexes on arrays

-- Create database if it doesn't exist
-- (This will be handled by the POSTGRES_DB environment variable)

-- Set timezone
SET timezone = 'UTC';

-- Create custom types if needed
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'doctor', 'nurse', 'receptionist', 'patient');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE appointment_status AS ENUM ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE appointment_type AS ENUM ('office_visit', 'consultation', 'follow_up', 'emergency', 'routine_checkup');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE visit_type AS ENUM ('new_patient', 'established_patient', 'urgent_care', 'specialist_consultation');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_patients_dob ON patients(date_of_birth);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);

CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

CREATE INDEX IF NOT EXISTS idx_office_visits_patient ON office_visits(patient_id);
CREATE INDEX IF NOT EXISTS idx_office_visits_doctor ON office_visits(doctor_id);
CREATE INDEX IF NOT EXISTS idx_office_visits_date ON office_visits(visit_date);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_medical_records_content_fts ON medical_records USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_patients_medical_history_fts ON patients USING gin(to_tsvector('english', medical_history));

-- Create GIN indexes for array fields
CREATE INDEX IF NOT EXISTS idx_patients_allergies ON patients USING gin(allergies);
CREATE INDEX IF NOT EXISTS idx_patients_medications ON patients USING gin(medications);
CREATE INDEX IF NOT EXISTS idx_doctors_education ON doctors USING gin(education);
CREATE INDEX IF NOT EXISTS idx_doctors_certifications ON doctors USING gin(certifications);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_office_visits_patient_date ON office_visits(patient_id, visit_date);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE lotushealth TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_office_visits_updated_at BEFORE UPDATE ON office_visits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function to calculate patient age
CREATE OR REPLACE FUNCTION calculate_age(birth_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(birth_date));
END;
$$ LANGUAGE plpgsql;

-- Create a function to get patient full name
CREATE OR REPLACE FUNCTION get_patient_full_name(patient_id UUID)
RETURNS TEXT AS $$
DECLARE
    full_name TEXT;
BEGIN
    SELECT CONCAT(first_name, ' ', last_name) INTO full_name
    FROM patients
    WHERE id = patient_id;
    
    RETURN full_name;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get doctor full name
CREATE OR REPLACE FUNCTION get_doctor_full_name(doctor_id UUID)
RETURNS TEXT AS $$
DECLARE
    full_name TEXT;
BEGIN
    SELECT u.full_name INTO full_name
    FROM doctors d
    JOIN users u ON d.user_id = u.id
    WHERE d.id = doctor_id;
    
    RETURN full_name;
END;
$$ LANGUAGE plpgsql;

-- Create a view for patient appointments with doctor and patient names
CREATE OR REPLACE VIEW patient_appointments_view AS
SELECT 
    a.id,
    a.scheduled_date,
    a.appointment_type,
    a.status,
    a.duration_minutes,
    a.notes,
    get_patient_full_name(a.patient_id) as patient_name,
    get_doctor_full_name(a.doctor_id) as doctor_name,
    a.created_at,
    a.updated_at
FROM appointments a;

-- Create a view for office visits with patient and doctor names
CREATE OR REPLACE VIEW office_visits_view AS
SELECT 
    ov.id,
    ov.visit_date,
    ov.visit_type,
    ov.chief_complaint,
    ov.diagnosis,
    ov.treatment_plan,
    get_patient_full_name(ov.patient_id) as patient_name,
    get_doctor_full_name(ov.doctor_id) as doctor_name,
    ov.created_at,
    ov.updated_at
FROM office_visits ov;

-- Create a view for dashboard statistics
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM patients) as total_patients,
    (SELECT COUNT(*) FROM appointments) as total_appointments,
    (SELECT COUNT(*) FROM appointments WHERE DATE(scheduled_date) = CURRENT_DATE) as today_appointments,
    (SELECT COUNT(*) FROM office_visits WHERE DATE(visit_date) = CURRENT_DATE) as today_visits,
    (SELECT COUNT(*) FROM appointments WHERE status = 'scheduled') as pending_appointments,
    (SELECT COUNT(*) FROM users WHERE role = 'doctor' AND is_active = true) as active_doctors,
    (SELECT COUNT(*) FROM users WHERE role = 'nurse' AND is_active = true) as active_nurses;

-- Insert sample data for testing
INSERT INTO users (id, username, email, password_hash, full_name, role, is_active, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'admin', 'admin@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'System Administrator', 'admin', true, NOW(), NOW()),
    (uuid_generate_v4(), 'dr.smith', 'dr.smith@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'Dr. John Smith', 'doctor', true, NOW(), NOW()),
    (uuid_generate_v4(), 'nurse.jones', 'nurse.jones@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'Nurse Sarah Jones', 'nurse', true, NOW(), NOW()),
    (uuid_generate_v4(), 'receptionist.wilson', 'receptionist.wilson@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'Mary Wilson', 'receptionist', true, NOW(), NOW())
ON CONFLICT (username) DO NOTHING;

-- Insert sample doctors
INSERT INTO doctors (id, user_id, specialization, license_number, years_experience, education, certifications, is_active, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    u.id,
    'Cardiology',
    'MD12345',
    15,
    ARRAY['Harvard Medical School', 'Johns Hopkins University'],
    ARRAY['Board Certified Cardiologist', 'Fellow of American College of Cardiology'],
    true,
    NOW(),
    NOW()
FROM users u WHERE u.username = 'dr.smith'
ON CONFLICT (license_number) DO NOTHING;

-- Insert sample patients
INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, phone, email, address, emergency_contact, insurance_info, medical_history, allergies, medications, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'John', 'Doe', '1985-03-15', 'male', '+1-555-0101', 'john.doe@email.com', '123 Main St, Anytown, USA', 'Jane Doe (Wife) +1-555-0102', '{"provider": "Blue Cross", "policy_number": "BC123456"}', 'Hypertension, Type 2 Diabetes', ARRAY['Penicillin', 'Sulfa drugs'], ARRAY['Metformin 500mg', 'Lisinopril 10mg'], NOW(), NOW()),
    (uuid_generate_v4(), 'Jane', 'Smith', '1990-07-22', 'female', '+1-555-0202', 'jane.smith@email.com', '456 Oak Ave, Somewhere, USA', 'Bob Smith (Husband) +1-555-0203', '{"provider": "Aetna", "policy_number": "AE789012"}', 'Asthma, Seasonal allergies', ARRAY['None known'], ARRAY['Albuterol inhaler'], NOW(), NOW()),
    (uuid_generate_v4(), 'Mike', 'Johnson', '1978-11-08', 'male', '+1-555-0303', 'mike.johnson@email.com', '789 Pine Rd, Elsewhere, USA', 'Lisa Johnson (Wife) +1-555-0304', '{"provider": "Cigna", "policy_number": "CI345678"}', 'High cholesterol, GERD', ARRAY['None known'], ARRAY['Atorvastatin 20mg', 'Omeprazole 20mg'], NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Insert sample appointments
INSERT INTO appointments (id, patient_id, doctor_id, appointment_type, status, scheduled_date, duration_minutes, notes, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    p.id,
    d.id,
    'office_visit',
    'scheduled',
    NOW() + INTERVAL '1 day',
    30,
    'Follow-up for diabetes management',
    NOW(),
    NOW()
FROM patients p, doctors d
WHERE p.last_name = 'Doe' AND d.license_number = 'MD12345'
ON CONFLICT DO NOTHING;

-- Insert sample office visit
INSERT INTO office_visits (id, patient_id, doctor_id, visit_type, chief_complaint, vital_signs, examination_notes, diagnosis, treatment_plan, prescriptions, visit_date, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    p.id,
    d.id,
    'established_patient',
    'Chest pain and shortness of breath',
    '{"blood_pressure": "140/90", "heart_rate": "85", "temperature": "98.6", "oxygen_saturation": "95"}',
    'Patient reports chest pain radiating to left arm. EKG shows normal sinus rhythm. No signs of acute coronary syndrome.',
    'Stable angina',
    'Continue current medications. Schedule stress test. Follow up in 2 weeks.',
    ARRAY['Nitroglycerin PRN', 'Aspirin 81mg daily'],
    NOW() - INTERVAL '1 day',
    NOW(),
    NOW()
FROM patients p, doctors d
WHERE p.last_name = 'Doe' AND d.license_number = 'MD12345'
ON CONFLICT DO NOTHING;

-- Insert sample medical records
INSERT INTO medical_records (id, patient_id, record_type, content, metadata, created_at, updated_at)
SELECT 
    uuid_generate_v4(),
    p.id,
    'diagnosis',
    'Type 2 Diabetes Mellitus - Diagnosed 2020. Currently managed with Metformin and lifestyle modifications.',
    '{"icd10_code": "E11.9", "severity": "moderate", "complications": "none"}',
    NOW(),
    NOW()
FROM patients p WHERE p.last_name = 'Doe'
ON CONFLICT DO NOTHING;

-- Create indexes on the views for better performance
CREATE INDEX IF NOT EXISTS idx_patient_appointments_view_date ON patient_appointments_view(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_office_visits_view_date ON office_visits_view(visit_date);

-- Grant permissions on views
GRANT SELECT ON patient_appointments_view TO postgres;
GRANT SELECT ON office_visits_view TO postgres;
GRANT SELECT ON dashboard_stats TO postgres;

-- Create a function to get patient summary
CREATE OR REPLACE FUNCTION get_patient_summary(patient_id UUID)
RETURNS JSON AS $$
DECLARE
    patient_data JSON;
    appointments_data JSON;
    visits_data JSON;
    records_data JSON;
    result JSON;
BEGIN
    -- Get patient basic info
    SELECT json_build_object(
        'id', p.id,
        'name', CONCAT(p.first_name, ' ', p.last_name),
        'age', calculate_age(p.date_of_birth),
        'gender', p.gender,
        'medical_history', p.medical_history,
        'allergies', p.allergies,
        'medications', p.medications
    ) INTO patient_data
    FROM patients p
    WHERE p.id = patient_id;
    
    -- Get recent appointments
    SELECT json_agg(json_build_object(
        'id', a.id,
        'date', a.scheduled_date,
        'type', a.appointment_type,
        'status', a.status,
        'doctor', get_doctor_full_name(a.doctor_id)
    )) INTO appointments_data
    FROM appointments a
    WHERE a.patient_id = patient_id
    ORDER BY a.scheduled_date DESC
    LIMIT 5;
    
    -- Get recent office visits
    SELECT json_agg(json_build_object(
        'id', ov.id,
        'date', ov.visit_date,
        'type', ov.visit_type,
        'chief_complaint', ov.chief_complaint,
        'diagnosis', ov.diagnosis
    )) INTO visits_data
    FROM office_visits ov
    WHERE ov.patient_id = patient_id
    ORDER BY ov.visit_date DESC
    LIMIT 5;
    
    -- Get recent medical records
    SELECT json_agg(json_build_object(
        'id', mr.id,
        'type', mr.record_type,
        'content', mr.content,
        'date', mr.created_at
    )) INTO records_data
    FROM medical_records mr
    WHERE mr.patient_id = patient_id
    ORDER BY mr.created_at DESC
    LIMIT 5;
    
    -- Build final result
    result = json_build_object(
        'patient', patient_data,
        'recent_appointments', appointments_data,
        'recent_visits', visits_data,
        'recent_records', records_data,
        'summary_date', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION get_patient_summary(UUID) TO postgres;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'LotusHealth database initialized successfully with sample data';
    RAISE NOTICE 'Sample users created: admin, dr.smith, nurse.jones, receptionist.wilson';
    RAISE NOTICE 'Sample patients created: John Doe, Jane Smith, Mike Johnson';
    RAISE NOTICE 'Sample appointments and office visits created';
    RAISE NOTICE 'Database ready for use with LLM integration';
END $$;
