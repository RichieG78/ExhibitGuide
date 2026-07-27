import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ExhibitImage from './ExhibitImage'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fetches all exhibits and shows them as a grid of cards.
// Each card links to that exhibit's detail page at /exhibits/:id.
function ExhibitList() {
  const [exhibits, setExhibits] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')

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
        <p className="list-sub">{exhibits.length} works · served live from the Django REST API</p>
        <div className="list-links">
          <Link to="/scan" className="list-scan-link">Enter the gallery — scan experience →</Link>
          <Link to="/dashboard" className="list-scan-link">Saved exhibits (member view) →</Link>
        </div>
      </header>
      <ul className="exhibit-grid">
        {exhibits.map((exhibit) => (
          <li key={exhibit.id} className="exhibit-card">
            <Link to={`/exhibits/${exhibit.id}`} className="exhibit-link">
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
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  )
}

export default ExhibitList
