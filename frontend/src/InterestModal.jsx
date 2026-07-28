import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './InterestModal.css'

const PENDING_INTEREST_KEY = 'eg_interest_exhibit_id'

const IconClose = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
)

function InterestModal({ exhibit, dwellStart, onClose, onSuccess }) {
  const navigate = useNavigate()
  const { user, register } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const usernameFromEmail = (value) => {
    const local = value.split('@')[0] || 'collector'
    return local.toLowerCase().replace(/[^a-z0-9_]/g, '_').replace(/_+/g, '_').slice(0, 24) || 'collector'
  }

  const registerWithRetry = async (baseUsername, emailValue, passwordValue) => {
    let username = baseUsername
    for (let i = 0; i < 4; i += 1) {
      try {
        await register(username, emailValue, passwordValue)
        return
      } catch (err) {
        const msg = String(err?.message || '')
        if (!/username|taken|exists/i.test(msg)) {
          throw err
        }
        username = `${baseUsername}_${Math.floor(1000 + Math.random() * 9000)}`
      }
    }
    throw new Error('Could not create account. Please try a different email.')
  }

  const submit = async (e) => {
    e.preventDefault()
    if (submitting) return

    setSubmitting(true)
    setError('')

    try {
      localStorage.setItem(PENDING_INTEREST_KEY, String(exhibit.id))

      if (user) {
        onSuccess()
        navigate(`/dashboard?interest_exhibit=${exhibit.id}`, { replace: true })
        return
      }

      if (!email || !password) {
        throw new Error('Email and password are required.')
      }

      const baseUsername = usernameFromEmail(email)
      await registerWithRetry(baseUsername, email, password)
      onSuccess()
      navigate(`/dashboard?interest_exhibit=${exhibit.id}`, { replace: true })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="modal-sheet" role="dialog" aria-modal="true" aria-label="Express your interest">
        <div className="modal-header">
          <span className="modal-handle" aria-hidden="true" />
          <h2 className="modal-title">Express your interest</h2>
          <button className="modal-close" type="button" onClick={onClose} aria-label="Close">
            <IconClose />
          </button>
        </div>

        <p className="modal-sub">
          Create your collector account in seconds to express interest in{' '}
          <em>{exhibit.title || exhibit.artist}</em> and continue on your dashboard.
        </p>

        <form onSubmit={submit}>
          <input
            className="modal-input"
            type="email"
            required
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoFocus
            disabled={Boolean(user)}
          />
          {!user && (
            <input
              className="modal-input"
              type="password"
              required
              placeholder="Create password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          )}
          <button className="modal-submit" type="submit" disabled={submitting}>
            {submitting ? 'Continuing…' : user ? 'Continue to dashboard' : 'Create account and continue'}
          </button>
        </form>

        {error && <p className="modal-error">{error}</p>}

        {!user && (
          <p className="modal-signin">
            Already have an account?{' '}
            <Link
              to={`/login?interest_exhibit=${exhibit.id}`}
              className="modal-signin__link"
              onClick={onClose}
            >
              Sign in
            </Link>
          </p>
        )}
      </div>
    </div>
  )
}

export default InterestModal
