import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './Auth.css'

async function readJsonSafe(res) {
  const contentType = res.headers.get('content-type') || ''
  const bodyText = await res.text()

  if (!bodyText) return {}

  if (contentType.includes('application/json')) {
    try {
      return JSON.parse(bodyText)
    } catch {
      return {}
    }
  }

  // Backend can return HTML for infrastructure/proxy errors; avoid JSON parse crashes.
  return { detail: `Unexpected response format (HTTP ${res.status}).` }
}

// Member profile page: loads current account data and lets users update the
// fields reused in enquiry/contact workflows.
function ProfilePage() {
  const navigate = useNavigate()
  const { authFetch, logout } = useAuth()

  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
  })
  const [status, setStatus] = useState('loading') // loading | ready | saving
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    // Initial load of profile values for the form.
    authFetch('/api/auth/profile/')
      .then(async (res) => {
        const data = await readJsonSafe(res)
        if (!res.ok) throw new Error(data.detail || 'Could not load profile.')
        setForm({
          username: data.username || '',
          email: data.email || '',
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          phone: data.phone || '',
          bio: data.bio || '',
        })
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('ready')
      })
  }, [authFetch])

  const onChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setStatus('saving')
    setError('')
    setSuccess('')

    try {
      // Persist the full profile so future enquiry forms can be pre-filled.
      const res = await authFetch('/api/auth/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await readJsonSafe(res)
      if (!res.ok) {
        const firstError =
          data.username?.[0] ||
          data.email?.[0] ||
          data.first_name?.[0] ||
          data.last_name?.[0] ||
          data.phone?.[0] ||
          data.bio?.[0] ||
          data.detail ||
          'Could not save profile.'
        throw new Error(firstError)
      }
      setForm((prev) => ({
        ...prev,
        username: data.username || '',
        email: data.email || '',
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        phone: data.phone || '',
        bio: data.bio || '',
      }))
      setSuccess('Profile updated.')
    } catch (err) {
      setError(err.message)
    } finally {
      setStatus('ready')
    }
  }

  const signingOut = () => {
    logout()
    navigate('/login')
  }

  return (
    <main className="auth-screen">
      <div className="auth-card">
        <div className="auth-topbar">
          <button
            type="button"
            className="auth-linkbtn auth-linkbtn--back"
            onClick={() => navigate('/dashboard')}
            aria-label="Back to dashboard"
          >
            ← Back
          </button>

          <Link to="/dashboard" className="auth-brand auth-brand--center">ExhibitGuide</Link>
          <span className="auth-topbar__spacer" aria-hidden="true" />
        </div>

        {error && <p className="auth-notice auth-notice--error" role="alert">{error}</p>}
        {success && <p className="auth-notice auth-notice--success" role="status">{success}</p>}

        <h1 className="auth-title">Your profile</h1>
        <p className="auth-sub">Update account details used for collector inquiries.</p>

        <form onSubmit={onSubmit}>
          <label className="auth-label">
            Username
            <input className="auth-input" name="username" value={form.username} onChange={onChange} required />
          </label>
          <label className="auth-label">
            Email
            <input className="auth-input" type="email" name="email" value={form.email} onChange={onChange} required />
          </label>
          <label className="auth-label">
            First name
            <input className="auth-input" name="first_name" value={form.first_name} onChange={onChange} />
          </label>
          <label className="auth-label">
            Last name
            <input className="auth-input" name="last_name" value={form.last_name} onChange={onChange} />
          </label>
          <label className="auth-label">
            Phone
            <input className="auth-input" name="phone" value={form.phone} onChange={onChange} />
          </label>
          <label className="auth-label">
            Bio
            <textarea className="auth-textarea" name="bio" value={form.bio} onChange={onChange} rows={4} />
          </label>

          <button className="auth-submit" type="submit" disabled={status !== 'ready'}>
            {status === 'saving' ? 'Saving…' : 'Save profile'}
          </button>
        </form>

        <div className="auth-actions">
          <button type="button" className="auth-linkbtn" onClick={() => navigate('/dashboard')}>Back to dashboard</button>
          <button type="button" className="auth-linkbtn" onClick={signingOut}>Log out</button>
        </div>
      </div>
    </main>
  )
}

export default ProfilePage
