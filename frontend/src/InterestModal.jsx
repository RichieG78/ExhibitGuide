import { useState } from 'react'
import './InterestModal.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const IconClose = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
)

// Bottom-sheet lead-capture modal (Figma design 3). Captures an email and posts
// it to the public /api/interest/ endpoint as a Prospect for this exhibit.
function InterestModal({ exhibit, dwellStart, onClose, onSuccess }) {
  const [email, setEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if (!email || submitting) return
    setSubmitting(true)
    setError('')
    const dwell_time = dwellStart
      ? Math.max(0, Math.round((Date.now() - dwellStart) / 1000))
      : 0

    fetch(`${API_BASE}/api/interest/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exhibit: exhibit.id, email, dwell_time }),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.email?.[0] || data.detail || `Error ${response.status}`)
          })
        }
        return response.json()
      })
      .then(() => onSuccess())
      .catch((err) => {
        setError(err.message)
        setSubmitting(false)
      })
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
          {exhibit.gallery_name || 'The gallery'} will reach out personally with full
          details and provenance on <em>{exhibit.title || exhibit.artist}</em>.
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
          />
          <button className="modal-submit" type="submit" disabled={submitting}>
            {submitting ? 'Sending…' : 'Notify the Gallery'}
          </button>
        </form>

        {error && <p className="modal-error">{error}</p>}

        <p className="modal-signin">
          or <span className="modal-signin__link">sign in</span> · Google · Apple
        </p>
      </div>
    </div>
  )
}

export default InterestModal
