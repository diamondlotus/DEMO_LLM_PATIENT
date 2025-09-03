import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { usersAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  UserIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  ShieldCheckIcon,
  UserGroupIcon,
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

const Users = () => {
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [viewingUser, setViewingUser] = useState(null);
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  // Fetch users
  const { data: usersResponse, isLoading, error } = useQuery(
    'users',
    usersAPI.getAll,
    {
      onError: (error) => {
        console.error('Error fetching users:', error);
        toast.error('Failed to fetch users');
      }
    }
  );
  
  // Extract users array from response
  const users = usersResponse?.data || [];

  // Create user mutation
  const createUserMutation = useMutation(usersAPI.create, {
    onSuccess: () => {
      queryClient.invalidateQueries('users');
      setShowModal(false);
      reset();
      toast.success('User created successfully');
    },
    onError: (error) => {
      console.error('Error creating user:', error);
      toast.error(getErrorMessage(error));
    },
  });

  // Update user mutation
  const updateUserMutation = useMutation(
    ({ id, userData }) => usersAPI.update(id, userData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
        setShowModal(false);
        setEditingUser(null);
        reset();
        toast.success('User updated successfully');
      },
      onError: (error) => {
        console.error('Error updating user:', error);
        toast.error(getErrorMessage(error));
      },
    }
  );

  // Delete user mutation
  const deleteUserMutation = useMutation(usersAPI.delete, {
    onSuccess: () => {
      queryClient.invalidateQueries('users');
      toast.success('User deleted successfully');
    },
    onError: (error) => {
      console.error('Error deleting user:', error);
      toast.error(getErrorMessage(error));
    },
  });

  const onSubmit = (data) => {
    // Combine first_name and last_name into full_name
    const userData = {
      ...data,
      full_name: `${data.first_name} ${data.last_name}`.trim()
    };
    
    if (editingUser) {
      updateUserMutation.mutate({ id: editingUser.id, userData });
    } else {
      createUserMutation.mutate(userData);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    // Parse full_name into first_name and last_name
    const nameParts = user.full_name ? user.full_name.split(' ') : ['', ''];
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';
    
    reset({
      username: user.username,
      email: user.email,
      first_name: firstName,
      last_name: lastName,
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active,
    });
    setShowModal(true);
  };

  const handleDelete = (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteUserMutation.mutate(userId);
    }
  };

  const handleView = (user) => {
    setViewingUser(user);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingUser(null);
    setViewingUser(null);
    reset();
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800';
      case 'doctor':
        return 'bg-blue-100 text-blue-800';
      case 'nurse':
        return 'bg-green-100 text-green-800';
      case 'receptionist':
        return 'bg-yellow-100 text-yellow-800';
      case 'patient':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <ShieldCheckIcon className="h-4 w-4" />;
      case 'doctor':
        return <UserIcon className="h-4 w-4" />;
      case 'nurse':
        return <UserIcon className="h-4 w-4" />;
      case 'receptionist':
        return <UserIcon className="h-4 w-4" />;
      case 'patient':
        return <UserIcon className="h-4 w-4" />;
      default:
        return <UserIcon className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading users: {getErrorMessage(error)}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage system users and their roles</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="btn btn-primary"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add User
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 rounded-md bg-blue-100">
                <UserGroupIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Users</p>
                <p className="text-2xl font-semibold text-gray-900">{users.length}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 rounded-md bg-green-100">
                <UserIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Active Users</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {users.filter(u => u.is_active).length}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 rounded-md bg-red-100">
                <ShieldCheckIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Admins</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {users.filter(u => u.role === 'admin').length}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 rounded-md bg-blue-100">
                <UserIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Doctors</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {users.filter(u => u.role === 'doctor').length}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">All Users</h3>
        </div>
        <div className="card-body p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="table-header-cell">User</th>
                  <th className="table-header-cell">Role</th>
                  <th className="table-header-cell">Status</th>
                  <th className="table-header-cell">Created</th>
                  <th className="table-header-cell">Actions</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {users.map((user) => (
                  <tr key={user.id} className="table-row">
                    <td className="table-cell">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center mr-4">
                          <span className="text-sm font-medium text-primary-600">
                            {user.full_name?.charAt(0)?.toUpperCase() || user.username?.charAt(0)?.toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {user.full_name || user.username}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                        {getRoleIcon(user.role)}
                        <span className="ml-1 capitalize">{user.role}</span>
                      </span>
                    </td>
                    <td className="table-cell">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="table-cell">
                      <div className="text-sm text-gray-900">
                        {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="table-cell">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleView(user)}
                          className="text-blue-600 hover:text-blue-900"
                          title="View Details"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(user)}
                          className="text-yellow-600 hover:text-yellow-900"
                          title="Edit User"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        {user.id !== currentUser?.id && (
                          <button
                            onClick={() => handleDelete(user.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete User"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create/Edit User Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingUser ? 'Edit User' : 'Create New User'}
              </h3>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Username
                  </label>
                  <input
                    type="text"
                    {...register('username', { required: 'Username is required' })}
                    className="form-input"
                    disabled={editingUser}
                  />
                  {errors.username && (
                    <p className="text-red-600 text-sm">{errors.username.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    {...register('email', { 
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    className="form-input"
                  />
                  {errors.email && (
                    <p className="text-red-600 text-sm">{errors.email.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      First Name
                    </label>
                    <input
                      type="text"
                      {...register('first_name', { required: 'First name is required' })}
                      className="form-input"
                    />
                    {errors.first_name && (
                      <p className="text-red-600 text-sm">{errors.first_name.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Last Name
                    </label>
                    <input
                      type="text"
                      {...register('last_name', { required: 'Last name is required' })}
                      className="form-input"
                    />
                    {errors.last_name && (
                      <p className="text-red-600 text-sm">{errors.last_name.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Role
                  </label>
                  <select
                    {...register('role', { required: 'Role is required' })}
                    className="form-select"
                  >
                    <option value="">Select a role</option>
                    <option value="admin">Admin</option>
                    <option value="doctor">Doctor</option>
                    <option value="nurse">Nurse</option>
                    <option value="receptionist">Receptionist</option>
                    <option value="patient">Patient</option>
                  </select>
                  {errors.role && (
                    <p className="text-red-600 text-sm">{errors.role.message}</p>
                  )}
                </div>

                {!editingUser && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Password
                    </label>
                    <input
                      type="password"
                      {...register('password', { 
                        required: !editingUser ? 'Password is required' : false,
                        minLength: {
                          value: 6,
                          message: 'Password must be at least 6 characters'
                        }
                      })}
                      className="form-input"
                    />
                    {errors.password && (
                      <p className="text-red-600 text-sm">{errors.password.message}</p>
                    )}
                  </div>
                )}

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('is_active')}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Active
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createUserMutation.isLoading || updateUserMutation.isLoading}
                    className="btn btn-primary"
                  >
                    {createUserMutation.isLoading || updateUserMutation.isLoading
                      ? 'Saving...'
                      : editingUser
                      ? 'Update User'
                      : 'Create User'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* View User Modal */}
      {viewingUser && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">User Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Username</label>
                  <p className="text-sm text-gray-900">{viewingUser.username}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <p className="text-sm text-gray-900">{viewingUser.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <p className="text-sm text-gray-900">{viewingUser.full_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(viewingUser.role)}`}>
                    {getRoleIcon(viewingUser.role)}
                    <span className="ml-1 capitalize">{viewingUser.role}</span>
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    viewingUser.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {viewingUser.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Created</label>
                  <p className="text-sm text-gray-900">
                    {new Date(viewingUser.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex justify-end pt-4">
                <button
                  onClick={closeModal}
                  className="btn btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
