import React from 'react';
import { useQuery } from 'react-query';
import { dashboardAPI } from '../services/api';
import {
  UserGroupIcon,
  CalendarIcon,
  UserIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const { data: statsResponse, isLoading: statsLoading, error: statsError } = useQuery(
    'dashboardStats', 
    dashboardAPI.getStats,
    {
      onError: (error) => console.error('Error fetching dashboard stats:', error),
      onSuccess: (data) => console.log('Dashboard stats data:', data)
    }
  );
  const { data: recentAppointmentsResponse, isLoading: appointmentsLoading, error: appointmentsError } = useQuery(
    'recentAppointments',
    dashboardAPI.getRecentAppointments,
    {
      onError: (error) => console.error('Error fetching recent appointments:', error),
      onSuccess: (data) => console.log('Recent appointments data:', data)
    }
  );
  const { data: upcomingAppointmentsResponse, isLoading: upcomingLoading, error: upcomingError } = useQuery(
    'upcomingAppointments',
    dashboardAPI.getUpcomingAppointments,
    {
      onError: (error) => console.error('Error fetching upcoming appointments:', error),
      onSuccess: (data) => console.log('Upcoming appointments data:', data)
    }
  );
  
  // Extract data from responses
  const stats = statsResponse?.data || {};
  const recentAppointments = Array.isArray(recentAppointmentsResponse?.data) ? recentAppointmentsResponse.data : [];
  const upcomingAppointments = Array.isArray(upcomingAppointmentsResponse?.data) ? upcomingAppointmentsResponse.data : [];

  const StatCard = ({ title, value, change, icon: Icon, color = 'primary' }) => (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center">
          <div className={`flex-shrink-0 p-3 rounded-md bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">{value}</div>
                {change && (
                  <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                    change > 0 ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {change > 0 ? (
                      <ArrowUpIcon className="self-center flex-shrink-0 h-4 w-4" />
                    ) : (
                      <ArrowDownIcon className="self-center flex-shrink-0 h-4 w-4" />
                    )}
                    <span className="sr-only">{change > 0 ? 'Increased' : 'Decreased'} by</span>
                    {Math.abs(change)}%
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );

  const AppointmentCard = ({ appointment }) => (
    <div className="flex items-center space-x-4 p-4 border-b border-gray-200 last:border-b-0">
      <div className="flex-shrink-0">
        <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
          <span className="text-sm font-medium text-primary-600">
            {appointment.patient_name?.charAt(0)?.toUpperCase()}
          </span>
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {appointment.patient_name}
        </p>
        <p className="text-sm text-gray-500">
          {appointment.doctor_name} • {appointment.appointment_type}
        </p>
      </div>
      <div className="flex-shrink-0 text-sm text-gray-500">
        {new Date(appointment.appointment_date).toLocaleDateString()}
      </div>
    </div>
  );

  if (statsLoading || appointmentsLoading || upcomingLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening with your clinic today.
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Patients"
          value={stats?.total_patients || 0}
          change={stats?.patient_growth || 0}
          icon={UserGroupIcon}
          color="primary"
        />
        <StatCard
          title="Today's Appointments"
          value={stats?.today_appointments || 0}
          change={stats?.appointment_growth || 0}
          icon={CalendarIcon}
          color="success"
        />
        <StatCard
          title="Active Doctors"
          value={stats?.active_doctors || 0}
          change={stats?.doctor_growth || 0}
          icon={UserIcon}
          color="warning"
        />
        <StatCard
          title="Monthly Revenue"
          value={`$${stats?.monthly_revenue?.toLocaleString() || 0}`}
          change={stats?.revenue_growth || 0}
          icon={CurrencyDollarIcon}
          color="danger"
        />
      </div>

      {/* Charts and recent activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Revenue Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Revenue Overview</h3>
          </div>
          <div className="card-body">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats?.revenue_data || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="revenue" stroke="#0ea5e9" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Recent Appointments */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Recent Appointments</h3>
          </div>
          <div className="card-body p-0">
            {appointmentsError && (
              <div className="p-4 text-center text-red-500">
                Error loading recent appointments: {appointmentsError.message}
              </div>
            )}
            {appointmentsLoading && (
              <div className="p-4 text-center text-gray-500">
                Loading recent appointments...
              </div>
            )}
            {!appointmentsLoading && !appointmentsError && (
              <div className="divide-y divide-gray-200">
                {Array.isArray(recentAppointments) && recentAppointments.slice(0, 5).map((appointment) => (
                  <AppointmentCard key={appointment.id} appointment={appointment} />
                ))}
                {(!Array.isArray(recentAppointments) || recentAppointments.length === 0) && (
                  <div className="p-4 text-center text-gray-500">
                    No recent appointments
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upcoming Appointments */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Upcoming Appointments</h3>
        </div>
        <div className="card-body p-0">
          <div className="overflow-hidden">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Patient</th>
                  <th className="table-header-cell">Doctor</th>
                  <th className="table-header-cell">Date & Time</th>
                  <th className="table-header-cell">Type</th>
                  <th className="table-header-cell">Status</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {Array.isArray(upcomingAppointments) && upcomingAppointments.map((appointment) => (
                  <tr key={appointment.id} className="table-row">
                    <td className="table-cell">
                      <div className="flex items-center">
                        <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center mr-3">
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
                    <td className="table-cell">{appointment.doctor_name}</td>
                    <td className="table-cell">
                      {new Date(appointment.appointment_date).toLocaleDateString()} at{' '}
                      {new Date(appointment.appointment_date).toLocaleTimeString()}
                    </td>
                    <td className="table-cell">{appointment.appointment_type}</td>
                    <td className="table-cell">
                      <span className={`badge ${
                        appointment.status === 'confirmed' ? 'badge-success' :
                        appointment.status === 'pending' ? 'badge-warning' :
                        'badge-danger'
                      }`}>
                        {appointment.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {(!Array.isArray(upcomingAppointments) || upcomingAppointments.length === 0) && (
                  <tr>
                    <td colSpan="5" className="table-cell text-center text-gray-500">
                      No upcoming appointments
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
