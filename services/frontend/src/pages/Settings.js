import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { settingsAPI, authAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  CogIcon,
  UserIcon,
  BuildingOfficeIcon,
  ShieldCheckIcon,
  BellIcon,
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

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm();

  // Fetch settings
  const { data: clinicSettings, isLoading: clinicLoading } = useQuery(
    'clinicSettings',
    settingsAPI.getClinicSettings
  );

  const { data: systemSettings, isLoading: systemLoading } = useQuery(
    'systemSettings',
    settingsAPI.getSystemSettings
  );

  // Update clinic settings mutation
  const updateClinicSettingsMutation = useMutation(settingsAPI.updateClinicSettings, {
    onSuccess: () => {
      queryClient.invalidateQueries('clinicSettings');
      toast.success('Clinic settings updated successfully!');
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  // Update system settings mutation
  const updateSystemSettingsMutation = useMutation(settingsAPI.updateSystemSettings, {
    onSuccess: () => {
      queryClient.invalidateQueries('systemSettings');
      toast.success('System settings updated successfully!');
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  // Change password mutation
  const changePasswordMutation = useMutation(authAPI.changePassword, {
    onSuccess: () => {
      toast.success('Password changed successfully!');
      reset();
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage);
    },
  });

  const handleProfileSubmit = (data) => {
    updateUser(data);
    toast.success('Profile updated successfully!');
  };

  const handleClinicSettingsSubmit = (data) => {
    updateClinicSettingsMutation.mutate(data);
  };

  const handleSystemSettingsSubmit = (data) => {
    updateSystemSettingsMutation.mutate(data);
  };

  const handlePasswordChange = (data) => {
    changePasswordMutation.mutate(data);
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'clinic', name: 'Clinic Settings', icon: BuildingOfficeIcon },
    { id: 'system', name: 'System Settings', icon: CogIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
  ];

  const ProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Personal Information</h3>
        <p className="mt-1 text-sm text-gray-500">
          Update your personal information and contact details.
        </p>
      </div>

      <form onSubmit={handleSubmit(handleProfileSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">First Name</label>
            <input
              type="text"
              defaultValue={user?.first_name || ''}
              className="input mt-1"
              {...register('first_name')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Last Name</label>
            <input
              type="text"
              defaultValue={user?.last_name || ''}
              className="input mt-1"
              {...register('last_name')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              defaultValue={user?.email || ''}
              className="input mt-1"
              {...register('email')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Phone</label>
            <input
              type="tel"
              defaultValue={user?.phone || ''}
              className="input mt-1"
              {...register('phone')}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Role</label>
          <input
            type="text"
            value={user?.role || ''}
            className="input mt-1 bg-gray-50"
            disabled
          />
        </div>

        <div className="flex justify-end">
          <button type="submit" className="btn-primary">
            Update Profile
          </button>
        </div>
      </form>
    </div>
  );

  const ClinicSettingsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Clinic Information</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure your clinic's basic information and settings.
        </p>
      </div>

      {clinicLoading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(handleClinicSettingsSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Clinic Name</label>
            <input
              type="text"
              defaultValue={clinicSettings?.clinic_name || ''}
              className="input mt-1"
              {...register('clinic_name')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Address</label>
            <textarea
              rows={3}
              defaultValue={clinicSettings?.address || ''}
              className="input mt-1"
              {...register('address')}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <input
                type="tel"
                defaultValue={clinicSettings?.phone || ''}
                className="input mt-1"
                {...register('phone')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                defaultValue={clinicSettings?.email || ''}
                className="input mt-1"
                {...register('email')}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Website</label>
            <input
              type="url"
              defaultValue={clinicSettings?.website || ''}
              className="input mt-1"
              {...register('website')}
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={updateClinicSettingsMutation.isLoading}
              className="btn-primary"
            >
              {updateClinicSettingsMutation.isLoading ? 'Updating...' : 'Save Settings'}
            </button>
          </div>
        </form>
      )}
    </div>
  );

  const SystemSettingsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">System Configuration</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure system-wide settings and preferences.
        </p>
      </div>

      {systemLoading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(handleSystemSettingsSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">System Name</label>
            <input
              type="text"
              defaultValue={systemSettings?.system_name || 'LotusHealth'}
              className="input mt-1"
              {...register('system_name')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Time Zone</label>
            <select
              defaultValue={systemSettings?.timezone || 'UTC'}
              className="input mt-1"
              {...register('timezone')}
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date Format</label>
            <select
              defaultValue={systemSettings?.date_format || 'MM/DD/YYYY'}
              className="input mt-1"
              {...register('date_format')}
            >
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={updateSystemSettingsMutation.isLoading}
              className="btn-primary"
            >
              {updateSystemSettingsMutation.isLoading ? 'Updating...' : 'Save Settings'}
            </button>
          </div>
        </form>
      )}
    </div>
  );

  const SecurityTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Security Settings</h3>
        <p className="mt-1 text-sm text-gray-500">
          Update your password and security preferences.
        </p>
      </div>

      <form onSubmit={handleSubmit(handlePasswordChange)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Current Password</label>
          <input
            type="password"
            className={`input mt-1 ${errors.old_password ? 'input-error' : ''}`}
            {...register('old_password', { required: 'Current password is required' })}
          />
          {errors.old_password && (
            <p className="mt-1 text-sm text-danger-600">{errors.old_password.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">New Password</label>
          <input
            type="password"
            className={`input mt-1 ${errors.new_password ? 'input-error' : ''}`}
            {...register('new_password', {
              required: 'New password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
            })}
          />
          {errors.new_password && (
            <p className="mt-1 text-sm text-danger-600">{errors.new_password.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Confirm New Password</label>
          <input
            type="password"
            className={`input mt-1 ${errors.confirm_password ? 'input-error' : ''}`}
            {...register('confirm_password', {
              required: 'Please confirm your password',
              validate: (value) => value === watch('new_password') || 'Passwords do not match',
            })}
          />
          {errors.confirm_password && (
            <p className="mt-1 text-sm text-danger-600">{errors.confirm_password.message}</p>
          )}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={changePasswordMutation.isLoading}
            className="btn-primary"
          >
            {changePasswordMutation.isLoading ? 'Changing...' : 'Change Password'}
          </button>
        </div>
      </form>
    </div>
  );

  const NotificationsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
        <p className="mt-1 text-sm text-gray-500">
          Configure how you receive notifications and alerts.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
            <p className="text-sm text-gray-500">Receive notifications via email</p>
          </div>
          <input
            type="checkbox"
            defaultChecked={true}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">SMS Notifications</h4>
            <p className="text-sm text-gray-500">Receive notifications via SMS</p>
          </div>
          <input
            type="checkbox"
            defaultChecked={false}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Appointment Reminders</h4>
            <p className="text-sm text-gray-500">Get reminded about upcoming appointments</p>
          </div>
          <input
            type="checkbox"
            defaultChecked={true}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-medium text-gray-900">System Alerts</h4>
            <p className="text-sm text-gray-500">Receive system maintenance and security alerts</p>
          </div>
          <input
            type="checkbox"
            defaultChecked={true}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button className="btn-primary">Save Preferences</button>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileTab />;
      case 'clinic':
        return <ClinicSettingsTab />;
      case 'system':
        return <SystemSettingsTab />;
      case 'security':
        return <SecurityTab />;
      case 'notifications':
        return <NotificationsTab />;
      default:
        return <ProfileTab />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and system preferences.
        </p>
      </div>

      {/* Settings tabs */}
      <div className="card">
        <div className="card-body p-0">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-5 w-5 inline mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
