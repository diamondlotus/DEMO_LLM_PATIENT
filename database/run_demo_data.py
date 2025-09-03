#!/usr/bin/env python3
"""
Demo Data Runner for LotusHealth
This script populates the database with demo data for testing the LLM AI agent
"""

import psycopg2
import os
import sys
from pathlib import Path

def run_demo_data():
    """Run the demo data SQL script"""
    
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'lotushealth')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Connection string
    conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Read and execute demo data SQL
        demo_sql_path = Path(__file__).parent / "demo_data.sql"
        
        if not demo_sql_path.exists():
            print(f"❌ Demo data SQL file not found: {demo_sql_path}")
            return False
            
        print("📖 Reading demo data SQL file...")
        with open(demo_sql_path, 'r') as f:
            sql_content = f.read()
        
        print("🚀 Executing demo data...")
        cursor.execute(sql_content)
        
        print("✅ Demo data executed successfully!")
        
        # Verify data was inserted
        print("\n📊 Verifying demo data...")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Users: {user_count}")
        
        # Check patients
        cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        print(f"   🏥 Patients: {patient_count}")
        
        # Check doctors
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = cursor.fetchone()[0]
        print(f"   👨‍⚕️ Doctors: {doctor_count}")
        
        # Check appointments
        cursor.execute("SELECT COUNT(*) FROM appointments")
        appointment_count = cursor.fetchone()[0]
        print(f"   📅 Appointments: {appointment_count}")
        
        # Check knowledge base
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        kb_count = cursor.fetchone()[0]
        print(f"   📚 Knowledge Base: {kb_count}")
        
        # Check medical records
        cursor.execute("SELECT COUNT(*) FROM medical_records")
        mr_count = cursor.fetchone()[0]
        print(f"   📋 Medical Records: {mr_count}")
        
        # Check LLM interactions
        cursor.execute("SELECT COUNT(*) FROM llm_interactions")
        llm_count = cursor.fetchone()[0]
        print(f"   🤖 LLM Interactions: {llm_count}")
        
        print("\n🎉 Demo data setup complete!")
        print("\n🔑 Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Doctor: dr.smith / doctor123")
        print("   Nurse: nurse.brown / nurse123")
        print("   Receptionist: receptionist.davis / receptionist123")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    print("🏥 LotusHealth Demo Data Setup")
    print("=" * 40)
    
    success = run_demo_data()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🌐 You can now access the frontend at: http://localhost")
        print("🤖 Test the AI Agent with the demo medical scenarios!")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)
