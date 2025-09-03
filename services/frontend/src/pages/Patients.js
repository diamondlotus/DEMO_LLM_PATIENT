import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { patientsAPI } from '../services/api';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// Helper function to format error messages
const getErrorMessage = (error) => {
  const errorData = error.response?.data;
  
  if (!errorData) {
    return 'An unexpected error occurred';
  }
  
  // Handle validation errors (array of error objects)
  if (Array.isArray(errorData.detail)) {
    return errorData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
  }
  
  // Handle simple error messages
  if (typeof errorData.detail === 'string') {
    return errorData.detail;
  }
  
  // Handle other error formats
  if (errorData.message) {
    return errorData.message;
  }
  
  return 'An error occurred';
};

const Patients = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPatient, setEditingPatient] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  // Fetch patients
  const { data: patientsResponse, isLoading } = useQuery(
    ['patients', searchTerm, filterStatus],
    () => patientsAPI.getAll({ search: searchTerm, status: filterStatus })
  );
  
  // Extract patients array from response
  const patients = patientsResponse?.data || [];

  // Create patient mutation
  const createPatientMutation = useMutation(patientsAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('patients');
      toast.success('Patient created successfully!');
      handleCloseModal();
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  // Update patient mutation
  const updatePatientMutation = useMutation(
    ({ id, data }) => patientsAPI.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('patients');
        toast.success('Patient updated successfully!');
        handleCloseModal();
      },
      onError: (error) => {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
      },
    }
  );

  // Delete patient mutation
  const deletePatientMutation = useMutation(patientsAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('patients');
      toast.success('Patient deleted successfully!');
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  const handleOpenModal = (patient = null) => {
    setEditingPatient(patient);
    if (patient) {
      reset(patient);
    } else {
      reset();
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingPatient(null);
    reset();
  };

  const onSubmit = (data) => {
    if (editingPatient) {
      updatePatientMutation.mutate({ id: editingPatient.id, data });
    } else {
      createPatientMutation.mutate(data);
    }
  };

  const handleDelete = (patientId) => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      deletePatientMutation.mutate(patientId);
    }
  };

  const PatientModal = () => (
    <div className={`fixed inset-0 z-50 overflow-y-auto ${isModalOpen ? 'block' : 'hidden'}`}>
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleCloseModal}></div>
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    {editingPatient ? 'Edit Patient' : 'Add New Patient'}
                  </h3>
                  
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">First Name</label>
                      <input
                        type="text"
                        className={`input mt-1 ${errors.first_name ? 'input-error' : ''}`}
                        {...register('first_name', { required: 'First name is required' })}
                      />
                      {errors.first_name && (
                        <p className="mt-1 text-sm text-danger-600">{errors.first_name.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Last Name</label>
                      <input
                        type="text"
                        className={`input mt-1 ${errors.last_name ? 'input-error' : ''}`}
                        {...register('last_name', { required: 'Last name is required' })}
                      />
                      {errors.last_name && (
                        <p className="mt-1 text-sm text-danger-600">{errors.last_name.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Email</label>
                      <input
                        type="email"
                        className={`input mt-1 ${errors.email ? 'input-error' : ''}`}
                        {...register('email', {
                          required: 'Email is required',
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address',
                          },
                        })}
                      />
                      {errors.email && (
                        <p className="mt-1 text-sm text-danger-600">{errors.email.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Phone</label>
                      <input
                        type="tel"
                        className={`input mt-1 ${errors.phone ? 'input-error' : ''}`}
                        {...register('phone', { 
                          required: 'Phone number is required',
                          minLength: { value: 10, message: 'Phone number must be at least 10 characters' },
                          maxLength: { value: 20, message: 'Phone number must be at most 20 characters' }
                        })}
                        placeholder="e.g., +1-555-123-4567"
                      />
                      {errors.phone && (
                        <p className="mt-1 text-sm text-danger-600">{errors.phone.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
                      <input
                        type="date"
                        className={`input mt-1 ${errors.date_of_birth ? 'input-error' : ''}`}
                        {...register('date_of_birth', { required: 'Date of birth is required' })}
                      />
                      {errors.date_of_birth && (
                        <p className="mt-1 text-sm text-danger-600">{errors.date_of_birth.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Gender</label>
                      <select
                        className={`input mt-1 ${errors.gender ? 'input-error' : ''}`}
                        {...register('gender', { required: 'Gender is required' })}
                      >
                        <option value="">Select gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                      {errors.gender && (
                        <p className="mt-1 text-sm text-danger-600">{errors.gender.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Address</label>
                      <textarea
                        rows={3}
                        className={`input mt-1 ${errors.address ? 'input-error' : ''}`}
                        {...register('address', {
                          required: 'Address is required',
                          minLength: { value: 10, message: 'Address must be at least 10 characters' },
                          maxLength: { value: 200, message: 'Address must be at most 200 characters' }
                        })}
                        placeholder="Full address including street, city, state, and zip code"
                      />
                      {errors.address && (
                        <p className="mt-1 text-sm text-danger-600">{errors.address.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Emergency Contact</label>
                      <input
                        type="text"
                        className={`input mt-1 ${errors.emergency_contact ? 'input-error' : ''}`}
                        {...register('emergency_contact', {
                          required: 'Emergency contact is required',
                          minLength: { value: 5, message: 'Emergency contact must be at least 5 characters' },
                          maxLength: { value: 100, message: 'Emergency contact must be at most 100 characters' }
                        })}
                        placeholder="Name and phone number of emergency contact"
                      />
                      {errors.emergency_contact && (
                        <p className="mt-1 text-sm text-danger-600">{errors.emergency_contact.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Medical History</label>
                      <textarea
                        rows={3}
                        className={`input mt-1 ${errors.medical_history ? 'input-error' : ''}`}
                        {...register('medical_history')}
                        placeholder="Any relevant medical history..."
                      />
                      {errors.medical_history && (
                        <p className="mt-1 text-sm text-danger-600">{errors.medical_history.message}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={createPatientMutation.isLoading || updatePatientMutation.isLoading}
                className="btn-primary sm:ml-3 sm:w-auto"
              >
                {createPatientMutation.isLoading || updatePatientMutation.isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {editingPatient ? 'Updating...' : 'Creating...'}
                  </div>
                ) : (
                  editingPatient ? 'Update Patient' : 'Create Patient'
                )}
              </button>
              <button
                type="button"
                onClick={handleCloseModal}
                className="btn-outline sm:mt-0 sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your patient records and information.
          </p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Patient
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search patients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input"
          >
            <option value="all">All Patients</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Patients table */}
      <div className="card">
        <div className="card-body p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="overflow-hidden">
              <table className="table">
                <thead className="table-header">
                  <tr>
                    <th className="table-header-cell">Patient</th>
                    <th className="table-header-cell">Contact</th>
                    <th className="table-header-cell">Date of Birth</th>
                    <th className="table-header-cell">Gender</th>
                    <th className="table-header-cell">Status</th>
                    <th className="table-header-cell">Actions</th>
                  </tr>
                </thead>
                <tbody className="table-body">
                  {patients?.map((patient) => (
                    <tr key={patient.id} className="table-row">
                      <td className="table-cell">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                            <span className="text-sm font-medium text-primary-600">
                              {patient.first_name?.charAt(0)?.toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {patient.first_name} {patient.last_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {patient.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div>
                          <div className="text-sm text-gray-900">{patient.email}</div>
                          <div className="text-sm text-gray-500">{patient.phone}</div>
                        </div>
                      </td>
                      <td className="table-cell">
                        {new Date(patient.date_of_birth).toLocaleDateString()}
                      </td>
                      <td className="table-cell capitalize">{patient.gender}</td>
                      <td className="table-cell">
                        <span className={`badge ${
                          patient.status === 'active' ? 'badge-success' : 'badge-warning'
                        }`}>
                          {patient.status}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleOpenModal(patient)}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(patient.id)}
                            className="text-danger-600 hover:text-danger-900"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {(!patients || patients.length === 0) && (
                    <tr>
                      <td colSpan="6" className="table-cell text-center text-gray-500 py-8">
                        No patients found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Patient Modal */}
      <PatientModal />
    </div>
  );
};

export default Patients;
