import React, { useState, useRef } from 'react';
import { aiAPI } from '../services/api';
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  CpuChipIcon,
  BeakerIcon,
  ChartBarIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const AILearning = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedContent, setUploadedContent] = useState([]);
  const [learningStats, setLearningStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  // File upload states
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileMetadata, setFileMetadata] = useState({
    content_type: 'medical_document',
    category: 'general',
    tags: '',
    uploader: 'user'
  });

  // Text upload states
  const [textContent, setTextContent] = useState('');
  const [textTitle, setTextTitle] = useState('');
  const [textMetadata, setTextMetadata] = useState({
    content_type: 'medical_content',
    category: 'general',
    tags: ''
  });

  const fileInputRef = useRef(null);

  // Load uploaded content list
  const loadUploadedContent = async () => {
    try {
      const response = await aiAPI.getUploadedContent();
      setUploadedContent(response.items || []);
    } catch (error) {
      console.error('Error loading uploaded content:', error);
    }
  };

  // Load learning statistics
  const loadLearningStats = async () => {
    try {
      const response = await aiAPI.getLearningStatistics();
      setLearningStats(response);
    } catch (error) {
      console.error('Error loading learning stats:', error);
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Upload file for AI learning
  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setIsLoading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('filename', selectedFile.name);
      formData.append('content_type', fileMetadata.content_type);
      formData.append('category', fileMetadata.category);
      formData.append('tags', fileMetadata.tags);
      formData.append('uploader', fileMetadata.uploader);

      // Use fetch directly for file upload
      const response = await fetch('/api/ai/upload-file', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus({ type: 'success', message: 'File uploaded and processed successfully!' });
        setSelectedFile(null);
        fileInputRef.current.value = '';
        loadUploadedContent(); // Refresh the list
        loadLearningStats(); // Refresh stats
      } else {
        setUploadStatus({ type: 'error', message: result.detail || 'Upload failed' });
      }
    } catch (error) {
      console.error('File upload error:', error);
      setUploadStatus({ type: 'error', message: 'Network error during upload' });
    } finally {
      setIsLoading(false);
    }
  };

  // Upload text content for AI learning
  const handleTextUpload = async () => {
    if (!textContent.trim() || !textTitle.trim()) {
      setUploadStatus({ type: 'error', message: 'Please provide both title and content' });
      return;
    }

    setIsLoading(true);
    setUploadStatus(null);

    try {
      const uploadData = {
        content: textContent,
        title: textTitle,
        metadata: {
          content_type: textMetadata.content_type,
          category: textMetadata.category,
          tags: textMetadata.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        }
      };

      const response = await fetch('/api/ai/upload-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(uploadData)
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus({ type: 'success', message: 'Text content uploaded and processed successfully!' });
        setTextContent('');
        setTextTitle('');
        loadUploadedContent(); // Refresh the list
        loadLearningStats(); // Refresh stats
      } else {
        setUploadStatus({ type: 'error', message: result.detail || 'Upload failed' });
      }
    } catch (error) {
      console.error('Text upload error:', error);
      setUploadStatus({ type: 'error', message: 'Network error during upload' });
    } finally {
      setIsLoading(false);
    }
  };

  // Load demo data
  const handleLoadDemoData = async () => {
    setIsLoading(true);
    setUploadStatus(null);

    try {
      const response = await fetch('/api/ai/load-demo-data', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus({
          type: 'success',
          message: `Demo data loaded successfully! ${result.result?.successful_loads || 0} documents processed.`
        });
        loadLearningStats(); // Refresh stats
      } else {
        setUploadStatus({ type: 'error', message: result.detail || 'Demo data loading failed' });
      }
    } catch (error) {
      console.error('Demo data loading error:', error);
      setUploadStatus({ type: 'error', message: 'Network error during demo data loading' });
    } finally {
      setIsLoading(false);
    }
  };

  // Load data on component mount
  React.useEffect(() => {
    loadUploadedContent();
    loadLearningStats();
  }, []);

  const tabs = [
    { id: 'upload', name: 'Upload Content', icon: CloudArrowUpIcon },
    { id: 'content', name: 'Uploaded Content', icon: DocumentTextIcon },
    { id: 'stats', name: 'Learning Stats', icon: ChartBarIcon }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <CpuChipIcon className="h-8 w-8 mr-3 text-blue-600" />
          AI Learning Center
        </h1>
        <p className="mt-2 text-gray-600">
          Upload medical content and train the AI agent to improve its medical knowledge and responses.
        </p>
      </div>

      {/* Status Messages */}
      {uploadStatus && (
        <div className={`mb-6 p-4 rounded-md ${
          uploadStatus.type === 'success'
            ? 'bg-green-50 border border-green-200'
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex">
            {uploadStatus.type === 'success' ? (
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
            ) : (
              <XCircleIcon className="h-5 w-5 text-red-400" />
            )}
            <div className="ml-3">
              <p className={`text-sm font-medium ${
                uploadStatus.type === 'success' ? 'text-green-800' : 'text-red-800'
              }`}>
                {uploadStatus.message}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <div className="space-y-8">
          {/* File Upload Section */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Medical Files</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select File (PDF, DOCX, TXT, MD, HTML)
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.md,.html"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content Type
                  </label>
                  <select
                    value={fileMetadata.content_type}
                    onChange={(e) => setFileMetadata({...fileMetadata, content_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="medical_document">Medical Document</option>
                    <option value="clinical_guideline">Clinical Guideline</option>
                    <option value="research_paper">Research Paper</option>
                    <option value="drug_database">Drug Database</option>
                    <option value="case_study">Case Study</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={fileMetadata.category}
                    onChange={(e) => setFileMetadata({...fileMetadata, category: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="general">General</option>
                    <option value="cardiology">Cardiology</option>
                    <option value="pulmonology">Pulmonology</option>
                    <option value="neurology">Neurology</option>
                    <option value="gastroenterology">Gastroenterology</option>
                    <option value="pediatrics">Pediatrics</option>
                    <option value="psychiatry">Psychiatry</option>
                    <option value="pharmacology">Pharmacology</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={fileMetadata.tags}
                  onChange={(e) => setFileMetadata({...fileMetadata, tags: e.target.value})}
                  placeholder="e.g., cardiology, hypertension, diagnosis"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || isLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                    Upload File
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Text Upload Section */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Text Content</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={textTitle}
                  onChange={(e) => setTextTitle(e.target.value)}
                  placeholder="Enter a title for your content"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Medical Content
                </label>
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Paste or type medical content here..."
                  rows={8}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content Type
                  </label>
                  <select
                    value={textMetadata.content_type}
                    onChange={(e) => setTextMetadata({...textMetadata, content_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="medical_content">Medical Content</option>
                    <option value="clinical_note">Clinical Note</option>
                    <option value="educational_material">Educational Material</option>
                    <option value="protocol">Protocol</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={textMetadata.category}
                    onChange={(e) => setTextMetadata({...textMetadata, category: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="general">General</option>
                    <option value="cardiology">Cardiology</option>
                    <option value="pulmonology">Pulmonology</option>
                    <option value="neurology">Neurology</option>
                    <option value="gastroenterology">Gastroenterology</option>
                    <option value="pediatrics">Pediatrics</option>
                    <option value="psychiatry">Psychiatry</option>
                    <option value="pharmacology">Pharmacology</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={textMetadata.tags}
                  onChange={(e) => setTextMetadata({...textMetadata, tags: e.target.value})}
                  placeholder="e.g., cardiology, hypertension, diagnosis"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleTextUpload}
                disabled={!textContent.trim() || !textTitle.trim() || isLoading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <DocumentTextIcon className="h-5 w-5 mr-2" />
                    Upload Text
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Demo Data Section */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Load Demo Medical Data</h2>
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <BeakerIcon className="h-5 w-5 text-blue-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      Demo Medical Knowledge Base
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>Load comprehensive demo data including:</p>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        <li>Cardiology assessment guidelines</li>
                        <li>Respiratory condition protocols</li>
                        <li>Neurological examination procedures</li>
                        <li>Gastrointestinal disorder management</li>
                        <li>Pediatric vital signs and conditions</li>
                        <li>Mental health assessment frameworks</li>
                        <li>Geriatric care considerations</li>
                        <li>Medication interaction guidelines</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleLoadDemoData}
                disabled={isLoading}
                className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading Demo Data...
                  </>
                ) : (
                  <>
                    <BeakerIcon className="h-5 w-5 mr-2" />
                    Load Demo Medical Data
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'content' && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Uploaded Content</h2>
            <p className="text-gray-600">Medical content uploaded for AI learning</p>
          </div>

          <div className="divide-y divide-gray-200">
            {uploadedContent.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No content uploaded yet</p>
                <p className="text-sm">Upload files or text content to train the AI</p>
              </div>
            ) : (
              uploadedContent.map((item) => (
                <div key={item.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-sm font-medium text-gray-900">
                          {item.filename}
                        </h3>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.status === 'processed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {item.status}
                        </span>
                      </div>

                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span>{item.content_type}</span>
                        <span>•</span>
                        <span>{new Date(item.upload_date).toLocaleDateString()}</span>
                        {item.insights && (
                          <>
                            <span>•</span>
                            <span>{item.insights.medical_terms} medical terms</span>
                            <span>•</span>
                            <span>Quality: {(item.insights.quality_score * 100).toFixed(0)}%</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button className="text-gray-400 hover:text-red-600">
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="space-y-6">
          {learningStats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {learningStats.total_documents_processed}
                    </h3>
                    <p className="text-sm text-gray-500">Documents Processed</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {learningStats.total_medical_terms_learned}
                    </h3>
                    <p className="text-sm text-gray-500">Medical Terms Learned</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CpuChipIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {(learningStats.model_accuracy * 100).toFixed(1)}%
                    </h3>
                    <p className="text-sm text-gray-500">Model Accuracy</p>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BeakerIcon className="h-8 w-8 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {learningStats.knowledge_base_size}
                    </h3>
                    <p className="text-sm text-gray-500">Knowledge Base Size</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg p-8 text-center">
              <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">Loading learning statistics...</p>
            </div>
          )}

          {learningStats && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Medical Categories Covered</h3>
              <div className="flex flex-wrap gap-2">
                {learningStats.categories_covered.map((category) => (
                  <span
                    key={category}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {category}
                  </span>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Last Training Update</h4>
                    <p className="text-sm text-gray-500">
                      {new Date(learningStats.last_training_date).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">System Status</p>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Active Learning
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AILearning;