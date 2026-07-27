import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

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
    return <p>Loading exhibits…</p>
  }
  if (status === 'error') {
    return <p className="error">Could not load exhibits: {error}</p>
  }

  return (
    <>
      <p className="list-count">{exhibits.length} exhibits</p>
      <ul className="exhibit-grid">
        {exhibits.map((exhibit) => (
          <li key={exhibit.id} className="exhibit-card">
            <Link to={`/exhibits/${exhibit.id}`} className="exhibit-link">
              <img
                className="exhibit-image"
                src={exhibit.image_url || exhibit.image}
                alt={exhibit.artist || 'Exhibit'}
                onError={(e) => {
                  if (exhibit.image && e.currentTarget.src !== exhibit.image) {
                    e.currentTarget.src = exhibit.image
                  }
                }}
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
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}

export default ExhibitList
