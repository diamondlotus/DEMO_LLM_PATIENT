"""
AI Service - Demo Data Loader
Loads medical knowledge and demo data into the AI knowledge base
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm_integration.healthcare_llm import HealthcareLLM

class DemoDataLoader:
    """Load demo medical data into AI knowledge base"""

    def __init__(self):
        self.healthcare_llm = HealthcareLLM()
        self.demo_medical_data = self._get_demo_medical_data()

    def _get_demo_medical_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive demo medical data"""
        return [
            # Common Symptoms and Conditions
            {
                "content": """
                Chest pain is a common symptom that can indicate various conditions:
                - Coronary artery disease (heart attack, angina)
                - Pulmonary embolism
                - Pneumonia or pleuritis
                - Gastroesophageal reflux disease (GERD)
                - Musculoskeletal pain
                - Anxiety or panic attacks

                Key assessment points:
                - Location, radiation, character, duration, severity
                - Associated symptoms (shortness of breath, nausea, sweating)
                - Risk factors (age, smoking, family history, hypertension)
                - Timing (at rest, exertion, meals)

                Red flags requiring immediate attention:
                - Crushing substernal chest pain > 20 minutes
                - Chest pain with shortness of breath, sweating, nausea
                - Chest pain radiating to left arm or jaw
                - Chest pain in patients with known heart disease
                """,
                "metadata": {
                    "category": "cardiology",
                    "type": "symptom_assessment",
                    "priority": "high",
                    "source": "demo_data"
                }
            },

            # Respiratory Conditions
            {
                "content": """
                Shortness of breath (dyspnea) assessment:
                - Acute vs chronic onset
                - Associated with exertion, rest, or positional changes
                - Accompanied by chest pain, cough, wheezing
                - Risk factors: smoking, asthma, COPD, heart disease

                Common causes:
                - Asthma exacerbation
                - Chronic obstructive pulmonary disease (COPD)
                - Congestive heart failure
                - Pulmonary embolism
                - Pneumonia
                - Anxiety/panic disorder

                Emergency signs:
                - Severe respiratory distress
                - Cyanosis (blue discoloration)
                - Unable to speak in full sentences
                - Altered mental status
                """,
                "metadata": {
                    "category": "pulmonology",
                    "type": "respiratory_assessment",
                    "priority": "high",
                    "source": "demo_data"
                }
            },

            # Neurological Symptoms
            {
                "content": """
                Headache assessment and classification:
                - Primary headaches: migraine, tension, cluster
                - Secondary headaches: due to underlying conditions
                - Red flags: sudden onset, worst headache ever, neurological symptoms

                Migraine characteristics:
                - Unilateral throbbing pain
                - Associated with nausea, photophobia, phonophobia
                - May have aura (visual disturbances)
                - Triggers: stress, certain foods, hormonal changes

                Tension headache:
                - Bilateral band-like pressure
                - Mild to moderate intensity
                - No associated symptoms
                - Related to stress, poor posture, eye strain

                Emergency evaluation needed for:
                - New onset severe headache
                - Headache with fever, neck stiffness
                - Headache with focal neurological signs
                - Headache in immunocompromised patients
                """,
                "metadata": {
                    "category": "neurology",
                    "type": "headache_assessment",
                    "priority": "medium",
                    "source": "demo_data"
                }
            },

            # Gastrointestinal Conditions
            {
                "content": """
                Abdominal pain assessment:
                - Location: epigastric, right upper quadrant, left lower quadrant, etc.
                - Character: sharp, dull, cramping, burning
                - Radiation: to back, shoulder, groin
                - Timing: relation to meals, bowel movements
                - Associated symptoms: nausea, vomiting, diarrhea, constipation

                Common causes by location:
                - Epigastric: gastritis, GERD, pancreatitis, myocardial infarction
                - Right upper quadrant: cholecystitis, hepatitis, pneumonia
                - Left lower quadrant: diverticulitis, ovarian pathology
                - Diffuse: gastroenteritis, bowel obstruction, peritonitis

                Red flags:
                - Severe pain with peritoneal signs
                - Pain with fever and leukocytosis
                - Pain in elderly patients
                - Pain with unexplained weight loss
                """,
                "metadata": {
                    "category": "gastroenterology",
                    "type": "abdominal_pain",
                    "priority": "medium",
                    "source": "demo_data"
                }
            },

            # Medication Information
            {
                "content": """
                Common medication classes and considerations:

                Analgesics:
                - Acetaminophen (Tylenol): Safe for liver, avoid in alcoholics
                - NSAIDs (ibuprofen, naproxen): Risk of GI bleeding, renal toxicity
                - Opioids: Use only when necessary, monitor for dependence

                Antibiotics:
                - Penicillin: Check for allergies
                - Cephalosporins: Cross-reactivity with penicillin
                - Sulfa drugs: Risk of allergic reactions
                - Fluoroquinolones: Tendon rupture risk

                Cardiovascular medications:
                - Beta-blockers: Bradycardia, fatigue, erectile dysfunction
                - ACE inhibitors: Cough, hyperkalemia, angioedema
                - Statins: Muscle pain, liver toxicity
                - Anticoagulants: Bleeding risk, drug interactions

                Drug interaction considerations:
                - Warfarin with many medications
                - Statins with grapefruit juice
                - Digoxin with multiple drugs
                - Lithium with NSAIDs and diuretics
                """,
                "metadata": {
                    "category": "pharmacology",
                    "type": "medication_guide",
                    "priority": "high",
                    "source": "demo_data"
                }
            },

            # Pediatric Assessment
            {
                "content": """
                Pediatric vital signs by age:
                - Newborn: HR 120-160, RR 30-60, BP 60-90/30-50
                - 1 year: HR 80-140, RR 20-40, BP 85-105/50-70
                - 5 years: HR 65-130, RR 20-30, BP 90-110/50-70
                - 10 years: HR 60-110, RR 15-25, BP 95-115/55-75

                Common pediatric complaints:
                - Fever: Most common reason for pediatric visits
                - Ear pain: Often due to otitis media
                - Sore throat: Viral pharyngitis vs strep
                - Abdominal pain: Many causes, often benign
                - Vomiting/diarrhea: Dehydration risk

                Pediatric assessment considerations:
                - Developmental stage affects communication
                - Parental concerns often accurate
                - Growth parameters important
                - Immunization status relevant
                - Social history crucial (school, family, abuse risk)
                """,
                "metadata": {
                    "category": "pediatrics",
                    "type": "pediatric_assessment",
                    "priority": "medium",
                    "source": "demo_data"
                }
            },

            # Mental Health Assessment
            {
                "content": """
                Mental health assessment framework:
                - Appearance and behavior
                - Mood and affect
                - Thought process and content
                - Perception (hallucinations, delusions)
                - Cognition and memory
                - Insight and judgment
                - Suicidal/homicidal ideation

                Common presentations:
                - Depression: Persistent sadness, anhedonia, sleep/appetite changes
                - Anxiety: Excessive worry, restlessness, physical symptoms
                - Bipolar disorder: Mood swings, manic episodes
                - Schizophrenia: Hallucinations, delusions, disorganized thinking
                - Substance use: Patterns of use, withdrawal symptoms

                Risk assessment:
                - Suicidal ideation: Plan, intent, means
                - Homicidal ideation: Specific targets, plans
                - Self-harm: Cutting, overdose history
                - Danger to others: Threats, violent behavior
                - Functional impairment: Work, relationships, self-care

                Safety planning:
                - Remove means of self-harm
                - Support system identification
                - Crisis hotline numbers
                - Follow-up appointment scheduling
                """,
                "metadata": {
                    "category": "psychiatry",
                    "type": "mental_health",
                    "priority": "high",
                    "source": "demo_data"
                }
            },

            # Geriatric Assessment
            {
                "content": """
                Geriatric assessment considerations:
                - Polypharmacy: Multiple medications increase interaction risk
                - Age-related changes: Decreased renal/hepatic function
                - Cognitive impairment: May mask or mimic physical illness
                - Functional status: ADLs (activities of daily living)
                - Social support: Caregiver availability, living situation
                - Falls risk: Balance, vision, medications
                - Nutritional status: Weight loss, dehydration risk

                Common geriatric syndromes:
                - Delirium: Acute confusion, often medication-induced
                - Dementia: Chronic cognitive decline
                - Falls: Leading cause of injury
                - Incontinence: Urinary/fecal
                - Frailty: Decreased reserve capacity
                - Depression: Often underdiagnosed

                Medication considerations:
                - Start low, go slow with dosing
                - Beers criteria for inappropriate medications
                - Drug-disease interactions
                - Drug-drug interactions
                - Compliance issues

                Preventive care:
                - Annual wellness visits
                - Immunizations (flu, pneumonia, shingles)
                - Cancer screening appropriate to age
                - Osteoporosis screening
                - Hearing/vision assessment
                """,
                "metadata": {
                    "category": "geriatrics",
                    "type": "geriatric_assessment",
                    "priority": "medium",
                    "source": "demo_data"
                }
            }
        ]

    def load_demo_data(self) -> Dict[str, Any]:
        """Load all demo medical data into the knowledge base"""
        try:
            print("🔄 Loading demo medical data into AI knowledge base...")

            total_documents = len(self.demo_medical_data)
            successful_loads = 0

            for i, doc_data in enumerate(self.demo_medical_data, 1):
                try:
                    content = doc_data["content"]
                    metadata = doc_data["metadata"]

                    # Add to knowledge base
                    success = self.healthcare_llm.add_medical_knowledge([content], [metadata])

                    if success:
                        successful_loads += 1
                        print(f"✅ Loaded document {i}/{total_documents}: {metadata.get('category', 'unknown')}")
                    else:
                        print(f"❌ Failed to load document {i}/{total_documents}")

                except Exception as e:
                    print(f"❌ Error loading document {i}: {str(e)}")
                    continue

            return result

        except Exception as e:
            print(f"❌ Error in load_demo_data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

            result = {
                "success": True,
                "total_documents": total_documents,
                "successful_loads": successful_loads,
                "failure_count": total_documents - successful_loads,
                "timestamp": datetime.utcnow().isoformat(),
                "categories_loaded": list(set([
                    doc["metadata"]["category"]
                    for doc in self.demo_medical_data
                    if doc["metadata"]["category"]
                ]))
            }

            result = {
                "success": True,
                "total_documents": total_documents,
                "successful_loads": successful_loads,
                "failure_count": total_documents - successful_loads,
                "timestamp": datetime.utcnow().isoformat(),
                "categories_loaded": list(set([
                    doc["metadata"]["category"]
                    for doc in self.demo_medical_data
                    if doc["metadata"]["category"]
                ]))
            }

            print("\n📊 Demo Data Loading Summary:")
            print(f"   Total Documents: {total_documents}")
            print(f"   Successfully Loaded: {successful_loads}")
            print(f"   Failed: {total_documents - successful_loads}")
            print(f"   Categories: {', '.join(result['categories_loaded'])}")

            return result

        except Exception as e:
            print(f"❌ Error loading demo data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_demo_patient_scenarios(self) -> List[Dict[str, Any]]:
        """Get demo patient scenarios for testing"""
        return [
            {
                "scenario": "Acute Chest Pain",
                "note": "45-year-old male presents with sudden onset substernal chest pain radiating to left arm, associated with shortness of breath and diaphoresis. Pain started 30 minutes ago while at rest. No prior cardiac history. Smoker, family history of heart disease.",
                "expected_findings": ["cardiac_chest_pain", "high_risk", "immediate_evaluation"]
            },
            {
                "scenario": "Pediatric Fever",
                "note": "3-year-old female with fever to 102.5°F for 2 days, associated with cough and runny nose. No vomiting or diarrhea. Attending daycare. Immunizations up to date. Parents report child is drinking well and playful between fever spikes.",
                "expected_findings": ["viral_illness", "low_risk", "supportive_care"]
            },
            {
                "scenario": "Geriatric Fall",
                "note": "78-year-old female fell at home, now complaining of right hip pain. Unable to bear weight. Lives alone, takes multiple medications including warfarin for atrial fibrillation. No loss of consciousness. Last fall 6 months ago.",
                "expected_findings": ["hip_fracture", "anticoagulation", "urgent_orthopedic"]
            },
            {
                "scenario": "Mental Health Crisis",
                "note": "28-year-old male presents with suicidal ideation, expressing hopelessness and worthlessness. Reports recent job loss and relationship breakup. No prior psychiatric history. Denies substance use. Has specific plan to overdose on medications at home.",
                "expected_findings": ["suicidal_ideation", "high_risk", "immediate_intervention"]
            },
            {
                "scenario": "Abdominal Pain",
                "note": "32-year-old female with severe right lower quadrant abdominal pain for 12 hours. Pain is sharp, constant, worse with movement. Associated with nausea and low-grade fever. Last menstrual period 2 weeks ago. No prior similar episodes.",
                "expected_findings": ["acute_appendicitis", "surgical_emergency", "immediate_evaluation"]
            }
        ]

def load_demo_data() -> Dict[str, Any]:
    """Convenience function to load demo data"""
    loader = DemoDataLoader()
    return loader.load_demo_data()

def get_demo_scenarios() -> List[Dict[str, Any]]:
    """Convenience function to get demo scenarios"""
    loader = DemoDataLoader()
    return loader.get_demo_patient_scenarios()

if __name__ == "__main__":
    # Load demo data when script is run directly
    result = load_demo_data()
    print(f"\nDemo data loading result: {json.dumps(result, indent=2)}")