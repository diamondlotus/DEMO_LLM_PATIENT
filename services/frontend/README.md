# LotusHealth Frontend

A modern React-based frontend for the LotusHealth medical management system.

## Features

- 🔐 **Authentication & RBAC** - Secure login with role-based access control
- 👥 **Patient Management** - Complete CRUD operations for patient records
- 📅 **Appointment Scheduling** - Manage appointments with doctors and patients
- 👨‍⚕️ **Doctor Management** - Manage medical staff and their specializations
- 📊 **Dashboard** - Real-time statistics and overview
- ⚙️ **Settings** - System configuration and user preferences
- 🎨 **Modern UI** - Beautiful, responsive design with Tailwind CSS
- 📱 **Mobile Responsive** - Works perfectly on all devices

## Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **React Query** - Server state management
- **React Hook Form** - Form handling and validation
- **Tailwind CSS** - Utility-first CSS framework
- **Heroicons** - Beautiful SVG icons
- **Axios** - HTTP client for API calls
- **React Hot Toast** - Toast notifications
- **Recharts** - Data visualization

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (see main README)

### Installation

1. **Install dependencies:**
   ```bash
   cd services/frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Development

### Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.js       # Main layout with sidebar
│   └── ProtectedRoute.js # Route protection
├── contexts/           # React contexts
│   └── AuthContext.js  # Authentication context
├── pages/              # Page components
│   ├── Login.js        # Login page
│   ├── Dashboard.js    # Dashboard with stats
│   ├── Patients.js     # Patient management
│   ├── Appointments.js # Appointment scheduling
│   ├── Doctors.js      # Doctor management
│   └── Settings.js     # System settings
├── services/           # API services
│   └── api.js          # API client and endpoints
├── App.js              # Main app component
├── index.js            # App entry point
└── index.css           # Global styles
```

### Key Components

#### Authentication
- **Login Page** - Secure authentication with form validation
- **AuthContext** - Global authentication state management
- **ProtectedRoute** - Route protection based on authentication and roles

#### Patient Management
- **Patient List** - View all patients with search and filtering
- **Patient Form** - Add/edit patient information
- **Patient Details** - View comprehensive patient information

#### Appointment Management
- **Appointment Calendar** - Schedule and manage appointments
- **Appointment Form** - Create/edit appointments
- **Appointment Status** - Track appointment status

#### Doctor Management
- **Doctor List** - View all doctors with specialization filtering
- **Doctor Form** - Add/edit doctor information
- **Doctor Schedule** - Manage doctor availability

#### Dashboard
- **Statistics Cards** - Key metrics and KPIs
- **Recent Activity** - Latest appointments and updates
- **Charts** - Data visualization with Recharts

### API Integration

The frontend communicates with the backend through the API service layer:

```javascript
// Example API usage
import { patientsAPI } from '../services/api';

// Get all patients
const { data: patients } = useQuery('patients', patientsAPI.getAll);

// Create patient
const createPatient = useMutation(patientsAPI.create, {
  onSuccess: () => {
    queryClient.invalidateQueries('patients');
    toast.success('Patient created successfully!');
  }
});
```

### Styling

The app uses Tailwind CSS for styling with custom components:

```css
/* Custom button styles */
.btn-primary {
  @apply btn bg-primary-600 text-white hover:bg-primary-700;
}

/* Custom input styles */
.input {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md;
}
```

### State Management

- **React Query** - Server state management and caching
- **React Context** - Global authentication state
- **Local State** - Component-specific state with useState

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8003
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t lotushealth-frontend .

# Run container
docker run -p 3000:80 lotushealth-frontend
```

## Features in Detail

### Authentication & RBAC
- JWT-based authentication
- Role-based access control (Admin, Doctor, Staff)
- Protected routes based on permissions
- Automatic token refresh

### Patient Management
- Complete CRUD operations
- Search and filtering
- Medical history tracking
- Insurance information
- Contact details

### Appointment Scheduling
- Calendar-based scheduling
- Doctor availability checking
- Appointment types (consultation, follow-up, etc.)
- Status tracking (pending, confirmed, cancelled)

### Doctor Management
- Doctor profiles with specializations
- License management
- Schedule management
- Contact information

### Dashboard
- Real-time statistics
- Recent appointments
- Patient growth charts
- Revenue tracking

### Settings
- User profile management
- Clinic information
- System configuration
- Security settings
- Notification preferences

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states
4. Add form validation
5. Test on different screen sizes

## Troubleshooting

### Common Issues

1. **API Connection Error**
   - Check if backend is running
   - Verify API URL in environment variables
   - Check CORS configuration

2. **Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies are installed

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for CSS conflicts
   - Verify responsive breakpoints

## License

This project is part of the LotusHealth medical management system.
