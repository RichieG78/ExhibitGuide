import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

// Gate a route behind authentication. While the stored token is still being
// validated we render nothing; once ready, redirect to /login if not signed in.
function RequireAuth({ children }) {
  const { user, ready } = useAuth()
  const location = useLocation()

  if (!ready) return null
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  return children
}

export default RequireAuth
