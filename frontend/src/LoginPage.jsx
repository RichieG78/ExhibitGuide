import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './Auth.css'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const next = location.state?.from || '/dashboard'

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await login(username, password)
      navigate(next, { replace: true })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <Link to="/" className="auth-brand">ExhibitGuide</Link>
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-sub">Sign in to your collector account.</p>
        <form onSubmit={submit}>
          <label className="auth-label">
            Username
            <input className="auth-input" value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
          </label>
          <label className="auth-label">
            Password
            <input className="auth-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          {error && <p className="auth-error">{error}</p>}
          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className="auth-alt">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </main>
  )
}

export default LoginPage
