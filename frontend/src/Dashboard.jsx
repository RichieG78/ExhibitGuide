import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ExhibitImage from './ExhibitImage'
import InterestModal from './InterestModal'
import './Dashboard.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Demo only: this screen is a logged-in collector's watchlist. Until auth +
// per-user saved-exhibit APIs exist (Phase 7), we feature real exhibits with
// simulated statuses and a demo collector name.
const DEMO_USER = 'Alastair Hargreaves'
const FILTERS = ['All', 'Watching', 'Enquired', 'Acquired']
const STATUS_CYCLE = ['Watching', 'Enquired', 'Watching', 'Acquired']

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
const IconUser = () => (
  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="4" /><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" /></svg>
)

function Dashboard() {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('All')
  const [modalExhibit, setModalExhibit] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/exhibits/`)
      .then((response) => {
        if (!response.ok) throw new Error(`API responded with ${response.status}`)
        return response.json()
      })
      .then((data) => {
        setItems(
          data.map((exhibit, i) => ({
            ...exhibit,
            demoStatus: STATUS_CYCLE[i % STATUS_CYCLE.length],
          }))
        )
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [])

  const visible =
    filter === 'All' ? items : items.filter((it) => it.demoStatus === filter)

  const markEnquired = (id) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, demoStatus: 'Enquired' } : it))
    )
  }

  return (
    <div className="dashboard">
      {/* Top nav */}
      <header className="dash-topnav">
        <button className="dash-iconbtn" type="button" onClick={() => navigate('/')} aria-label="Back">
          <IconBack />
        </button>
        <span className="dash-topnav__title">Saved Exhibits</span>
        <span className="dash-avatar" aria-hidden="true">
          {DEMO_USER.split(' ').map((w) => w[0]).join('')}
        </span>
      </header>

      {/* Greeting */}
      <section className="dash-greeting">
        <p className="dash-eyebrow">Welcome Back</p>
        <h1 className="dash-name">{DEMO_USER}</h1>
        <p className="dash-subtitle">Pieces you've expressed interest in</p>
      </section>

      {/* Filters */}
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

      {/* Feed */}
      <div className="dash-feed">
        {status === 'loading' && <p className="dash-status">Loading your collection…</p>}
        {status === 'error' && <p className="dash-status">Could not load: {error}</p>}
        {status === 'ready' && visible.length === 0 && (
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
            <span className="dash-tag">{item.demoStatus}</span>
            <div>
              <button className="dash-enquire" type="button" onClick={() => setModalExhibit(item)}>
                Enquire
              </button>
            </div>
            <div className="dash-divider" />
          </article>
        ))}
      </div>

      {/* Bottom nav */}
      <nav className="dash-bottomnav">
        <button className="dash-contact" type="button" onClick={() => setModalExhibit(items[0] || null)}>
          Contact Gallery
        </button>
        <div className="dash-navpill">
          <button className="dash-navitem dash-navitem--active" type="button" onClick={() => navigate('/')} aria-label="Home"><IconHome /></button>
          <button className="dash-navitem" type="button" aria-label="Explore"><IconCompass /></button>
          <button className="dash-navitem" type="button" aria-label="Saved"><IconBookmark /></button>
          <button className="dash-navitem" type="button" aria-label="Profile"><IconUser /></button>
        </div>
      </nav>

      {modalExhibit && (
        <InterestModal
          exhibit={modalExhibit}
          dwellStart={null}
          onClose={() => setModalExhibit(null)}
          onSuccess={() => {
            markEnquired(modalExhibit.id)
            setModalExhibit(null)
          }}
        />
      )}
    </div>
  )
}

export default Dashboard
