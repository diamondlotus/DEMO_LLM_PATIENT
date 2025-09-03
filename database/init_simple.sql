-- Simple initialization script for LotusHealth PostgreSQL
-- Create tables and insert demo data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth TIMESTAMP NOT NULL,
    gender VARCHAR(10) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    emergency_contact VARCHAR(100) NOT NULL,
    insurance_info JSONB,
    medical_history TEXT,
    allergies TEXT[],
    medications TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create doctors table
CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    years_experience INTEGER,
    education TEXT[],
    certifications TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    -- LLM Integration fields
    expertise_embedding JSONB,  -- Embeddings of doctor's expertise
    ai_assistant_enabled BOOLEAN DEFAULT TRUE,  -- Whether AI assistant is enabled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) NOT NULL,
    doctor_id UUID REFERENCES doctors(id) NOT NULL,
    appointment_type VARCHAR(50) NOT NULL CHECK (appointment_type IN ('office_visit', 'consultation', 'follow_up', 'emergency', 'routine_checkup')),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')),
    scheduled_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create schedules table
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID REFERENCES doctors(id) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create knowledge_base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(200),
    version VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    content_embedding JSONB,
    keywords TEXT[],
    related_topics TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create patient_education table
CREATE TABLE IF NOT EXISTS patient_education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    is_read BOOLEAN DEFAULT FALSE,
    ai_generated BOOLEAN DEFAULT FALSE,
    personalization_factors JSONB,
    comprehension_check JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo users with hashed passwords
-- Password for all demo users is "admin123" (hashed with bcrypt)
INSERT INTO users (id, username, email, password_hash, first_name, last_name, full_name, role, is_active, created_at, updated_at) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'admin', 'admin@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'System', 'Administrator', 'System Administrator', 'admin', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440002', 'dr.smith', 'dr.smith@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'John', 'Smith', 'Dr. John Smith', 'doctor', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440003', 'nurse.jones', 'nurse.jones@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'Sarah', 'Jones', 'Nurse Sarah Jones', 'nurse', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440004', 'receptionist.wilson', 'receptionist.wilson@lotushealth.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.G', 'Mary', 'Wilson', 'Mary Wilson', 'receptionist', true, NOW(), NOW())
ON CONFLICT (username) DO NOTHING;

-- Insert demo doctor
INSERT INTO doctors (id, user_id, specialization, license_number, years_experience, education, certifications, is_active, created_at, updated_at) VALUES
    ('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440002', 'Cardiology', 'MD12345', 15, ARRAY['Harvard Medical School', 'Johns Hopkins University'], ARRAY['Board Certified Cardiologist', 'Fellow of American College of Cardiology'], true, NOW(), NOW())
ON CONFLICT (license_number) DO NOTHING;

-- Insert demo patients
INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, phone, email, address, emergency_contact, insurance_info, medical_history, allergies, medications, created_at, updated_at) VALUES
    ('750e8400-e29b-41d4-a716-446655440001', 'John', 'Doe', '1985-03-15 00:00:00', 'male', '+1-555-0101', 'john.doe@email.com', '123 Main St, Anytown, USA', 'Jane Doe (Wife) +1-555-0102', '{"provider": "Blue Cross", "policy_number": "BC123456"}', 'Hypertension, Type 2 Diabetes', ARRAY['Penicillin', 'Sulfa drugs'], ARRAY['Metformin 500mg', 'Lisinopril 10mg'], NOW(), NOW()),
    ('750e8400-e29b-41d4-a716-446655440002', 'Jane', 'Smith', '1990-07-22 00:00:00', 'female', '+1-555-0202', 'jane.smith@email.com', '456 Oak Ave, Somewhere, USA', 'Bob Smith (Husband) +1-555-0203', '{"provider": "Aetna", "policy_number": "AE789012"}', 'Asthma, Seasonal allergies', ARRAY['None known'], ARRAY['Albuterol inhaler'], NOW(), NOW()),
    ('750e8400-e29b-41d4-a716-446655440003', 'Mike', 'Johnson', '1978-11-08 00:00:00', 'male', '+1-555-0303', 'mike.johnson@email.com', '789 Pine Rd, Elsewhere, USA', 'Lisa Johnson (Wife) +1-555-0304', '{"provider": "Cigna", "policy_number": "CI345678"}', 'High cholesterol, GERD', ARRAY['None known'], ARRAY['Atorvastatin 20mg', 'Omeprazole 20mg'], NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Insert demo appointment
INSERT INTO appointments (id, patient_id, doctor_id, appointment_type, status, scheduled_date, duration_minutes, notes, created_at, updated_at) VALUES
    ('850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001', 'office_visit', 'scheduled', NOW() + INTERVAL '1 day', 30, 'Follow-up for diabetes management', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_schedules_doctor ON schedules(doctor_id);
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_active ON knowledge_base(is_active);
CREATE INDEX IF NOT EXISTS idx_patient_education_patient ON patient_education(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_education_topic ON patient_education(topic);

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'LotusHealth database initialized successfully with demo data';
    RAISE NOTICE 'Demo users created: admin, dr.smith, nurse.jones, receptionist.wilson';
    RAISE NOTICE 'Password for all demo users: admin123';
    RAISE NOTICE 'Demo patients created: John Doe, Jane Smith, Mike Johnson';
    RAISE NOTICE 'Demo doctor created: Dr. John Smith (Cardiology)';
    RAISE NOTICE 'Demo appointment created';
END $$;
