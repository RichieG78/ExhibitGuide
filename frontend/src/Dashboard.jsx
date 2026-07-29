import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ExhibitImage from './ExhibitImage'
import './Dashboard.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const PENDING_INTEREST_KEY = 'eg_interest_exhibit_id'
const CONTACT_PREF_PROMPT_KEY = 'eg_contact_pref_prompt'
const FILTERS = ['All', 'Watching', 'Enquired', 'Acquired']

const IconBack = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
)
const IconArrowRight = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
)

function Dashboard() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, authFetch } = useAuth()
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [filter, setFilter] = useState('All')
  const [contactMethod, setContactMethod] = useState('email')
  const [contactEmail, setContactEmail] = useState('')
  const [contactPhone, setContactPhone] = useState('')
  const [note, setNote] = useState('')
  const [modalError, setModalError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [activeInquiryItem, setActiveInquiryItem] = useState(null)
  const [submittingInquiry, setSubmittingInquiry] = useState(false)
  const [profileData, setProfileData] = useState({ email: '', phone: '' })
  const [autoSavingInterest, setAutoSavingInterest] = useState(false)
  const [prefModalOpen, setPrefModalOpen] = useState(false)
  const [prefMethod, setPrefMethod] = useState('email')
  const [prefEmail, setPrefEmail] = useState('')
  const [prefPhone, setPrefPhone] = useState('')
  const [prefError, setPrefError] = useState('')
  const [savingPreference, setSavingPreference] = useState(false)
  const [prefPromptShownThisVisit, setPrefPromptShownThisVisit] = useState(false)
  const autoSavedRef = useRef(false)

  const interestExhibitId = useMemo(() => {
    const fromQuery = searchParams.get('interest_exhibit')
    if (fromQuery) return fromQuery
    return localStorage.getItem(PENDING_INTEREST_KEY)
  }, [searchParams])

  const load = useCallback(() => {
    setStatus('loading')
    authFetch('/api/collection/')
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setItems(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [authFetch])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    authFetch('/api/auth/profile/')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!data) return
        setProfileData({ email: data.email || '', phone: data.phone || '' })
        setContactEmail(data.email || '')
        setPrefEmail(data.email || '')
        setPrefPhone(data.phone || '')
      })
      .catch(() => {
        // Non-blocking for dashboard render.
      })
  }, [authFetch])

  useEffect(() => {
    const shouldPrompt = localStorage.getItem(CONTACT_PREF_PROMPT_KEY) === '1'
    if (!shouldPrompt || prefModalOpen || modalOpen || prefPromptShownThisVisit) return

    setPrefMethod(profileData.phone ? 'phone' : 'email')
    setPrefEmail(profileData.email || user?.email || '')
    setPrefPhone(profileData.phone || '')
    setPrefError('')
    setPrefModalOpen(true)
    setPrefPromptShownThisVisit(true)
  }, [prefModalOpen, modalOpen, profileData, user, prefPromptShownThisVisit])

  useEffect(() => {
    if (!interestExhibitId || autoSavedRef.current || status !== 'ready') return
    const alreadyInWatchlist = items.some(
      (item) => String(item.id) === String(interestExhibitId) && item.status !== 'enquired'
    )
    const alreadyInCollection = items.some((item) => String(item.id) === String(interestExhibitId))

    if (alreadyInCollection) {
      autoSavedRef.current = true
      localStorage.removeItem(PENDING_INTEREST_KEY)
      return
    }

    if (alreadyInWatchlist) {
      autoSavedRef.current = true
      return
    }

    autoSavedRef.current = true
    setAutoSavingInterest(true)
    authFetch('/api/saved/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exhibit: Number(interestExhibitId) }),
    })
      .then((res) => {
        if (!res.ok) throw new Error('Could not add artwork to watchlist')
        localStorage.removeItem(PENDING_INTEREST_KEY)
        setNotice('The scanned artwork has been added to your watchlist.')
        return load()
      })
      .catch(() => {
        setNotice('Could not auto-add the scanned artwork. Please try again.')
      })
      .finally(() => setAutoSavingInterest(false))
  }, [interestExhibitId, status, items, authFetch, load])

  const visible = filter === 'All' ? items : items.filter((it) => it.status === filter.toLowerCase())

  const openEnquiryModal = (item) => {
    if (prefModalOpen) return
    setActiveInquiryItem(item)
    setContactMethod('email')
    setContactEmail(profileData.email || user?.email || '')
    setContactPhone(profileData.phone || '')
    setNote('')
    setModalError('')
    setModalOpen(true)
  }

  const closeEnquiryModal = () => {
    setModalOpen(false)
    setActiveInquiryItem(null)
    setModalError('')
  }

  const closePreferenceModal = () => {
    setPrefModalOpen(false)
    setPrefError('')
  }

  const saveContactPreference = async (event) => {
    event.preventDefault()
    if (savingPreference) return

    const email = (prefEmail || '').trim()
    const phone = (prefPhone || '').trim()

    if (prefMethod === 'email' && !email) {
      setPrefError('Please add your email address to continue.')
      return
    }
    if ((prefMethod === 'phone' || prefMethod === 'text') && !phone) {
      setPrefError('Please add your phone number to continue.')
      return
    }

    setSavingPreference(true)
    setPrefError('')
    try {
      const payload = {}
      if (email) payload.email = email
      if (phone) payload.phone = phone
      const res = await authFetch('/api/auth/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.detail || data.phone?.[0] || data.email?.[0] || 'Could not save contact preference.')
      }

      setProfileData({
        email: data.email || email,
        phone: data.phone || phone,
      })
      setContactEmail(data.email || email)
      setContactPhone(data.phone || phone)
      setNotice('Contact preference saved to your profile. You can change it any time from Profile.')
      localStorage.removeItem(CONTACT_PREF_PROMPT_KEY)
      closePreferenceModal()
    } catch (err) {
      setPrefError(err.message)
    } finally {
      setSavingPreference(false)
    }
  }

  const submitEnquiry = async (event) => {
    event.preventDefault()
    if (!activeInquiryItem || submittingInquiry) return

    const cleanEmail = (contactEmail || '').trim()
    const cleanPhone = (contactPhone || '').trim()
    const profileEmail = (profileData.email || user?.email || '').trim()
    const profilePhone = (profileData.phone || '').trim()
    const resolvedEmail = cleanEmail || profileEmail
    const resolvedPhone = cleanPhone || profilePhone

    if (contactMethod === 'email' && !resolvedEmail) {
      setModalError('Please add your email address to continue.')
      return
    }
    if ((contactMethod === 'phone' || contactMethod === 'text') && !resolvedPhone) {
      setModalError('Please add your phone number to continue.')
      return
    }

    setSubmittingInquiry(true)
    setModalError('')
    try {
      const methodLabel = contactMethod === 'text' ? 'Text message' : contactMethod[0].toUpperCase() + contactMethod.slice(1)
      const messageLines = []
      if (note.trim()) messageLines.push(note.trim())
      messageLines.push(`Preferred contact method: ${methodLabel}`)
      if (resolvedEmail) messageLines.push(`Email: ${resolvedEmail}`)
      if (resolvedPhone) messageLines.push(`Phone: ${resolvedPhone}`)

      const res = await authFetch('/api/inquiries/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exhibit: activeInquiryItem.id,
          message: messageLines.join('\n\n'),
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.detail || `Error ${res.status}`)
      }

      if (data.already_expressed) {
        setNotice('You have already made an enquiry for this exhibit.')
      } else {
        setNotice('Your enquiry has been sent to the gallery owner.')
        localStorage.setItem(CONTACT_PREF_PROMPT_KEY, '1')
        setPrefPromptShownThisVisit(false)
      }
      closeEnquiryModal()
      load()
    } catch (err) {
      setModalError(err.message || 'Could not send enquiry. Please try again.')
    } finally {
      setSubmittingInquiry(false)
    }
  }

  const displayName = user?.username || 'Collector'

  return (
    <div className="dashboard">
      <header className="dash-topnav">
        <button className="dash-iconbtn" type="button" onClick={() => navigate('/')} aria-label="Back">
          <IconBack />
        </button>
        <span className="dash-topnav__title">Saved Exhibits</span>
        <button className="dash-avatar" type="button" onClick={() => navigate('/profile')} title="Profile" aria-label="Profile">
          {displayName.slice(0, 2).toUpperCase()}
        </button>
      </header>

      <section className="dash-greeting">
        <p className="dash-eyebrow">Welcome Back</p>
        <h1 className="dash-name">{displayName}</h1>
        <p className="dash-subtitle">Pieces you've expressed interest in</p>
      </section>

      {autoSavingInterest && <p className="dash-notice">Adding scanned artwork to your watchlist…</p>}
      {notice && <p className="dash-notice">{notice}</p>}

      <div className="dash-filters">
        {FILTERS.map((f) => (
          <button
            key={f}
            type="button"
            className={`dash-pill ${filter === f ? 'dash-pill--active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="dash-feed">
        {status === 'loading' && <p className="dash-status">Loading your collection…</p>}
        {status === 'error' && <p className="dash-status">Could not load: {error}</p>}
        {status === 'ready' && items.length === 0 && (
          <p className="dash-status">
            You haven't saved any works yet.{' '}
            <button className="dash-linkbtn" type="button" onClick={() => navigate('/')}>Browse the gallery →</button>
          </p>
        )}
        {status === 'ready' && items.length > 0 && visible.length === 0 && (
          <p className="dash-status">Nothing {filter.toLowerCase()} yet.</p>
        )}

        {visible.map((item) => (
          <article className="dash-card" key={item.id}>
            <button className="dash-card__media" type="button" onClick={() => navigate(`/exhibits/${item.id}`)}>
              <ExhibitImage exhibit={item} className="dash-card__img" />
            </button>
            <div className="dash-card__head">
              <div>
                <h2 className="dash-card__title">{item.title || item.artist}</h2>
                <p className="dash-card__artist">{item.artist}</p>
              </div>
              <button className="dash-card__arrow" type="button" onClick={() => navigate(`/exhibits/${item.id}`)} aria-label="View exhibit">
                <IconArrowRight />
              </button>
            </div>
            <span className="dash-tag">{item.status}</span>
            <div>
              {item.status === 'enquired' ? (
                <span className="dash-enquired">Enquired ✓</span>
              ) : (
                <button className="dash-enquire" type="button" onClick={() => openEnquiryModal(item)}>
                  Enquire
                </button>
              )}
            </div>
            <div className="dash-divider" />
          </article>
        ))}
      </div>

      {modalOpen && activeInquiryItem && (
        <div className="dash-modal-overlay" onClick={(event) => event.target === event.currentTarget && closeEnquiryModal()}>
          <div className="dash-modal" role="dialog" aria-modal="true" aria-label="Send enquiry to gallery">
            <h2 className="dash-modal__title">Enquire About {activeInquiryItem.title || activeInquiryItem.artist}</h2>
            <p className="dash-modal__subtitle">Tell the gallery how you would like to be contacted.</p>

            <form onSubmit={submitEnquiry}>
              <label className="dash-modal__label" htmlFor="enquiry-note">Note for the gallery</label>
              <textarea
                id="enquiry-note"
                className="dash-modal__textarea"
                rows={4}
                placeholder="Add context for your enquiry"
                value={note}
                onChange={(event) => setNote(event.target.value)}
              />

              <fieldset className="dash-modal__methods">
                <legend>Preferred contact method</legend>
                <label>
                  <input
                    type="radio"
                    name="contact-method"
                    value="email"
                    checked={contactMethod === 'email'}
                    onChange={(event) => setContactMethod(event.target.value)}
                  />
                  Email
                </label>
                <label>
                  <input
                    type="radio"
                    name="contact-method"
                    value="phone"
                    checked={contactMethod === 'phone'}
                    onChange={(event) => setContactMethod(event.target.value)}
                  />
                  Phone
                </label>
                <label>
                  <input
                    type="radio"
                    name="contact-method"
                    value="text"
                    checked={contactMethod === 'text'}
                    onChange={(event) => setContactMethod(event.target.value)}
                  />
                  Text
                </label>
              </fieldset>

              <label className="dash-modal__label" htmlFor="enquiry-email">Email</label>
              <input
                id="enquiry-email"
                className="dash-modal__input"
                type="email"
                placeholder="name@example.com"
                value={contactEmail}
                onChange={(event) => setContactEmail(event.target.value)}
              />

              <label className="dash-modal__label" htmlFor="enquiry-phone">Phone</label>
              <input
                id="enquiry-phone"
                className="dash-modal__input"
                type="text"
                placeholder="Add phone number when selecting phone or text"
                value={contactPhone}
                onChange={(event) => setContactPhone(event.target.value)}
              />

              {modalError && <p className="dash-modal__error">{modalError}</p>}

              <div className="dash-modal__actions">
                <button className="dash-modal__btn dash-modal__btn--ghost" type="button" onClick={closeEnquiryModal}>
                  Cancel
                </button>
                <button className="dash-modal__btn dash-modal__btn--primary" type="submit" disabled={submittingInquiry}>
                  {submittingInquiry ? 'Sending…' : 'Send enquiry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {prefModalOpen && (
        <div className="dash-modal-overlay" onClick={(event) => event.target === event.currentTarget && closePreferenceModal()}>
          <div className="dash-modal" role="dialog" aria-modal="true" aria-label="Save contact preference">
            <h2 className="dash-modal__title">Save Contact Preference</h2>
            <p className="dash-modal__subtitle">
              Choose how you would like gallery owners to contact you for future enquiries. You can change this any time in your profile.
            </p>

            <form onSubmit={saveContactPreference}>
              <fieldset className="dash-modal__methods">
                <legend>Preferred contact method</legend>
                <label>
                  <input
                    type="radio"
                    name="pref-method"
                    value="email"
                    checked={prefMethod === 'email'}
                    onChange={(event) => setPrefMethod(event.target.value)}
                  />
                  Email
                </label>
                <label>
                  <input
                    type="radio"
                    name="pref-method"
                    value="phone"
                    checked={prefMethod === 'phone'}
                    onChange={(event) => setPrefMethod(event.target.value)}
                  />
                  Phone
                </label>
                <label>
                  <input
                    type="radio"
                    name="pref-method"
                    value="text"
                    checked={prefMethod === 'text'}
                    onChange={(event) => setPrefMethod(event.target.value)}
                  />
                  Text
                </label>
              </fieldset>

              <label className="dash-modal__label" htmlFor="pref-email">Email</label>
              <input
                id="pref-email"
                className="dash-modal__input"
                type="email"
                placeholder="name@example.com"
                value={prefEmail}
                onChange={(event) => setPrefEmail(event.target.value)}
              />

              <label className="dash-modal__label" htmlFor="pref-phone">Phone</label>
              <input
                id="pref-phone"
                className="dash-modal__input"
                type="text"
                placeholder="Add phone number when selecting phone or text"
                value={prefPhone}
                onChange={(event) => setPrefPhone(event.target.value)}
              />

              {(prefMethod === 'phone' || prefMethod === 'text') && (
                <p className="dash-modal__hint">This phone number will be saved in your profile for future enquiries.</p>
              )}

              {prefError && <p className="dash-modal__error">{prefError}</p>}

              <div className="dash-modal__actions">
                <button className="dash-modal__btn dash-modal__btn--ghost" type="button" onClick={closePreferenceModal}>
                  Skip for now
                </button>
                <button className="dash-modal__btn dash-modal__btn--primary" type="submit" disabled={savingPreference}>
                  {savingPreference ? 'Saving…' : 'Save preference'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
