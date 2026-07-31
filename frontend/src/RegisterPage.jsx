import { useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './Auth.css'

// Account creation page for new collectors.
function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const interestExhibit = useMemo(
    () => new URLSearchParams(location.search).get('interest_exhibit'),
    [location.search]
  )

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await register(username, email, password)
      // If registration started from an exhibit interest flow, continue it.
      const next = interestExhibit
        ? `/dashboard?interest_exhibit=${encodeURIComponent(interestExhibit)}`
        : '/dashboard'
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
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-sub">Save works to your collection and enquire with the gallery.</p>
        <form onSubmit={submit}>
          <label className="auth-label">
            Username
            <input className="auth-input" value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus aria-invalid={Boolean(error)} aria-describedby={error ? 'register-error' : undefined} />
          </label>
          <label className="auth-label">
            Email
            <input className="auth-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required aria-invalid={Boolean(error)} aria-describedby={error ? 'register-error' : undefined} />
          </label>
          <label className="auth-label">
            Password
            <input className="auth-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required aria-invalid={Boolean(error)} aria-describedby={error ? 'register-error' : undefined} />
          </label>
          {error && <p id="register-error" className="auth-error" role="alert" aria-live="assertive">{error}</p>}
          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? 'Creating…' : 'Create account'}
          </button>
        </form>
        <p className="auth-alt">
          Already have an account?{' '}
          <Link to={interestExhibit ? `/login?interest_exhibit=${encodeURIComponent(interestExhibit)}` : '/login'}>
            Sign in
          </Link>
        </p>
      </div>
    </main>
  )
}

export default RegisterPage
