import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from 'react-query';
import { aiAPI } from '../services/api';
import {
  PaperAirplaneIcon,
  CpuChipIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  StarIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

const AIAgent = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [processingHistory, setProcessingHistory] = useState([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentFeedback, setCurrentFeedback] = useState({});
  const [learningNotes, setLearningNotes] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // AI Learning mutation
  const learningMutation = useMutation({
    mutationFn: aiAPI.learnAndUpdate,
    onSuccess: (data) => {
      console.log('Learning successful:', data);
      setShowFeedback(false);
      setCurrentFeedback({});
      setLearningNotes('');
      // Show success message
      const successMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `Thank you for your feedback! I've learned from this interaction and updated my knowledge base. This will help me provide better responses in the future.`,
        timestamp: new Date(),
        workflow_type: 'learning_update'
      };
      setMessages(prev => [...prev, successMessage]);
    },
    onError: (error) => {
      console.error('Learning failed:', error);
      // Show error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error while learning from your feedback. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      console.log('Sending request to AI service...');
      console.log('Request data:', { session_id: `session_${Date.now()}`, note: inputMessage });
      
      // Try to process as medical note first
      const response = await aiAPI.processNote({
        session_id: `session_${Date.now()}`,
        note: inputMessage
      });
      
      console.log('AI service response:', response);

      // Validate response structure
      if (!response || typeof response !== 'object') {
        throw new Error('Invalid response from AI service');
      }

      // Extract the patient report content safely
      const reportContent = response.patient_report || response;
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: reportContent,
        timestamp: new Date(),
        processing_time: response.processing_time || 0,
        workflow_type: response.workflow_type || 'unknown'
      };

      setMessages(prev => [...prev, aiMessage]);

      // Add to processing history
      setProcessingHistory(prev => [{
        id: response.session_id || `session_${Date.now()}`,
        input: inputMessage,
        output: reportContent,
        timestamp: new Date(),
        processing_time: response.processing_time || 0,
        workflow_type: response.workflow_type || 'unknown'
      }, ...prev.slice(0, 9)]); // Keep last 10 items

    } catch (error) {
      console.error('AI processing error:', error);

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFeedback = (messageId, feedbackScore) => {
    const message = messages.find(m => m.id === messageId);
    if (message && message.type === 'ai') {
      setCurrentFeedback({
        messageId,
        feedbackScore,
        userInput: messages.find(m => m.type === 'user' && m.id < messageId)?.content || '',
        aiResponse: message.content
      });
      setShowFeedback(true);
    }
  };

  const submitFeedback = () => {
    if (!currentFeedback.messageId || !currentFeedback.userInput || !currentFeedback.aiResponse) {
      return;
    }

    const learningData = {
      interaction_type: 'user_feedback',
      user_input: currentFeedback.userInput,
      ai_response: typeof currentFeedback.aiResponse === 'string' 
        ? currentFeedback.aiResponse 
        : JSON.stringify(currentFeedback.aiResponse),
      feedback_score: currentFeedback.feedbackScore,
      medical_context: {
        message_type: 'ai_response',
        workflow_type: messages.find(m => m.id === currentFeedback.messageId)?.workflow_type || 'unknown'
      },
      learning_notes: learningNotes
    };

    learningMutation.mutate(learningData);
  };

  const clearChat = () => {
    setMessages([]);
  };

  const examplePrompts = [
    "Patient presents with chest pain and shortness of breath lasting 2 hours. Associated with diaphoresis and nausea.",
    "65-year-old male with hypertension presents with sudden onset severe headache and confusion.",
    "Patient reports persistent cough for 3 weeks, productive of green sputum, accompanied by fever and fatigue.",
    "Female patient, 45 years old, complains of joint pain and stiffness in multiple joints, worse in the morning."
  ];

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <CpuChipIcon className="h-8 w-8 text-blue-600 mr-3" />
          AI Medical Assistant
        </h1>
        <p className="text-gray-600 mt-1">
          Interact with our AI-powered medical assistant for patient note analysis and insights
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('chat')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'chat'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ChatBubbleLeftRightIcon className="h-5 w-5 inline mr-2" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ClockIcon className="h-5 w-5 inline mr-2" />
            Processing History
          </button>
        </nav>
      </div>

      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Chat Header */}
              <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Medical AI Assistant</h3>
                <button
                  onClick={clearChat}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear Chat
                </button>
              </div>

              {/* Messages */}
              <div className="h-96 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 mt-8">
                    <CpuChipIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Start a conversation</p>
                    <p className="text-sm">Enter a patient note or medical query below</p>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.type === 'error'
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {message.type === 'ai' && (
                        <div className="mb-2">
                          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                            <div className="flex items-center">
                              {message.workflow_type === 'simple_mock' ? (
                                <ExclamationTriangleIcon className="h-3 w-3 mr-1 text-yellow-500" />
                              ) : (
                                <CheckCircleIcon className="h-3 w-3 mr-1 text-green-500" />
                              )}
                              {message.workflow_type} • {message.processing_time?.toFixed(2)}s
                            </div>
                            <div className="flex items-center space-x-1">
                              <span className="text-xs text-gray-500">Rate this response:</span>
                              <div className="flex space-x-1">
                                {[1, 2, 3, 4, 5].map((score) => (
                                  <button
                                    key={score}
                                    onClick={() => handleFeedback(message.id, score)}
                                    className="text-yellow-400 hover:text-yellow-600 transition-colors"
                                    title={`Rate ${score} stars`}
                                  >
                                    <StarIcon className="h-3 w-3" />
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {message.type === 'ai' && message.content && typeof message.content === 'object' ? (
                        <div className="space-y-2">
                          {message.content.patient_summary && (
                            <div>
                              <strong>Summary:</strong> {message.content.patient_summary}
                            </div>
                          )}

                          {message.content.key_points && Array.isArray(message.content.key_points) && message.content.key_points.length > 0 && (
                            <div>
                              <strong>Key Points:</strong>
                              <ul className="list-disc list-inside mt-1 ml-2">
                                {message.content.key_points.map((point, index) => (
                                  <li key={index} className="text-sm">{point}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {message.content.recommendations && Array.isArray(message.content.recommendations) && message.content.recommendations.length > 0 && (
                            <div>
                              <strong>Recommendations:</strong>
                              <ul className="list-disc list-inside mt-1 ml-2">
                                {message.content.recommendations.map((rec, index) => (
                                  <li key={index} className="text-sm">{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {message.content.questions_for_doctor && Array.isArray(message.content.questions_for_doctor) && message.content.questions_for_doctor.length > 0 && (
                            <div>
                              <strong>Questions for Doctor:</strong>
                              <ul className="list-disc list-inside mt-1 ml-2">
                                {message.content.questions_for_doctor.map((question, index) => (
                                  <li key={index} className="text-sm">{question}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {message.content.follow_up_plan && (
                            <div>
                              <strong>Follow-up Plan:</strong> {message.content.follow_up_plan}
                            </div>
                          )}

                          {message.content.risk_level && (
                            <div className="mt-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                message.content.risk_level === 'high'
                                  ? 'bg-red-100 text-red-800'
                                  : message.content.risk_level === 'medium'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                Risk: {message.content.risk_level.toUpperCase()}
                              </span>
                            </div>
                          )}

                          {message.content.urgency && (
                            <div className="mt-2">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                message.content.urgency === 'emergency'
                                  ? 'bg-red-100 text-red-800'
                                  : message.content.urgency === 'urgent'
                                  ? 'bg-orange-100 text-orange-800'
                                  : message.content.urgency === 'soon'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                Urgency: {message.content.urgency.toUpperCase()}
                              </span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="whitespace-pre-wrap">{typeof message.content === 'string' ? message.content : JSON.stringify(message.content, null, 2)}</div>
                      )}

                      <div className="text-xs mt-1 opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span className="text-sm text-gray-600">AI is analyzing...</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="px-4 py-3 border-t border-gray-200">
                <div className="flex space-x-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter patient note or medical query..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows="2"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <PaperAirplaneIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Example Prompts */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                <DocumentTextIcon className="h-4 w-4 mr-2" />
                Example Patient Notes
              </h4>
              <div className="space-y-2">
                {examplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(prompt)}
                    className="w-full text-left p-2 text-xs bg-gray-50 hover:bg-gray-100 rounded border text-gray-700 hover:text-gray-900 transition-colors"
                  >
                    {prompt.length > 60 ? `${prompt.substring(0, 60)}...` : prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* AI Capabilities */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">AI Capabilities</h4>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• Extract medical entities from notes</li>
                <li>• Validate medical terminology</li>
                <li>• Generate patient-friendly reports</li>
                <li>• Assess risk factors</li>
                <li>• Suggest treatment approaches</li>
                <li>• Provide ICD-10/SNOMED codes</li>
              </ul>
            </div>

            {/* AI Learning */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-3 flex items-center">
                <LightBulbIcon className="h-4 w-4 mr-2" />
                AI Learning System
              </h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Rate AI responses (1-5 stars)</li>
                <li>• Provide feedback for improvement</li>
                <li>• AI learns from user interactions</li>
                <li>• Updates medical knowledge base</li>
                <li>• Improves future responses</li>
                <li>• Tracks learning patterns</li>
              </ul>
            </div>

            {/* Disclaimer */}
            <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
              <div className="flex">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-yellow-800">Medical Disclaimer</h4>
                  <p className="text-xs text-yellow-700 mt-1">
                    AI-generated information should be reviewed by healthcare professionals.
                    This tool is for educational purposes only.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-4 py-3 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Processing History</h3>
            <p className="text-sm text-gray-600">Recent AI processing sessions</p>
          </div>

          <div className="divide-y divide-gray-200">
            {processingHistory.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <ClockIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No processing history yet</p>
                <p className="text-sm">Start a conversation to see your history here</p>
              </div>
            ) : (
              processingHistory.map((item) => (
                <div key={item.id} className="px-4 py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          Session {item.id}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.workflow_type === 'simple_mock'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {item.workflow_type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {item.processing_time?.toFixed(2)}s
                        </span>
                      </div>

                      <div className="text-sm text-gray-600 mb-2">
                        <strong>Input:</strong> {item.input.length > 100 ? `${item.input.substring(0, 100)}...` : item.input}
                      </div>

                      <div className="text-sm text-gray-600">
                        <strong>Summary:</strong> {item.output?.patient_summary || 'Analysis completed'}
                      </div>
                    </div>

                    <div className="text-xs text-gray-500 ml-4">
                      {item.timestamp.toLocaleString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <LightBulbIcon className="h-5 w-5 text-blue-600 mr-2" />
                Help Me Learn
              </h3>
              <button
                onClick={() => setShowFeedback(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircleIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Rating: {currentFeedback.feedbackScore}/5 stars
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((score) => (
                    <button
                      key={score}
                      onClick={() => setCurrentFeedback(prev => ({ ...prev, feedbackScore: score }))}
                      className={`text-2xl transition-colors ${
                        score <= currentFeedback.feedbackScore 
                          ? 'text-yellow-400' 
                          : 'text-gray-300'
                      }`}
                    >
                      <StarIcon className="h-5 w-5" />
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes (Optional)
                </label>
                <textarea
                  value={learningNotes}
                  onChange={(e) => setLearningNotes(e.target.value)}
                  placeholder="What could I improve? Any specific medical insights?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="3"
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowFeedback(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
                <button
                  onClick={submitFeedback}
                  disabled={learningMutation.isLoading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {learningMutation.isLoading ? 'Learning...' : 'Submit Feedback'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAgent;