import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ExhibitImage from './ExhibitImage'
import InterestModal from './InterestModal'
import './ExhibitDetail.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fixed waveform bar heights (decorative), matching the Figma rhythm.
const WAVEFORM = [
  28, 44, 62, 55, 38, 72, 50, 30, 58, 68, 40, 52, 76, 60, 32, 42, 66, 50, 56,
  38, 30, 64, 48, 54,
]

/* — Inline UI icons (generic chrome; stroke uses currentColor) — */
const IconBack = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>
)
const IconShare = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v13M8 7l4-4 4 4M4 14v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5" /></svg>
)
const IconHeadphones = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M3 14v-2a9 9 0 0 1 18 0v2" /><rect x="3" y="14" width="4" height="7" rx="1.5" /><rect x="17" y="14" width="4" height="7" rx="1.5" /></svg>
)
const IconDoc = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" /><path d="M14 3v6h6M9 13h6M9 17h6" /></svg>
)
const IconVideo = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="6" width="13" height="12" rx="2" /><path d="m16 10 5-3v10l-5-3" /></svg>
)
const IconPlay = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5.5v13l11-6.5z" /></svg>
)
const IconPause = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M7 5h3v14H7zM14 5h3v14h-3z" /></svg>
)
const IconPlus = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 5v14M5 12h14" /></svg>
)
const IconCheck = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
)

function formatTime(seconds) {
  if (!seconds || Number.isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function ExhibitDetail({ id, qrId }) {
  const { user, authFetch } = useAuth()
  const [exhibit, setExhibit] = useState(null)
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')
  const [tab, setTab] = useState('listen') // 'listen' | 'read' | 'watch'
  const [playing, setPlaying] = useState(false)
  const [current, setCurrent] = useState(0)
  const [duration, setDuration] = useState(0)
  const [notice, setNotice] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [saved, setSaved] = useState(false)
  const [dwellStart] = useState(() => Date.now()) // for the dwell_time metric
  const audioRef = useRef(null)

  useEffect(() => {
    setStatus('loading')
    // Scanned QR codes resolve by printed identifier; everything else by id.
    const endpoint = qrId
      ? `${API_BASE}/api/exhibits/qr/${qrId}/`
      : `${API_BASE}/api/exhibits/${id}/`
    fetch(endpoint)
      .then((response) => {
        if (!response.ok) throw new Error(`API responded with ${response.status}`)
        return response.json()
      })
      .then((data) => {
        setExhibit(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id, qrId])

  if (status === 'loading') {
    return <div className="detail-screen"><p className="detail-status">Loading exhibit…</p></div>
  }
  if (status === 'error') {
    return (
      <div className="detail-screen">
        <p className="detail-status detail-error">Could not load exhibit: {error}</p>
      </div>
    )
  }

  const year = exhibit.publish_date ? new Date(exhibit.publish_date).getFullYear() : null
  const dimensions =
    exhibit.dimensions_height && exhibit.dimensions_width
      ? `${exhibit.dimensions_height} × ${exhibit.dimensions_width} cm`
      : null
  const metaLine = [exhibit.medium, dimensions, year].filter(Boolean).join(' · ')

  const togglePlay = () => {
    const el = audioRef.current
    if (!el) return
    if (el.paused) {
      el.play()
      setPlaying(true)
    } else {
      el.pause()
      setPlaying(false)
    }
  }

  const saveToWatchlist = () => {
    authFetch('/api/saved/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exhibit: exhibit.id }),
    }).then((res) => {
      if (res.ok) setSaved(true)
    })
  }

  return (
    <div className="detail-screen">
      {/* Header */}
      <header className="detail-header">
        <Link to="/" className="detail-icon-btn" aria-label="Back to all exhibits">
          <IconBack />
        </Link>
        <span className="detail-header__title">{exhibit.gallery_name || 'ExhibitGuide'}</span>
        <button className="detail-icon-btn" type="button" aria-label="Share" onClick={() => setNotice('Sharing is coming in a later phase.')}>
          <IconShare />
        </button>
      </header>

      {submitted && (
        <div className="detail-banner" role="status">
          <IconCheck />
          Your interest has been noted — {exhibit.gallery_name || 'the gallery'} will be in touch.
        </div>
      )}

      {/* Hero */}
      <section className="detail-hero">
        <ExhibitImage exhibit={exhibit} className="detail-hero__img" />
        <div className="detail-hero__scrim" />
        {exhibit.show_name && <p className="detail-hero__eyebrow">{exhibit.show_name}</p>}
        <div className="detail-hero__caption">
          {exhibit.artist && <p className="detail-hero__artist">{exhibit.artist}</p>}
          <h1 className="detail-hero__title">{exhibit.title || exhibit.artist || 'Untitled'}</h1>
          {metaLine && <p className="detail-hero__meta">{metaLine}</p>}
        </div>
      </section>

      {/* Body */}
      <div className="detail-body">
        {/* Tabs */}
        <div className="tabs" role="tablist">
          <button className={`tab ${tab === 'listen' ? 'tab--active' : ''}`} onClick={() => setTab('listen')} type="button">
            <IconHeadphones /> Listen
          </button>
          <button className={`tab ${tab === 'read' ? 'tab--active' : ''}`} onClick={() => setTab('read')} type="button">
            <IconDoc /> Read
          </button>
          <button className={`tab ${tab === 'watch' ? 'tab--active' : ''}`} onClick={() => setTab('watch')} type="button">
            <IconVideo /> Watch
          </button>
        </div>

        {/* Tab panels */}
        {tab === 'listen' && (
          <div className="audio-card">
            <div className="audio-card__row">
              <button className="audio-play" type="button" onClick={togglePlay} aria-label={playing ? 'Pause' : 'Play'} disabled={!exhibit.audio_url}>
                {playing ? <IconPause /> : <IconPlay />}
              </button>
              <div className="waveform" aria-hidden="true">
                {WAVEFORM.map((h, i) => (
                  <span key={i} className="waveform__bar" style={{ height: `${h}px` }} />
                ))}
              </div>
            </div>
            <div className="audio-times">
              <span>{formatTime(current)}</span>
              <span>{formatTime(duration)}</span>
            </div>
            <p className="audio-label">Artist's Statement — Audio</p>
            {exhibit.tldr && <p className="audio-text">{exhibit.tldr}</p>}
            {exhibit.audio_url && (
              <audio
                ref={audioRef}
                src={exhibit.audio_url}
                onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
                onTimeUpdate={(e) => setCurrent(e.currentTarget.currentTime)}
                onEnded={() => setPlaying(false)}
                preload="metadata"
              />
            )}
          </div>
        )}

        {tab === 'read' && (
          <div className="panel-card">
            <p className="panel-label">About the work</p>
            <p className="panel-text">{exhibit.full_text || 'No description available.'}</p>
          </div>
        )}

        {tab === 'watch' && (
          <div className="panel-card">
            <p className="panel-label">Film</p>
            {exhibit.video_url ? (
              <a className="watch-link" href={exhibit.video_url} target="_blank" rel="noreferrer">
                <IconVideo /> Watch the film
              </a>
            ) : (
              <p className="panel-text">No video available for this work.</p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="detail-actions">
          <button className="btn-primary" type="button" onClick={() => setShowModal(true)}>
            <span>Express Interest in Purchasing</span>
            <IconPlus />
          </button>
          <button className="btn-secondary" type="button" onClick={() => setNotice('Price list requests open in a later phase.')}>
            Request Price List
          </button>
          {user &&
            (saved ? (
              <Link to="/dashboard" className="btn-secondary detail-saved-link">
                ✓ Saved — view your collection
              </Link>
            ) : (
              <button className="btn-secondary" type="button" onClick={saveToWatchlist}>
                + Save to watchlist
              </button>
            ))}
          {notice && <p className="detail-notice">{notice}</p>}
        </div>

        {/* Gallery Director's Note */}
        {exhibit.provenance && (
          <div className="director-note">
            <div className="director-note__avatar" aria-hidden="true">
              {(exhibit.gallery_name || 'G').charAt(0)}
            </div>
            <div>
              <p className="director-note__label">Gallery Director's Note</p>
              <p className="director-note__quote">“{exhibit.provenance}”</p>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <InterestModal
          exhibit={exhibit}
          dwellStart={dwellStart}
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setSubmitted(true)
            setShowModal(false)
          }}
        />
      )}
    </div>
  )
}

export default ExhibitDetail
