#!/usr/bin/env python3
"""
Run appointment constraints migration
"""

import sys
import os
import logging
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the appointment constraints migration"""
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'lotushealth'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        # Connect to database using connection string
        connection_string = f"host={db_config['host']} port={db_config['port']} dbname={db_config['database']} user={db_config['username']} password={db_config['password']}"
        conn = connect(connection_string)
        cursor = conn.cursor()
        
        logger.info("Connected to database successfully")
        
        # Check if constraints already exist
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'appointments' 
            AND constraint_type = 'CHECK'
            AND constraint_name IN ('chk_appointment_type', 'chk_appointment_status')
        """)
        
        existing_constraints = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing constraints: {existing_constraints}")
        
        # Add appointment_type constraint if it doesn't exist
        if 'chk_appointment_type' not in existing_constraints:
            logger.info("Adding appointment_type constraint...")
            cursor.execute("""
                ALTER TABLE appointments 
                ADD CONSTRAINT chk_appointment_type 
                CHECK (appointment_type IN ('office_visit', 'consultation', 'follow_up', 'emergency', 'routine_checkup'))
            """)
            logger.info("appointment_type constraint added successfully")
        else:
            logger.info("appointment_type constraint already exists")
        
        # Add status constraint if it doesn't exist
        if 'chk_appointment_status' not in existing_constraints:
            logger.info("Adding appointment status constraint...")
            cursor.execute("""
                ALTER TABLE appointments 
                ADD CONSTRAINT chk_appointment_status 
                CHECK (status IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'))
            """)
            logger.info("appointment status constraint added successfully")
        else:
            logger.info("appointment status constraint already exists")
        
        # Update any existing invalid data
        logger.info("Updating invalid appointment_type values...")
        cursor.execute("""
            UPDATE appointments 
            SET appointment_type = 'office_visit' 
            WHERE appointment_type NOT IN ('office_visit', 'consultation', 'follow_up', 'emergency', 'routine_checkup')
        """)
        updated_types = cursor.rowcount
        logger.info(f"Updated {updated_types} appointment_type values")
        
        logger.info("Updating invalid status values...")
        cursor.execute("""
            UPDATE appointments 
            SET status = 'scheduled' 
            WHERE status NOT IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show')
        """)
        updated_statuses = cursor.rowcount
        logger.info(f"Updated {updated_statuses} status values")
        
        # Add LLM fields to appointments table
        logger.info("Adding LLM fields to appointments table...")
        cursor.execute("""
            ALTER TABLE appointments 
            ADD COLUMN IF NOT EXISTS ai_notes TEXT,
            ADD COLUMN IF NOT EXISTS risk_assessment JSONB,
            ADD COLUMN IF NOT EXISTS follow_up_recommendations TEXT
        """)
        logger.info("LLM fields added to appointments table")
        
        # Add LLM fields to patients table
        logger.info("Adding LLM fields to patients table...")
        cursor.execute("""
            ALTER TABLE patients 
            ADD COLUMN IF NOT EXISTS medical_notes_embedding JSONB,
            ADD COLUMN IF NOT EXISTS risk_factors JSONB,
            ADD COLUMN IF NOT EXISTS treatment_recommendations JSONB
        """)
        logger.info("LLM fields added to patients table")
        
        # Add LLM fields to doctors table
        logger.info("Adding LLM fields to doctors table...")
        cursor.execute("""
            ALTER TABLE doctors 
            ADD COLUMN IF NOT EXISTS expertise_embedding JSONB,
            ADD COLUMN IF NOT EXISTS ai_assistant_enabled BOOLEAN DEFAULT TRUE
        """)
        logger.info("LLM fields added to doctors table")
        
        # Update existing records to have default values
        logger.info("Updating existing records with default values...")
        cursor.execute("""
            UPDATE appointments 
            SET ai_notes = NULL, risk_assessment = NULL, follow_up_recommendations = NULL
            WHERE ai_notes IS NULL
        """)
        appointments_updated = cursor.rowcount
        
        cursor.execute("""
            UPDATE patients 
            SET medical_notes_embedding = NULL, risk_factors = NULL, treatment_recommendations = NULL
            WHERE medical_notes_embedding IS NULL
        """)
        patients_updated = cursor.rowcount
        
        cursor.execute("""
            UPDATE doctors 
            SET expertise_embedding = NULL, ai_assistant_enabled = TRUE
            WHERE expertise_embedding IS NULL
        """)
        doctors_updated = cursor.rowcount
        
        logger.info(f"Updated {appointments_updated} appointments, {patients_updated} patients, {doctors_updated} doctors")
        
        # Commit changes
        conn.commit()
        logger.info("Migration completed successfully!")
        
        # Verify constraints
        cursor.execute("""
            SELECT constraint_name, check_clause
            FROM information_schema.check_constraints
            WHERE constraint_name IN ('chk_appointment_type', 'chk_appointment_status')
        """)
        
        constraints = cursor.fetchall()
        logger.info("Current constraints:")
        for constraint_name, check_clause in constraints:
            logger.info(f"  {constraint_name}: {check_clause}")
        
        # Verify new LLM fields
        logger.info("Verifying new LLM fields...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'appointments' 
            AND column_name IN ('ai_notes', 'risk_assessment', 'follow_up_recommendations')
        """)
        
        new_appointment_fields = cursor.fetchall()
        logger.info("New appointment fields:")
        for field_name, data_type in new_appointment_fields:
            logger.info(f"  {field_name}: {data_type}")
        
        # Add missing tables
        logger.info("Adding missing tables...")
        
        # Create knowledge_base table
        cursor.execute("""
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
            )
        """)
        logger.info("knowledge_base table created/verified")
        
        # Create patient_education table
        cursor.execute("""
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
            )
        """)
        logger.info("patient_education table created/verified")
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_base_active ON knowledge_base(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_education_patient ON patient_education(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_education_topic ON patient_education(topic)")
        logger.info("Indexes created/verified")
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = cursor.fetchone()[0]
        if kb_count == 0:
            cursor.execute("""
                INSERT INTO knowledge_base (id, category, title, content, source, version, is_active, created_at, updated_at) VALUES
                (uuid_generate_v4(), 'medical_guidelines', 'Hypertension Management', 'Comprehensive guidelines for managing hypertension in adults...', 'American Heart Association', '2023.1', true, NOW(), NOW()),
                (uuid_generate_v4(), 'drug_info', 'Metformin Information', 'Metformin is an oral diabetes medicine that helps control blood sugar levels...', 'FDA Drug Database', '2023.2', true, NOW(), NOW()),
                (uuid_generate_v4(), 'disease_info', 'Type 2 Diabetes Overview', 'Type 2 diabetes is a chronic condition that affects how your body metabolizes glucose...', 'CDC Guidelines', '2023.1', true, NOW(), NOW())
            """)
            logger.info("Sample knowledge base data inserted")
        
        cursor.execute("SELECT COUNT(*) FROM patient_education")
        pe_count = cursor.fetchone()[0]
        if pe_count == 0:
            cursor.execute("""
                INSERT INTO patient_education (id, patient_id, topic, content, difficulty_level, language, created_at) VALUES
                (uuid_generate_v4(), '750e8400-e29b-41d4-a716-446655440001', 'Diabetes Management', 'Learn about managing your diabetes through diet, exercise, and medication...', 'basic', 'en', NOW()),
                (uuid_generate_v4(), '750e8400-e29b-41d4-a716-446655440002', 'Asthma Care', 'Understanding your asthma triggers and how to use your inhaler properly...', 'basic', 'en', NOW())
            """)
            logger.info("Sample patient education data inserted")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
