import { useEffect, useState } from 'react'
import './App.css'

// Base URL of the Django REST API. Uses a Vite environment variable if one is
// set (handy for production), otherwise falls back to the local dev server.
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [exhibits, setExhibits] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')

  // Fetch the exhibits from the Django API once, when the component first mounts.
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
    return (
      <main className="page">
        <p>Loading exhibits…</p>
      </main>
    )
  }

  if (status === 'error') {
    return (
      <main className="page">
        <h1>ExhibitGuide</h1>
        <p className="error">Could not load exhibits: {error}</p>
        <p>Is the Django API running at {API_BASE}?</p>
      </main>
    )
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>ExhibitGuide</h1>
        <p>{exhibits.length} exhibits · served live from the Django REST API</p>
      </header>

      <ul className="exhibit-grid">
        {exhibits.map((exhibit) => (
          <li key={exhibit.id} className="exhibit-card">
            <img
              className="exhibit-image"
              src={exhibit.image_url || exhibit.image}
              alt={exhibit.artist || 'Exhibit'}
            />
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
          </li>
        ))}
      </ul>
    </main>
  )
}

export default App
