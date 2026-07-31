import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import ExhibitImage from './ExhibitImage'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fetches all exhibits and shows them as a grid of cards.
// Each card links to that exhibit's detail page at /exhibits/:id.
function ExhibitList() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [exhibits, setExhibits] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  useEffect(() => {
    fetch(`${API_BASE}/api/exhibits/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API responded with ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        setExhibits(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [])

  if (status === 'loading') {
    return <main className="page"><p>Loading exhibits…</p></main>
  }
  if (status === 'error') {
    return <main className="page"><p className="error">Could not load exhibits: {error}</p></main>
  }

  return (
    <main className="page">
      <header className="list-header">
        <h1 className="list-title">ExhibitGuide</h1>
        <p className="list-sub">Start here: scan a code, open a work, and follow the visitor journey end-to-end.</p>

        <nav className="list-topnav" aria-label="Primary actions">
          <Link to="/scan" className="list-topnav__btn">Enter the gallery</Link>
          {!user && (
            <>
              <Link to="/login" className="list-topnav__btn">Member sign in</Link>
              <Link to="/register" className="list-topnav__btn">Create collector account</Link>
            </>
          )}
          {user && (
            <button type="button" className="list-topnav__btn" onClick={handleLogout}>Log out</button>
          )}
          <a href="/exhibit-qr-codes.html" className="list-topnav__btn">Printable QR code sheet</a>
        </nav>

        <section className="list-howto" aria-label="How to try ExhibitGuide">
          <h2 className="list-howto__title">How to try it</h2>
          <ol className="list-howto__steps">
            <li>
              <strong>Open your phone camera</strong>
              <span>Any modern iPhone or Android camera can read QR codes directly.</span>
            </li>
            <li>
              <strong>Scan a code from a wall label</strong>
              <span>Use the QR links below or the printable sheet to simulate gallery labels.</span>
            </li>
            <li>
              <strong>Read, listen, and watch from the artwork page</strong>
              <span>No account is required to consume content.</span>
            </li>
            <li>
              <strong>Express interest to notify the gallery</strong>
              <span>Then continue to dashboard to see scans, enquiries, and follow-up signals.</span>
            </li>
          </ol>
        </section>

        <div className="list-links">
          {user ? (
            <>
              <Link to="/dashboard" className="list-scan-link">My dashboard →</Link>
              <Link to="/profile" className="list-scan-link">My profile →</Link>
            </>
          ) : null}
          {user?.is_staff && (
            <Link to="/manage" className="list-scan-link">Manage exhibits (staff) →</Link>
          )}
        </div>
      </header>
      <ul className="exhibit-grid">
        {exhibits.map((exhibit) => (
          <li key={exhibit.id} className="exhibit-card">
            <Link to={exhibit.qr_identifier ? `/qr/${exhibit.qr_identifier}` : `/exhibits/${exhibit.id}`} className="exhibit-link">
              <ExhibitImage exhibit={exhibit} className="exhibit-image" />
              <div className="exhibit-body">
                <h2 className="exhibit-title">{exhibit.artist || 'Unknown artist'}</h2>
                <p className="exhibit-show">{exhibit.show_name}</p>
                <p className="exhibit-tldr">{exhibit.tldr}</p>
                <p className="exhibit-price">
                  {exhibit.price
                    ? `${exhibit.currency} ${exhibit.price.toLocaleString()}`
                    : 'Price on request'}
                </p>

                {exhibit.qr_identifier && (
                  <div className="exhibit-qr" aria-label={`QR ${exhibit.qr_identifier} for ${exhibit.title || exhibit.artist || 'this exhibit'}`}>
                    <img
                      className="exhibit-qr__img"
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&margin=0&data=${encodeURIComponent(`${window.location.origin}/qr/${exhibit.qr_identifier}`)}`}
                      alt={`QR code for ${exhibit.title || exhibit.artist || 'exhibit'}`}
                      loading="lazy"
                    />
                    <span className="exhibit-qr__hint">Scan this code or tap this card to open</span>
                  </div>
                )}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  )
}

export default ExhibitList
