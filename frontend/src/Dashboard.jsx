import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ExhibitImage from './ExhibitImage'
import './Dashboard.css'

const FILTERS = ['All', 'Watching', 'Enquired', 'Acquired']

const IconBack = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
)
const IconArrowRight = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
)
const IconHome = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10.5 12 3l9 7.5M5 9.5V20a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9.5" /></svg>
)
const IconCompass = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2 5-5 2 2-5z" /></svg>
)
const IconBookmark = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" /></svg>
)
const IconLogout = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d="M15 4h3a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-3M10 17l-5-5 5-5M5 12h11" /></svg>
)

function Dashboard() {
  const navigate = useNavigate()
  const { user, authFetch, logout } = useAuth()
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('All')

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

  const visible = filter === 'All' ? items : items.filter((it) => it.status === filter.toLowerCase())

  const enquire = (id) => {
    authFetch('/api/inquiries/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exhibit: id }),
    }).then((res) => {
      if (res.ok) load()
    })
  }

  const doLogout = () => {
    logout()
    navigate('/')
  }

  const displayName = user?.username || 'Collector'

  return (
    <div className="dashboard">
      <header className="dash-topnav">
        <button className="dash-iconbtn" type="button" onClick={() => navigate('/')} aria-label="Back">
          <IconBack />
        </button>
        <span className="dash-topnav__title">Saved Exhibits</span>
        <button className="dash-avatar" type="button" onClick={doLogout} title="Log out" aria-label="Log out">
          {displayName.slice(0, 2).toUpperCase()}
        </button>
      </header>

      <section className="dash-greeting">
        <p className="dash-eyebrow">Welcome Back</p>
        <h1 className="dash-name">{displayName}</h1>
        <p className="dash-subtitle">Pieces you've expressed interest in</p>
      </section>

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
                <button className="dash-enquire" type="button" onClick={() => enquire(item.id)}>
                  Enquire
                </button>
              )}
            </div>
            <div className="dash-divider" />
          </article>
        ))}
      </div>

      <nav className="dash-bottomnav">
        <button className="dash-contact" type="button" onClick={() => navigate('/')}>
          Contact Gallery
        </button>
        <div className="dash-navpill">
          <button className="dash-navitem dash-navitem--active" type="button" onClick={() => navigate('/')} aria-label="Home"><IconHome /></button>
          <button className="dash-navitem" type="button" onClick={() => navigate('/')} aria-label="Explore"><IconCompass /></button>
          <button className="dash-navitem" type="button" aria-label="Saved"><IconBookmark /></button>
          <button className="dash-navitem" type="button" onClick={doLogout} aria-label="Log out"><IconLogout /></button>
        </div>
      </nav>
    </div>
  )
}

export default Dashboard
