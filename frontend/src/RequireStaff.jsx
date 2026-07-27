import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

// Gate a route behind staff (gallery-owner) access. Not signed in → login;
// signed in but not staff → back to the public gallery.
function RequireStaff({ children }) {
  const { user, ready } = useAuth()
  const location = useLocation()

  if (!ready) return null
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (!user.is_staff) return <Navigate to="/" replace />
  return children
}

export default RequireStaff
