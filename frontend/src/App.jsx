import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/common/ProtectedRoute'

// Pages
import Landing       from './pages/Landing'
import Login         from './pages/Login'
import Register      from './pages/Register'
import Dashboard     from './pages/Dashboard'
import PlanTrip      from './pages/PlanTrip'
import TripSummary   from './pages/TripSummary'
import MapPage       from './pages/MapPage'
import SavedTrips    from './pages/SavedTrips'
import Profile       from './pages/Profile'
import AdminDashboard from './pages/AdminDashboard'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public */}
        <Route path="/"          element={<Landing />} />
        <Route path="/login"     element={<Login />} />
        <Route path="/register"  element={<Register />} />

        {/* Protected */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard"       element={<Dashboard />} />
          <Route path="/plan"            element={<PlanTrip />} />
          <Route path="/trip/:tripId"    element={<TripSummary />} />
          <Route path="/map"             element={<MapPage />} />
          <Route path="/saved"           element={<SavedTrips />} />
          <Route path="/profile"         element={<Profile />} />
        </Route>

        {/* Admin */}
        <Route element={<ProtectedRoute adminOnly />}>
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  )
}
