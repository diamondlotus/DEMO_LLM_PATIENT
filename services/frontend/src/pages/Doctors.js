import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { doctorsAPI, authAPI } from '../services/api';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  UserIcon,
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

const Doctors = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [filterSpecialization, setFilterSpecialization] = useState('all');
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  // Fetch doctors
  const { data: doctorsResponse, isLoading, error } = useQuery(
    ['doctors', searchTerm, filterSpecialization],
    () => doctorsAPI.getAll({ search: searchTerm, specialization: filterSpecialization }),
    {
      onError: (error) => {
        console.error('Error fetching doctors:', error);
        toast.error('Failed to fetch doctors');
      },
      onSuccess: (data) => {
        console.log('Doctors data:', data);
      }
    }
  );
  
  // Extract doctors array from response
  const doctors = doctorsResponse?.data || [];

  // Create doctor mutation
  const createDoctorMutation = useMutation(doctorsAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('doctors');
      toast.success('Doctor created successfully!');
      handleCloseModal();
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  // Update doctor mutation
  const updateDoctorMutation = useMutation(
    ({ id, data }) => doctorsAPI.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('doctors');
        toast.success('Doctor updated successfully!');
        handleCloseModal();
      },
      onError: (error) => {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
      },
    }
  );

  // Delete doctor mutation
  const deleteDoctorMutation = useMutation(doctorsAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('doctors');
      toast.success('Doctor deleted successfully!');
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  const handleOpenModal = (doctor = null) => {
    setEditingDoctor(doctor);
    if (doctor) {
      // For editing, only set doctor-specific fields
      reset({
        specialization: doctor.specialization,
        license_number: doctor.license_number,
        years_experience: doctor.years_experience,
        education: doctor.education ? doctor.education.join('\n') : '',
        certifications: doctor.certifications ? doctor.certifications.join('\n') : '',
        is_active: doctor.is_active
      });
    } else {
      reset();
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingDoctor(null);
    reset();
  };

  const onSubmit = async (data) => {
    if (editingDoctor) {
      // For updating doctors, process education and certifications
      const updateData = {
        ...data,
        education: data.education ? data.education.split('\n').filter(line => line.trim()) : [],
        certifications: data.certifications ? data.certifications.split('\n').filter(line => line.trim()) : []
      };
      updateDoctorMutation.mutate({ id: editingDoctor.id, data: updateData });
    } else {
      // For new doctors, send all data to backend - it will create user automatically
      const doctorData = {
        // User creation fields
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        phone: data.phone,
        address: data.address,
        // Doctor fields
        specialization: data.specialization,
        license_number: data.license_number,
        years_experience: data.years_experience || 0,
        education: data.education ? data.education.split('\n').filter(line => line.trim()) : [],
        certifications: data.certifications ? data.certifications.split('\n').filter(line => line.trim()) : [],
        is_active: true
      };
      
      createDoctorMutation.mutate(doctorData);
    }
  };

  const handleDelete = (doctorId) => {
    if (window.confirm('Are you sure you want to delete this doctor?')) {
      deleteDoctorMutation.mutate(doctorId);
    }
  };

  const specializations = [
    'Cardiology',
    'Dermatology',
    'Endocrinology',
    'Gastroenterology',
    'General Practice',
    'Neurology',
    'Oncology',
    'Orthopedics',
    'Pediatrics',
    'Psychiatry',
    'Radiology',
    'Surgery',
  ];

  const DoctorModal = () => (
    <div className={`fixed inset-0 z-50 overflow-y-auto ${isModalOpen ? 'block' : 'hidden'}`}>
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleCloseModal}></div>
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    {editingDoctor ? 'Edit Doctor' : 'Add New Doctor'}
                  </h3>
                  
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {!editingDoctor && (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">First Name</label>
                          <input
                            type="text"
                            className={`input mt-1 ${errors.first_name ? 'input-error' : ''}`}
                            {...register('first_name', { required: !editingDoctor ? 'First name is required' : false })}
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
                            {...register('last_name', { required: !editingDoctor ? 'Last name is required' : false })}
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
                              required: !editingDoctor ? 'Email is required' : false,
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
                            {...register('phone', { required: !editingDoctor ? 'Phone number is required' : false })}
                          />
                          {errors.phone && (
                            <p className="mt-1 text-sm text-danger-600">{errors.phone.message}</p>
                          )}
                        </div>
                      </>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Specialization</label>
                      <select
                        className={`input mt-1 ${errors.specialization ? 'input-error' : ''}`}
                        {...register('specialization', { required: 'Specialization is required' })}
                      >
                        <option value="">Select specialization</option>
                        {specializations.map((spec) => (
                          <option key={spec} value={spec}>{spec}</option>
                        ))}
                      </select>
                      {errors.specialization && (
                        <p className="mt-1 text-sm text-danger-600">{errors.specialization.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">License Number</label>
                      <input
                        type="text"
                        className={`input mt-1 ${errors.license_number ? 'input-error' : ''}`}
                        {...register('license_number', { required: 'License number is required' })}
                      />
                      {errors.license_number && (
                        <p className="mt-1 text-sm text-danger-600">{errors.license_number.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Years of Experience</label>
                      <input
                        type="number"
                        min="0"
                        max="50"
                        className={`input mt-1 ${errors.years_experience ? 'input-error' : ''}`}
                        {...register('years_experience', { 
                          min: { value: 0, message: 'Years of experience must be at least 0' },
                          max: { value: 50, message: 'Years of experience must be at most 50' }
                        })}
                      />
                      {errors.years_experience && (
                        <p className="mt-1 text-sm text-danger-600">{errors.years_experience.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Address</label>
                      <textarea
                        rows={3}
                        className={`input mt-1 ${errors.address ? 'input-error' : ''}`}
                        {...register('address')}
                      />
                      {errors.address && (
                        <p className="mt-1 text-sm text-danger-600">{errors.address.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Education (one per line)</label>
                      <textarea
                        rows={2}
                        className={`input mt-1 ${errors.education ? 'input-error' : ''}`}
                        {...register('education')}
                        placeholder="MD from Harvard Medical School&#10;Residency at Johns Hopkins"
                      />
                      {errors.education && (
                        <p className="mt-1 text-sm text-danger-600">{errors.education.message}</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700">Certifications (one per line)</label>
                      <textarea
                        rows={2}
                        className={`input mt-1 ${errors.certifications ? 'input-error' : ''}`}
                        {...register('certifications')}
                        placeholder="Board Certified in Cardiology&#10;ACLS Certified"
                      />
                      {errors.certifications && (
                        <p className="mt-1 text-sm text-danger-600">{errors.certifications.message}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={createDoctorMutation.isLoading || updateDoctorMutation.isLoading}
                className="btn-primary sm:ml-3 sm:w-auto"
              >
                {createDoctorMutation.isLoading || updateDoctorMutation.isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {editingDoctor ? 'Updating...' : 'Creating...'}
                  </div>
                ) : (
                  editingDoctor ? 'Update Doctor' : 'Create Doctor'
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
          <h1 className="text-2xl font-bold text-gray-900">Doctors</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your medical staff and their information.
          </p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Doctor
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search doctors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={filterSpecialization}
            onChange={(e) => setFilterSpecialization(e.target.value)}
            className="input"
          >
            <option value="all">All Specializations</option>
            {specializations.map((spec) => (
              <option key={spec} value={spec}>{spec}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Doctors table */}
      <div className="card">
        <div className="card-body p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <p className="text-red-600 mb-4">Error loading doctors: {error.message}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="btn btn-primary"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="overflow-hidden">
              <table className="table">
                <thead className="table-header">
                  <tr>
                    <th className="table-header-cell">Doctor</th>
                    <th className="table-header-cell">Contact</th>
                    <th className="table-header-cell">Specialization</th>
                    <th className="table-header-cell">License</th>
                    <th className="table-header-cell">Status</th>
                    <th className="table-header-cell">Actions</th>
                  </tr>
                </thead>
                <tbody className="table-body">
                  {doctors?.map((doctor) => (
                    <tr key={doctor.id} className="table-row">
                      <td className="table-cell">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                            <UserIcon className="h-5 w-5 text-primary-600" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              Dr. {doctor.first_name} {doctor.last_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {doctor.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div>
                          <div className="text-sm text-gray-900">{doctor.email}</div>
                          <div className="text-sm text-gray-500">{doctor.phone}</div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="text-sm text-gray-900">{doctor.specialization}</span>
                      </td>
                      <td className="table-cell">
                        <span className="text-sm text-gray-900">{doctor.license_number}</span>
                      </td>
                      <td className="table-cell">
                        <span className={`badge ${
                          doctor.status === 'active' ? 'badge-success' : 'badge-warning'
                        }`}>
                          {doctor.status}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleOpenModal(doctor)}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(doctor.id)}
                            className="text-danger-600 hover:text-danger-900"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {(!doctors || doctors.length === 0) && (
                    <tr>
                      <td colSpan="6" className="table-cell text-center text-gray-500 py-8">
                        No doctors found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Doctor Modal */}
      <DoctorModal />
    </div>
  );
};

export default Doctors;
