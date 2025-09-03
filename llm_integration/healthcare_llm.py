from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
import os
import sys

# Add project root to path to import database models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Database imports
from database.connection import get_db_session
from database.models.knowledge_base import KnowledgeBase
from database.models.llm_interaction import LLMInteraction
from database.models.patient import Patient
from database.models.medical_record import MedicalRecord
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareLLM:
    def __init__(self, openai_api_key: str = None):
        """Initialize Healthcare LLM with OpenAI integration"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.1,  # Lower temperature for medical accuracy
            openai_api_key=self.openai_api_key
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize vector store
        self.vector_store = None
        self._initialize_vector_store()
        
        # Initialize memory for conversations
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store for medical knowledge"""
        try:
            # Create or load existing vector store
            self.vector_store = Chroma(
                collection_name="healthcare_knowledge",
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Fallback to in-memory store
            self.vector_store = Chroma(
                collection_name="healthcare_knowledge",
                embedding_function=self.embeddings
            )
    
    def add_medical_knowledge(self, documents: List[str], metadata: List[Dict] = None):
        """Add medical knowledge documents to vector store"""
        try:
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadata or [{}] * len(texts)
            )
            
            logger.info(f"Added {len(texts)} medical knowledge chunks to vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to add medical knowledge: {e}")
            return False
    
    def get_patient_context(self, patient_data: Dict[str, Any]) -> str:
        """Generate patient context for LLM interactions"""
        context_parts = []
        
        if patient_data.get('medical_history'):
            context_parts.append(f"Medical History: {patient_data['medical_history']}")
        
        if patient_data.get('allergies'):
            context_parts.append(f"Allergies: {', '.join(patient_data['allergies'])}")
        
        if patient_data.get('medications'):
            context_parts.append(f"Current Medications: {', '.join(patient_data['medications'])}")
        
        if patient_data.get('age'):
            context_parts.append(f"Age: {patient_data['age']} years")
        
        if patient_data.get('gender'):
            context_parts.append(f"Gender: {patient_data['gender']}")
        
        return "\n".join(context_parts) if context_parts else "No specific patient context available."
    
    def get_patient_from_db(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve patient data from the shared clinic database"""
        try:
            with get_db_session() as session:
                patient = session.query(Patient).filter(Patient.id == patient_id).first()
                if patient:
                    return {
                        'id': str(patient.id),
                        'name': patient.full_name,
                        'age': patient.age,
                        'gender': patient.gender,
                        'medical_history': patient.medical_history,
                        'allergies': patient.allergies,
                        'current_medications': patient.current_medications,
                        'vital_signs': patient.vital_signs
                    }
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve patient data: {e}")
            return None
    
    def store_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Store LLM interaction in the shared database"""
        try:
            with get_db_session() as session:
                interaction = LLMInteraction(
                    patient_id=interaction_data.get('patient_id'),
                    doctor_id=interaction_data.get('doctor_id'),
                    interaction_type=interaction_data.get('interaction_type', 'general'),
                    user_input=interaction_data.get('user_input', ''),
                    llm_response=interaction_data.get('llm_response', ''),
                    context=interaction_data.get('context', {}),
                    confidence_score=interaction_data.get('confidence_score', 0.0)
                )
                session.add(interaction)
                session.commit()
                logger.info(f"Stored LLM interaction: {interaction.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return False
    
    def update_knowledge_base(self, knowledge_data: Dict[str, Any]) -> bool:
        """Update knowledge base in the shared database"""
        try:
            with get_db_session() as session:
                knowledge = KnowledgeBase(
                    category=knowledge_data.get('category', 'general'),
                    title=knowledge_data.get('title', ''),
                    content=knowledge_data.get('content', ''),
                    source=knowledge_data.get('source', 'ai_learning'),
                    version=knowledge_data.get('version', '1.0'),
                    keywords=knowledge_data.get('keywords', []),
                    related_topics=knowledge_data.get('related_topics', [])
                )
                session.add(knowledge)
                session.commit()
                logger.info(f"Updated knowledge base: {knowledge.id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update knowledge base: {e}")
            return False
    
    def learn_from_medical_records(self, patient_id: str = None) -> bool:
        """Learn from medical records in the shared database"""
        try:
            with get_db_session() as session:
                query = session.query(MedicalRecord)
                if patient_id:
                    query = query.filter(MedicalRecord.patient_id == patient_id)
                
                records = query.limit(100).all()  # Limit to prevent memory issues
                
                for record in records:
                    # Extract medical insights from the record
                    medical_text = f"{record.diagnosis} {record.treatment_plan} {record.notes}"
                    
                    # Add to vector store for future reference
                    self.add_medical_knowledge(
                        documents=[medical_text],
                        metadata=[{
                            'source': 'medical_record',
                            'patient_id': str(record.patient_id),
                            'record_id': str(record.id),
                            'date': record.created_at.isoformat() if record.created_at else None
                        }]
                    )
                
                logger.info(f"Learned from {len(records)} medical records")
                return True
                
        except Exception as e:
            logger.error(f"Failed to learn from medical records: {e}")
            return False
    
    def process_and_learn(self, user_input: str, patient_id: str = None, doctor_id: str = None) -> Dict[str, Any]:
        """Process user input and learn from the interaction"""
        try:
            # Get patient context if available
            patient_context = ""
            if patient_id:
                patient_data = self.get_patient_from_db(patient_id)
                if patient_data:
                    patient_context = self.get_patient_context(patient_data)
            
            # Process the input (analyze symptoms or generate response)
            if "symptom" in user_input.lower() or "pain" in user_input.lower():
                response = self.analyze_patient_symptoms(user_input, patient_context)
            else:
                response = self.generate_general_response(user_input, patient_context)
            
            # Store the interaction in database
            interaction_data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'interaction_type': 'symptom_analysis' if 'symptom' in user_input.lower() else 'general_query',
                'user_input': user_input,
                'llm_response': json.dumps(response),
                'context': {'patient_context': patient_context},
                'confidence_score': response.get('confidence', 0.5)
            }
            
            self.store_interaction(interaction_data)
            
            # Extract learning insights
            learning_insights = self.extract_learning_insights(user_input, response)
            
            # Update knowledge base with new insights
            if learning_insights:
                self.update_knowledge_base(learning_insights)
            
            return {
                'response': response,
                'patient_context': patient_context,
                'learning_applied': bool(learning_insights),
                'interaction_stored': True
            }
            
        except Exception as e:
            logger.error(f"Failed to process and learn: {e}")
            return {
                'error': 'Failed to process request',
                'details': str(e)
            }
    
    def extract_learning_insights(self, user_input: str, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract learning insights from user input and AI response"""
        try:
            # Simple keyword extraction for learning
            medical_keywords = []
            if 'diagnosis' in response:
                medical_keywords.append('diagnosis')
            if 'treatment' in response:
                medical_keywords.append('treatment')
            if 'symptom' in user_input.lower():
                medical_keywords.append('symptom_analysis')
            
            if not medical_keywords:
                return None
            
            return {
                'category': 'ai_learning',
                'title': f"Learning from {user_input[:50]}...",
                'content': f"User query: {user_input}\nAI response: {json.dumps(response, indent=2)}",
                'source': 'user_interaction',
                'version': '1.0',
                'keywords': medical_keywords,
                'related_topics': ['medical_ai', 'patient_care', 'diagnostic_support']
            }
            
        except Exception as e:
            logger.error(f"Failed to extract learning insights: {e}")
            return None
    
    def generate_general_response(self, user_input: str, patient_context: str = "") -> Dict[str, Any]:
        """Generate general medical response"""
        try:
            system_prompt = """You are an AI medical assistant. Provide helpful, accurate medical information.
            Always emphasize that this is for educational purposes and not a substitute for professional medical advice."""
            
            user_prompt = f"""
            Patient Context:
            {patient_context}
            
            User Query:
            {user_input}
            
            Please provide a helpful response.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "response": response.content,
                "timestamp": datetime.now().isoformat(),
                "confidence": "medium",
                "type": "general_response"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate general response: {e}")
            return {
                "error": "Failed to generate response",
                "details": str(e)
            }
    
    def analyze_patient_symptoms(self, symptoms: str, patient_context: str = "") -> Dict[str, Any]:
        """Analyze patient symptoms and provide diagnostic insights"""
        try:
            system_prompt = """You are an AI medical assistant. Analyze the patient's symptoms and provide:
            1. Possible differential diagnoses (ranked by likelihood)
            2. Recommended diagnostic tests
            3. Urgency level (low, medium, high, emergency)
            4. Red flag symptoms to watch for
            5. General recommendations
            
            Always emphasize that this is for educational purposes and not a substitute for professional medical advice."""
            
            user_prompt = f"""
            Patient Context:
            {patient_context}
            
            Symptoms:
            {symptoms}
            
            Please provide a structured analysis in JSON format.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                analysis = {
                    "analysis": response.content,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": "medium"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze symptoms: {e}")
            return {
                "error": "Failed to analyze symptoms",
                "details": str(e)
            }
    
    def generate_treatment_plan(self, diagnosis: str, patient_context: str = "") -> Dict[str, Any]:
        """Generate treatment plan based on diagnosis"""
        try:
            system_prompt = """You are an AI medical assistant. Generate a comprehensive treatment plan including:
            1. Primary treatment recommendations
            2. Alternative treatment options
            3. Medication considerations
            4. Lifestyle modifications
            5. Follow-up schedule
            6. Monitoring parameters
            
            Always consider patient context and emphasize safety."""
            
            user_prompt = f"""
            Patient Context:
            {patient_context}
            
            Diagnosis:
            {diagnosis}
            
            Please provide a structured treatment plan in JSON format.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                plan = json.loads(response.content)
            except json.JSONDecodeError:
                plan = {
                    "treatment_plan": response.content,
                    "timestamp": datetime.now().isoformat()
                }
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate treatment plan: {e}")
            return {
                "error": "Failed to generate treatment plan",
                "details": str(e)
            }
    
    def provide_medical_education(self, topic: str, patient_level: str = "basic") -> Dict[str, Any]:
        """Provide patient education on medical topics"""
        try:
            system_prompt = f"""You are an AI medical educator. Provide {patient_level} level education on medical topics.
            Include:
            1. Simple explanation of the topic
            2. Key points to remember
            3. When to seek medical help
            4. Prevention tips
            5. Questions for their doctor
            
            Use clear, simple language appropriate for {patient_level} understanding."""
            
            user_prompt = f"Please provide education on: {topic}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "topic": topic,
                "level": patient_level,
                "content": response.content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to provide medical education: {e}")
            return {
                "error": "Failed to provide medical education",
                "details": str(e)
            }
    
    def check_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """Check for potential drug interactions"""
        try:
            system_prompt = """You are an AI pharmacist. Analyze the provided medications for:
            1. Potential drug interactions
            2. Contraindications
            3. Side effect warnings
            4. Dosage considerations
            5. Recommendations
            
            Always emphasize consulting with a healthcare provider."""
            
            user_prompt = f"Please analyze these medications for interactions: {', '.join(medications)}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "medications": medications,
                "analysis": response.content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check drug interactions: {e}")
            return {
                "error": "Failed to check drug interactions",
                "details": str(e)
            }
    
    def generate_medical_summary(self, patient_data: Dict[str, Any], visit_data: Dict[str, Any]) -> str:
        """Generate medical summary for patient records"""
        try:
            system_prompt = """You are an AI medical assistant. Generate a concise, professional medical summary including:
            1. Chief complaint
            2. Key findings
            3. Diagnosis
            4. Treatment plan
            5. Follow-up recommendations
            
            Use medical terminology appropriate for healthcare professionals."""
            
            user_prompt = f"""
            Patient Data:
            {json.dumps(patient_data, indent=2)}
            
            Visit Data:
            {json.dumps(visit_data, indent=2)}
            
            Please generate a professional medical summary.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate medical summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def search_medical_knowledge(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search medical knowledge base using vector similarity"""
        try:
            if not self.vector_store:
                return []
            
            # Search vector store
            docs = self.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search medical knowledge: {e}")
            return []
    
    def chat_with_patient(self, message: str, patient_context: str = "", conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with patient for medical guidance"""
        try:
            system_prompt = """You are an AI medical assistant. Provide helpful, accurate medical information while:
            1. Always emphasizing the importance of consulting healthcare professionals
            2. Never making definitive diagnoses
            3. Providing general information and guidance
            4. Identifying when immediate medical attention is needed
            5. Being empathetic and supportive
            
            Use the patient context to provide personalized responses."""
            
            # Build conversation context
            context = f"Patient Context: {patient_context}\n\n" if patient_context else ""
            
            if conversation_history:
                context += "Recent conversation:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages
                    context += f"{msg['role']}: {msg['content']}\n"
                context += "\n"
            
            user_prompt = f"{context}Patient: {message}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "response": response.content,
                "timestamp": datetime.now().isoformat(),
                "confidence": "medium",
                "disclaimer": "This information is for educational purposes only. Please consult a healthcare professional for medical advice."
            }
            
        except Exception as e:
            logger.error(f"Failed to chat with patient: {e}")
            return {
                "error": "Failed to process message",
                "details": str(e)
            }
    
    def get_healthcare_insights(self, data: Dict[str, Any], insight_type: str = "general") -> Dict[str, Any]:
        """Generate healthcare insights from patient data"""
        try:
            system_prompt = """You are an AI healthcare analyst. Analyze the provided data and generate insights about:
            1. Health trends
            2. Risk factors
            3. Improvement opportunities
            4. Preventive measures
            5. Recommendations
            
            Focus on actionable insights for healthcare providers."""
            
            user_prompt = f"""
            Insight Type: {insight_type}
            
            Data:
            {json.dumps(data, indent=2)}
            
            Please provide healthcare insights in JSON format.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                insights = json.loads(response.content)
            except json.JSONDecodeError:
                insights = {
                    "insights": response.content,
                    "type": insight_type,
                    "timestamp": datetime.now().isoformat()
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate healthcare insights: {e}")
            return {
                "error": "Failed to generate insights",
                "details": str(e)
            }

# Convenience function to create LLM instance
def create_healthcare_llm(openai_api_key: str = None) -> HealthcareLLM:
    """Create and return a HealthcareLLM instance"""
    return HealthcareLLM(openai_api_key)
