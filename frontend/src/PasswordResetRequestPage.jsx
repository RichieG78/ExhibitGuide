import { useState } from 'react'
import { Link } from 'react-router-dom'
import './Auth.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Step 1 of password reset: user submits email to receive a reset link.
function PasswordResetRequestPage() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | submitting | done
  const [error, setError] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    setStatus('submitting')
    setError('')

    try {
      const res = await fetch(`${API_BASE}/api/auth/password-reset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.email?.[0] || data.detail || 'Could not send reset link.')
      }
      setStatus('done')
    } catch (err) {
      setError(err.message)
      setStatus('idle')
    }
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <Link to="/login" className="auth-brand">ExhibitGuide</Link>
        <h1 className="auth-title">Reset your password</h1>
        <p className="auth-sub">Enter the email tied to your account.</p>

        <form onSubmit={submit}>
          <label className="auth-label">
            Email
            <input
              className="auth-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'password-reset-request-error' : undefined}
            />
          </label>

          {error && <p id="password-reset-request-error" className="auth-error" role="alert" aria-live="assertive">{error}</p>}
          {status === 'done' && (
            <p className="auth-success" role="status" aria-live="polite">
              If that email exists, a password reset link has been sent.
            </p>
          )}

          <button className="auth-submit" type="submit" disabled={status === 'submitting'}>
            {status === 'submitting' ? 'Sending…' : 'Send reset link'}
          </button>
        </form>

        <p className="auth-alt">
          Remembered it? <Link to="/login">Back to sign in</Link>
        </p>
      </div>
    </main>
  )
}

export default PasswordResetRequestPage
