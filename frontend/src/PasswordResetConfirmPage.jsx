import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import './Auth.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Step 2 of password reset: user sets a new password using link parameters.
function PasswordResetConfirmPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') || ''
  const token = searchParams.get('token') || ''

  const hasValidLinkParams = useMemo(() => Boolean(uid && token), [uid, token])

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [status, setStatus] = useState('idle') // idle | submitting | done
  const [error, setError] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setStatus('submitting')
    try {
      const res = await fetch(`${API_BASE}/api/auth/password-reset/confirm/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, token, new_password: password }),
      })
      const data = await res.json()
      if (!res.ok) {
        const firstError =
          data.new_password?.[0] || data.token?.[0] || data.uid?.[0] || data.detail || 'Reset failed.'
        throw new Error(firstError)
      }
      setStatus('done')
      setTimeout(() => navigate('/login', { replace: true }), 1200)
    } catch (err) {
      setError(err.message)
      setStatus('idle')
    }
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <Link to="/login" className="auth-brand">ExhibitGuide</Link>
        <h1 className="auth-title">Choose a new password</h1>

        {!hasValidLinkParams ? (
          <>
            <p className="auth-error" role="alert">Reset link is missing required details.</p>
            <p className="auth-alt">
              <Link to="/password-reset">Request a new link</Link>
            </p>
          </>
        ) : (
          <form onSubmit={submit}>
            <label className="auth-label">
              New password
              <input
                className="auth-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoFocus
                aria-invalid={Boolean(error)}
                aria-describedby={error ? 'password-reset-confirm-error' : undefined}
              />
            </label>
            <label className="auth-label">
              Confirm new password
              <input
                className="auth-input"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                aria-invalid={Boolean(error)}
                aria-describedby={error ? 'password-reset-confirm-error' : undefined}
              />
            </label>

            {error && <p id="password-reset-confirm-error" className="auth-error" role="alert" aria-live="assertive">{error}</p>}
            {status === 'done' && <p className="auth-success" role="status" aria-live="polite">Password updated. Redirecting to login…</p>}

            <button className="auth-submit" type="submit" disabled={status === 'submitting' || status === 'done'}>
              {status === 'submitting' ? 'Updating…' : 'Update password'}
            </button>
          </form>
        )}
      </div>
    </main>
  )
}

export default PasswordResetConfirmPage
