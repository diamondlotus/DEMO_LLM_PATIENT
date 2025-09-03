import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import Appointments from './pages/Appointments';
import Doctors from './pages/Doctors';
import AIAgent from './pages/AIAgent';
import AILearning from './pages/AILearning';
import Users from './pages/Users';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} 
      />
      <Route 
        path="/" 
        element={<Navigate to="/dashboard" replace />} 
      />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/patients" 
        element={
          <ProtectedRoute>
            <Layout>
              <Patients />
            </Layout>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/appointments" 
        element={
          <ProtectedRoute>
            <Layout>
              <Appointments />
            </Layout>
          </ProtectedRoute>
        } 
      />
      <Route
        path="/doctors"
        element={
          <ProtectedRoute>
            <Layout>
              <Doctors />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ai-agent"
        element={
          <ProtectedRoute>
            <Layout>
              <AIAgent />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ai-learning"
        element={
          <ProtectedRoute>
            <Layout>
              <AILearning />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <Layout>
              <Users />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <Layout>
              <Settings />
            </Layout>
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <AppRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
