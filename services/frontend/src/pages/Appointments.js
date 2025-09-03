import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { appointmentsAPI, patientsAPI, doctorsAPI } from '../services/api';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  CalendarIcon,
  ClockIcon,
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

const Appointments = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm();

  const selectedDoctorId = watch('doctor_id');

  // Fetch appointments
  const { data: appointmentsResponse, isLoading } = useQuery(
    ['appointments', searchTerm, filterStatus, selectedDate],
    () => appointmentsAPI.getAll({ search: searchTerm, status: filterStatus, date: selectedDate })
  );

  // Fetch patients for dropdown
  const { data: patientsResponse } = useQuery('patients', () => patientsAPI.getAll());

  // Fetch doctors for dropdown
  const { data: doctorsResponse } = useQuery('doctors', () => doctorsAPI.getAll());
  
  // Extract data from responses
  const appointments = appointmentsResponse?.data || [];
  const patients = patientsResponse?.data || [];
  const doctors = doctorsResponse?.data || [];

  // Create appointment mutation
  const createAppointmentMutation = useMutation(appointmentsAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('appointments');
      toast.success('Appointment created successfully!');
      handleCloseModal();
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  // Update appointment mutation
  const updateAppointmentMutation = useMutation(
    ({ id, data }) => appointmentsAPI.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('appointments');
        toast.success('Appointment updated successfully!');
        handleCloseModal();
      },
      onError: (error) => {
        const errorMessage = getErrorMessage(error);
        toast.error(errorMessage);
      },
    }
  );

  // Delete appointment mutation
  const deleteAppointmentMutation = useMutation(appointmentsAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('appointments');
      toast.success('Appointment deleted successfully!');
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  const handleOpenModal = (appointment = null) => {
    setEditingAppointment(appointment);
    if (appointment) {
      reset({
        patient_id: appointment.patient_id,
        doctor_id: appointment.doctor_id,
        appointment_type: appointment.appointment_type,
        appointment_date: appointment.scheduled_date.split('T')[0],
        appointment_time: appointment.scheduled_date.split('T')[1].substring(0, 5),
        duration_minutes: appointment.duration_minutes,
        notes: appointment.notes
      });
    } else {
      reset();
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingAppointment(null);
    reset();
  };

  const onSubmit = (data) => {
    const appointmentData = {
      patient_id: data.patient_id,
      doctor_id: data.doctor_id,
      appointment_type: data.appointment_type,
      scheduled_date: `${data.appointment_date}T${data.appointment_time}:00`,
      duration_minutes: data.duration_minutes || 30,
      notes: data.notes || ''
    };

    if (editingAppointment) {
      updateAppointmentMutation.mutate({ id: editingAppointment.id, data: appointmentData });
    } else {
      createAppointmentMutation.mutate(appointmentData);
    }
  };

  const handleDelete = (appointmentId) => {
    if (window.confirm('Are you sure you want to delete this appointment?')) {
      deleteAppointmentMutation.mutate(appointmentId);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'badge-success';
      case 'pending':
        return 'badge-warning';
      case 'cancelled':
        return 'badge-danger';
      default:
        return 'badge-info';
    }
  };

  const AppointmentModal = () => (
    <div className={`fixed inset-0 z-50 overflow-y-auto ${isModalOpen ? 'block' : 'hidden'}`}>
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleCloseModal}></div>
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    {editingAppointment ? 'Edit Appointment' : 'Schedule New Appointment'}
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Patient</label>
                      <select
                        className={`input mt-1 ${errors.patient_id ? 'input-error' : ''}`}
                        {...register('patient_id', { required: 'Patient is required' })}
                      >
                        <option value="">Select patient</option>
                        {patients?.map((patient) => (
                          <option key={patient.id} value={patient.id}>
                            {patient.first_name} {patient.last_name} - {patient.email}
                          </option>
                        ))}
                      </select>
                      {errors.patient_id && (
                        <p className="mt-1 text-sm text-danger-600">{errors.patient_id.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Doctor</label>
                      <select
                        className={`input mt-1 ${errors.doctor_id ? 'input-error' : ''}`}
                        {...register('doctor_id', { required: 'Doctor is required' })}
                      >
                        <option value="">Select doctor</option>
                        {doctors?.map((doctor) => (
                          <option key={doctor.id} value={doctor.id}>
                            Dr. {doctor.first_name} {doctor.last_name} - {doctor.specialization}
                          </option>
                        ))}
                      </select>
                      {errors.doctor_id && (
                        <p className="mt-1 text-sm text-danger-600">{errors.doctor_id.message}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Date</label>
                        <input
                          type="date"
                          className={`input mt-1 ${errors.appointment_date ? 'input-error' : ''}`}
                          {...register('appointment_date', { required: 'Date is required' })}
                        />
                        {errors.appointment_date && (
                          <p className="mt-1 text-sm text-danger-600">{errors.appointment_date.message}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Time</label>
                        <input
                          type="time"
                          className={`input mt-1 ${errors.appointment_time ? 'input-error' : ''}`}
                          {...register('appointment_time', { required: 'Time is required' })}
                        />
                        {errors.appointment_time && (
                          <p className="mt-1 text-sm text-danger-600">{errors.appointment_time.message}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Appointment Type</label>
                      <select
                        className={`input mt-1 ${errors.appointment_type ? 'input-error' : ''}`}
                        {...register('appointment_type', { required: 'Appointment type is required' })}
                      >
                        <option value="">Select type</option>
                        <option value="office_visit">Office Visit</option>
                        <option value="consultation">Consultation</option>
                        <option value="follow_up">Follow-up</option>
                        <option value="emergency">Emergency</option>
                        <option value="routine_checkup">Routine Check-up</option>
                      </select>
                      {errors.appointment_type && (
                        <p className="mt-1 text-sm text-danger-600">{errors.appointment_type.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <select
                        className={`input mt-1 ${errors.status ? 'input-error' : ''}`}
                        {...register('status', { required: 'Status is required' })}
                      >
                        <option value="">Select status</option>
                        <option value="scheduled">Scheduled</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="no_show">No Show</option>
                      </select>
                      {errors.status && (
                        <p className="mt-1 text-sm text-danger-600">{errors.status.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Notes</label>
                      <textarea
                        rows={3}
                        className={`input mt-1 ${errors.notes ? 'input-error' : ''}`}
                        {...register('notes')}
                        placeholder="Any additional notes..."
                      />
                      {errors.notes && (
                        <p className="mt-1 text-sm text-danger-600">{errors.notes.message}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={createAppointmentMutation.isLoading || updateAppointmentMutation.isLoading}
                className="btn-primary sm:ml-3 sm:w-auto"
              >
                {createAppointmentMutation.isLoading || updateAppointmentMutation.isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {editingAppointment ? 'Updating...' : 'Creating...'}
                  </div>
                ) : (
                  editingAppointment ? 'Update Appointment' : 'Schedule Appointment'
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
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and schedule patient appointments.
          </p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Schedule Appointment
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search appointments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="input"
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="cancelled">Cancelled</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Appointments table */}
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
                    <th className="table-header-cell">Doctor</th>
                    <th className="table-header-cell">Date & Time</th>
                    <th className="table-header-cell">Type</th>
                    <th className="table-header-cell">Status</th>
                    <th className="table-header-cell">Actions</th>
                  </tr>
                </thead>
                <tbody className="table-body">
                  {appointments?.map((appointment) => (
                    <tr key={appointment.id} className="table-row">
                      <td className="table-cell">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                            <span className="text-sm font-medium text-primary-600">
                              {appointment.patient_name?.charAt(0)?.toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {appointment.patient_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {appointment.patient_email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            Dr. {appointment.doctor_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {appointment.doctor_specialization}
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="flex items-center">
                          <CalendarIcon className="h-4 w-4 text-gray-400 mr-1" />
                          <span className="text-sm text-gray-900">
                            {new Date(appointment.appointment_date).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center mt-1">
                          <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                          <span className="text-sm text-gray-500">
                            {new Date(appointment.appointment_date).toLocaleTimeString()}
                          </span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="text-sm text-gray-900 capitalize">
                          {appointment.appointment_type}
                        </span>
                      </td>
                      <td className="table-cell">
                        <span className={`badge ${getStatusColor(appointment.status)}`}>
                          {appointment.status}
                        </span>
                      </td>
                      <td className="table-cell">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleOpenModal(appointment)}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(appointment.id)}
                            className="text-danger-600 hover:text-danger-900"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {(!appointments || appointments.length === 0) && (
                    <tr>
                      <td colSpan="6" className="table-cell text-center text-gray-500 py-8">
                        No appointments found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Appointment Modal */}
      <AppointmentModal />
    </div>
  );
};

export default Appointments;
