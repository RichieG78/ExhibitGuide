import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ExhibitImage from './ExhibitImage'
import './Dashboard.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const PENDING_INTEREST_KEY = 'eg_interest_exhibit_id'
const CONTACT_PREF_PROMPT_KEY = 'eg_contact_pref_prompt'
const FILTERS = ['Your scans', 'Enquired', 'Shows', 'Acquired']

function normalizeStatus(rawStatus) {
  if (rawStatus === 'prospect') return 'prospect'
  if (rawStatus === 'lead' || rawStatus === 'enquired') return 'lead'
  if (rawStatus === 'acquired') return 'acquired'
  return 'watching'
}

function statusLabel(status) {
  if (status === 'prospect') return 'Enquired'
  if (status === 'lead') return 'Interest Notified to Gallery'
  if (status === 'acquired') return 'Acquired'
  return 'Saved'
}

function isContactPreferenceComplete(profile) {
  const method = (profile?.preferred_contact_method || '').trim()
  const email = (profile?.email || '').trim()
  const phone = (profile?.phone || '').trim()

  if (!method) return false
  if (method === 'email') return Boolean(email)
  if (method === 'phone' || method === 'text') return Boolean(phone)
  return false
}

function hasProfileName(profile) {
  return Boolean((profile?.first_name || '').trim() && (profile?.last_name || '').trim())
}

const IconBack = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
)
const IconLogout = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><path d="M16 17l5-5-5-5" /><path d="M21 12H9" /></svg>
)

function Dashboard() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, authFetch, logout } = useAuth()
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [filter, setFilter] = useState('Your scans')
  const [showFilter, setShowFilter] = useState('All shows')
  const [contactMethod, setContactMethod] = useState('email')
  const [contactFirstName, setContactFirstName] = useState('')
  const [contactLastName, setContactLastName] = useState('')
  const [contactEmail, setContactEmail] = useState('')
  const [contactPhone, setContactPhone] = useState('')
  const [note, setNote] = useState('')
  const [modalError, setModalError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [activeInquiryItem, setActiveInquiryItem] = useState(null)
  const [submittingInquiry, setSubmittingInquiry] = useState(false)
  const [profileData, setProfileData] = useState({
    email: '',
    phone: '',
    preferred_contact_method: '',
    first_name: '',
    last_name: '',
  })
  const [profileLoaded, setProfileLoaded] = useState(false)
  const [autoSavingInterest, setAutoSavingInterest] = useState(false)
  const [prefModalOpen, setPrefModalOpen] = useState(false)
  const [prefMethod, setPrefMethod] = useState('email')
  const [prefEmail, setPrefEmail] = useState('')
  const [prefPhone, setPrefPhone] = useState('')
  const [prefError, setPrefError] = useState('')
  const [savingPreference, setSavingPreference] = useState(false)
  const [prefPromptShownThisVisit, setPrefPromptShownThisVisit] = useState(false)
  const autoSavedRef = useRef(false)
  const enquiryModalRef = useRef(null)
  const preferenceModalRef = useRef(null)
  const modalReturnFocusRef = useRef(null)

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
        setProfileData({
          email: data.email || '',
          phone: data.phone || '',
          preferred_contact_method: data.preferred_contact_method || '',
          first_name: data.first_name || '',
          last_name: data.last_name || '',
        })
        setContactEmail(data.email || '')
        setPrefEmail(data.email || '')
        setPrefPhone(data.phone || '')
      })
      .catch(() => {
        // Non-blocking for dashboard render.
      })
      .finally(() => setProfileLoaded(true))
  }, [authFetch])

  useEffect(() => {
    if (!profileLoaded) return
    const shouldPrompt = localStorage.getItem(CONTACT_PREF_PROMPT_KEY) === '1'
    const hasCompletedPreference = isContactPreferenceComplete(profileData)
    if (!shouldPrompt || hasCompletedPreference || prefModalOpen || modalOpen || prefPromptShownThisVisit) return

    setPrefMethod(profileData.preferred_contact_method || (profileData.phone ? 'phone' : 'email'))
    setPrefEmail(profileData.email || user?.email || '')
    setPrefPhone(profileData.phone || '')
    setPrefError('')
    setPrefModalOpen(true)
    setPrefPromptShownThisVisit(true)
  }, [prefModalOpen, modalOpen, profileData, user, prefPromptShownThisVisit, profileLoaded])

  useEffect(() => {
    if (!interestExhibitId || autoSavedRef.current || status !== 'ready') return
    const alreadyInWatchlist = items.some(
      (item) => String(item.id) === String(interestExhibitId) && normalizeStatus(item.status) === 'watching'
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
        setNotice('The scanned artwork has been added to your scans.')
        return load()
      })
      .catch(() => {
        setNotice('Could not auto-add the scanned artwork. Please try again.')
      })
      .finally(() => setAutoSavingInterest(false))
  }, [interestExhibitId, status, items, authFetch, load])

  useEffect(() => {
    if (!modalOpen && !prefModalOpen) return

    const activeModal = modalOpen ? enquiryModalRef.current : preferenceModalRef.current
    if (!activeModal) return

    modalReturnFocusRef.current = document.activeElement
    const frame = window.requestAnimationFrame(() => {
      const firstField = activeModal.querySelector('input, textarea, button, [href], [tabindex]:not([tabindex="-1"])')
      firstField?.focus()
    })

    const onKeyDown = (event) => {
      const currentModal = modalOpen ? enquiryModalRef.current : preferenceModalRef.current
      if (!currentModal) return

      if (event.key === 'Escape') {
        event.preventDefault()
        if (modalOpen) {
          closeEnquiryModal()
        } else {
          closePreferenceModal()
        }
        return
      }

      if (event.key !== 'Tab') return

      const focusable = currentModal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const nodes = Array.from(focusable).filter((node) => !node.disabled && node.getAttribute('aria-hidden') !== 'true')
      if (nodes.length === 0) return

      const first = nodes[0]
      const last = nodes[nodes.length - 1]
      const active = document.activeElement

      if (event.shiftKey && active === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && active === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown)
    return () => {
      window.cancelAnimationFrame(frame)
      document.removeEventListener('keydown', onKeyDown)
      if (modalReturnFocusRef.current && typeof modalReturnFocusRef.current.focus === 'function') {
        modalReturnFocusRef.current.focus()
      }
    }
  }, [modalOpen, prefModalOpen])

  const showOptions = useMemo(() => {
    const names = Array.from(new Set(items.map((item) => item.show_name).filter(Boolean)))
    names.sort((a, b) => a.localeCompare(b))
    return ['All shows', ...names]
  }, [items])

  const visible = useMemo(() => {
    if (filter === 'Your scans') {
      return items.filter((item) => {
        const state = normalizeStatus(item.status)
        return state === 'watching' || state === 'lead' || state === 'prospect'
      })
    }

    if (filter === 'Enquired') {
      return items.filter((item) => {
        const state = normalizeStatus(item.status)
        return state === 'lead' || state === 'prospect'
      })
    }

    if (filter === 'Acquired') {
      return items.filter((item) => normalizeStatus(item.status) === 'acquired')
    }

    if (filter === 'Shows' && showFilter !== 'All shows') {
      return items.filter((item) => item.show_name === showFilter)
    }

    return items
  }, [filter, items, showFilter])

  const openEnquiryModal = (item) => {
    if (prefModalOpen) return
    setActiveInquiryItem(item)
    setContactMethod(profileData.preferred_contact_method || 'email')
    setContactFirstName(profileData.first_name || '')
    setContactLastName(profileData.last_name || '')
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
      payload.preferred_contact_method = prefMethod
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
        preferred_contact_method: data.preferred_contact_method || prefMethod,
      })
      setContactEmail(data.email || email)
      setContactPhone(data.phone || phone)
      setContactMethod(data.preferred_contact_method || prefMethod)
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
    const cleanFirstName = (contactFirstName || '').trim()
    const cleanLastName = (contactLastName || '').trim()
    const profileEmail = (profileData.email || user?.email || '').trim()
    const profilePhone = (profileData.phone || '').trim()
    const profileFirstName = (profileData.first_name || '').trim()
    const profileLastName = (profileData.last_name || '').trim()
    const resolvedEmail = cleanEmail || profileEmail
    const resolvedPhone = cleanPhone || profilePhone
    const resolvedFirstName = cleanFirstName || profileFirstName
    const resolvedLastName = cleanLastName || profileLastName
    if (!resolvedFirstName) {
      setModalError('Please add your first name to continue.')
      return
    }
    if (!resolvedLastName) {
      setModalError('Please add your last name to continue.')
      return
    }

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
      const profilePayload = {
        first_name: resolvedFirstName,
        last_name: resolvedLastName,
        preferred_contact_method: contactMethod,
      }
      if (resolvedEmail) {
        profilePayload.email = resolvedEmail
      }
      if (resolvedPhone) {
        profilePayload.phone = resolvedPhone
      }

      const profileRes = await authFetch('/api/auth/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profilePayload),
      })
      const profileUpdate = await profileRes.json().catch(() => ({}))
      if (!profileRes.ok) {
        throw new Error(
          profileUpdate.detail ||
          profileUpdate.first_name?.[0] ||
          profileUpdate.last_name?.[0] ||
          profileUpdate.email?.[0] ||
          profileUpdate.phone?.[0] ||
          profileUpdate.preferred_contact_method?.[0] ||
          'Could not save your details to profile. Please try again.'
        )
      }

      setProfileData((prev) => ({
        ...prev,
        email: profileUpdate.email || resolvedEmail,
        phone: profileUpdate.phone || resolvedPhone,
        preferred_contact_method: profileUpdate.preferred_contact_method || contactMethod,
        first_name: profileUpdate.first_name || resolvedFirstName,
        last_name: profileUpdate.last_name || resolvedLastName,
      }))

      const methodLabel = contactMethod === 'text' ? 'Text message' : contactMethod[0].toUpperCase() + contactMethod.slice(1)
      const messageLines = []
      if (note.trim()) messageLines.push(note.trim())
      messageLines.push(`Name: ${resolvedFirstName} ${resolvedLastName}`.trim())
      messageLines.push(`Preferred contact method: ${methodLabel}`)
      if (resolvedEmail) messageLines.push(`Email: ${resolvedEmail}`)
      if (resolvedPhone) messageLines.push(`Phone: ${resolvedPhone}`)

      const res = await authFetch('/api/inquiries/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exhibit: activeInquiryItem.id,
          purchase_intent: true,
          message: messageLines.join('\n\n'),
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data.detail || `Error ${res.status}`)
      }

      if (data.upgraded_to_prospect) {
        setNotice('Purchase enquiry sent. Your interest has been flagged for gallery follow-up.')
      } else if (data.already_expressed) {
        setNotice('You have already made an enquiry for this exhibit.')
      } else {
        setNotice('Your purchase enquiry has been sent to the gallery owner.')
        if (!isContactPreferenceComplete(profileData)) {
          localStorage.setItem(CONTACT_PREF_PROMPT_KEY, '1')
          setPrefPromptShownThisVisit(false)
        }
      }
      closeEnquiryModal()
      load()
    } catch (err) {
      setModalError(err.message || 'Could not send enquiry. Please try again.')
    } finally {
      setSubmittingInquiry(false)
    }
  }

  const profileFirstName = (profileData.first_name || '').trim()
  const displayName = profileFirstName || user?.username || 'Collector'
  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1)
      return
    }
    navigate('/')
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="dashboard">
      <header className="dash-topnav">
        <button className="dash-iconbtn" type="button" onClick={handleBack} aria-label="Back">
          <IconBack />
        </button>
        <span className="dash-topnav__title">Saved Exhibits</span>
        <div className="dash-topnav__right">
          <button className="dash-avatar" type="button" onClick={() => navigate('/profile')} title="Profile" aria-label="Profile">
            {displayName.slice(0, 2).toUpperCase()}
          </button>
          <button className="dash-iconbtn dash-iconbtn--logout" type="button" onClick={handleLogout} aria-label="Log out">
            <IconLogout />
          </button>
        </div>
      </header>

      <section className="dash-greeting">
        <p className="dash-eyebrow">Welcome Back</p>
        <h1 className="dash-name">{displayName}</h1>
        <p className="dash-subtitle">Your scan history appears here. Enquire on any artwork to notify the gallery.</p>
      </section>

      {autoSavingInterest && <p className="dash-notice" role="status" aria-live="polite">Adding scanned artwork to your watchlist…</p>}
      {notice && <p className="dash-notice" role="status" aria-live="polite">{notice}</p>}

      <div className="dash-filters">
        {FILTERS.map((f) => (
          <button
            key={f}
            type="button"
            className={`dash-pill ${filter === f ? 'dash-pill--active' : ''}`}
            onClick={() => {
              setFilter(f)
              if (f !== 'Shows') setShowFilter('All shows')
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {filter === 'Shows' && (
        <div className="dash-filters dash-filters--sub">
          {showOptions.map((name) => (
            <button
              key={name}
              type="button"
              className={`dash-pill ${showFilter === name ? 'dash-pill--active' : ''}`}
              onClick={() => setShowFilter(name)}
            >
              {name}
            </button>
          ))}
        </div>
      )}

      <div className="dash-feed">
        {status === 'loading' && <p className="dash-status" role="status" aria-live="polite">Loading your collection…</p>}
        {status === 'error' && <p className="dash-status" role="alert">Could not load: {error}</p>}
        {status === 'ready' && items.length === 0 && (
          <p className="dash-status">
            You haven't saved any works yet.{' '}
            <button className="dash-linkbtn" type="button" onClick={() => navigate('/')}>Browse the gallery →</button>
          </p>
        )}
        {status === 'ready' && items.length > 0 && visible.length === 0 && (
          <p className="dash-status">
            {filter === 'Shows' && showFilter !== 'All shows'
              ? `No scans in ${showFilter} yet.`
              : filter === 'Enquired'
                ? 'No enquiries yet. Use Enquire about purchasing on a scanned artwork.'
                : `Nothing ${filter.toLowerCase()} yet.`}
          </p>
        )}

        {visible.map((item) => {
          const currentStatus = normalizeStatus(item.status)
          return (
          <article className="dash-card" key={item.id}>
            <button className="dash-card__media" type="button" onClick={() => navigate(`/exhibits/${item.id}`)}>
              <ExhibitImage exhibit={item} className="dash-card__img" />
            </button>
            <div className="dash-card__head">
              <div>
                <h2 className="dash-card__title">{item.title || item.artist}</h2>
                <p className="dash-card__artist">{item.artist}</p>
              </div>
            </div>
            <span className="dash-tag">{statusLabel(currentStatus)}</span>
            <div>
              {currentStatus === 'prospect' ? (
                <span className="dash-prospect">Enquired ✓ Gallery notified</span>
              ) : currentStatus === 'lead' || currentStatus === 'watching' ? (
                <button className="dash-enquire" type="button" onClick={() => openEnquiryModal(item)}>
                  Enquire about purchasing
                </button>
              ) : (
                <span className="dash-enquired">Acquired ✓</span>
              )}
            </div>
            <div className="dash-divider" />
          </article>
          )
        })}
      </div>

      {modalOpen && activeInquiryItem && (
        <div className="dash-modal-overlay" onClick={(event) => event.target === event.currentTarget && closeEnquiryModal()}>
          <div
            ref={enquiryModalRef}
            className="dash-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="enquiry-modal-title"
          >
            <h2 id="enquiry-modal-title" className="dash-modal__title">Enquire About {activeInquiryItem.title || activeInquiryItem.artist}</h2>
            <p className="dash-modal__subtitle">Signal purchase intent and tell the gallery how you would like to be contacted.</p>

            <form onSubmit={submitEnquiry}>
              {!hasProfileName(profileData) && (
                <>
                  <label className="dash-modal__label" htmlFor="enquiry-first-name">First name</label>
                  <input
                    id="enquiry-first-name"
                    className="dash-modal__input"
                    type="text"
                    placeholder="First name"
                    value={contactFirstName}
                    onChange={(event) => setContactFirstName(event.target.value)}
                    required
                  />

                  <label className="dash-modal__label" htmlFor="enquiry-last-name">Last name</label>
                  <input
                    id="enquiry-last-name"
                    className="dash-modal__input"
                    type="text"
                    placeholder="Last name"
                    value={contactLastName}
                    onChange={(event) => setContactLastName(event.target.value)}
                    required
                  />
                </>
              )}

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
                aria-invalid={Boolean(modalError)}
                aria-describedby={modalError ? 'enquiry-modal-error' : undefined}
              />

              <label className="dash-modal__label" htmlFor="enquiry-phone">Phone</label>
              <input
                id="enquiry-phone"
                className="dash-modal__input"
                type="text"
                placeholder="Add phone number when selecting phone or text"
                value={contactPhone}
                onChange={(event) => setContactPhone(event.target.value)}
                aria-invalid={Boolean(modalError)}
                aria-describedby={modalError ? 'enquiry-modal-error' : undefined}
              />

              {modalError && (
                <p id="enquiry-modal-error" className="dash-modal__error" role="alert" aria-live="assertive">
                  {modalError}
                </p>
              )}

              <div className="dash-modal__actions">
                <button className="dash-modal__btn dash-modal__btn--ghost" type="button" onClick={closeEnquiryModal}>
                  Cancel
                </button>
                <button className="dash-modal__btn dash-modal__btn--primary" type="submit" disabled={submittingInquiry}>
                  {submittingInquiry ? 'Sending…' : 'Send purchase enquiry'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {prefModalOpen && (
        <div className="dash-modal-overlay" onClick={(event) => event.target === event.currentTarget && closePreferenceModal()}>
          <div
            ref={preferenceModalRef}
            className="dash-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="preference-modal-title"
          >
            <h2 id="preference-modal-title" className="dash-modal__title">Save Contact Preference</h2>
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
                aria-invalid={Boolean(prefError)}
                aria-describedby={prefError ? 'pref-modal-error' : undefined}
              />

              <label className="dash-modal__label" htmlFor="pref-phone">Phone</label>
              <input
                id="pref-phone"
                className="dash-modal__input"
                type="text"
                placeholder="Add phone number when selecting phone or text"
                value={prefPhone}
                onChange={(event) => setPrefPhone(event.target.value)}
                aria-invalid={Boolean(prefError)}
                aria-describedby={prefError ? 'pref-modal-error' : undefined}
              />

              {(prefMethod === 'phone' || prefMethod === 'text') && (
                <p className="dash-modal__hint">This phone number will be saved in your profile for future enquiries.</p>
              )}

              {prefError && (
                <p id="pref-modal-error" className="dash-modal__error" role="alert" aria-live="assertive">
                  {prefError}
                </p>
              )}

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
