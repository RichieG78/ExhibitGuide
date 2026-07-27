import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './ExhibitDetail.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Shows the full detail of a single exhibit, fetched by its id.
// Written as a reusable component so it can later be driven by a route param.
function ExhibitDetail({ id }) {
  const [exhibit, setExhibit] = useState(null)
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')

  useEffect(() => {
    setStatus('loading')
    fetch(`${API_BASE}/api/exhibits/${id}/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API responded with ${response.status}`)
        }
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
  }, [id])

  if (status === 'loading') {
    return <p className="detail-status">Loading exhibit…</p>
  }
  if (status === 'error') {
    return <p className="detail-status detail-error">Could not load exhibit: {error}</p>
  }

  const priceLabel = exhibit.price
    ? `${exhibit.currency} ${exhibit.price.toLocaleString()}`
    : 'Price on request'

  const dimensions =
    exhibit.dimensions_height && exhibit.dimensions_width
      ? `${exhibit.dimensions_height} × ${exhibit.dimensions_width} cm`
      : null

  const publishDate = exhibit.publish_date
    ? new Date(exhibit.publish_date).toLocaleDateString()
    : null

  return (
    <>
      <Link to="/" className="detail-back">← All exhibits</Link>
      <article className="detail">
      <div className="detail-media">
        <img
          className="detail-image"
          src={exhibit.image_url || exhibit.image}
          alt={exhibit.artist || 'Exhibit'}
          onError={(e) => {
            // If the external image_url fails, fall back to the local image once.
            if (exhibit.image && e.currentTarget.src !== exhibit.image) {
              e.currentTarget.src = exhibit.image
            }
          }}
        />
      </div>

      <div className="detail-info">
        {exhibit.show_name && <p className="detail-show">{exhibit.show_name}</p>}
        <h1 className="detail-artist">{exhibit.artist || 'Unknown artist'}</h1>

        <ul className="detail-meta">
          {exhibit.medium && (
            <li>
              <span>Medium</span>
              {exhibit.medium}
            </li>
          )}
          {dimensions && (
            <li>
              <span>Dimensions</span>
              {dimensions}
            </li>
          )}
          {exhibit.gallery_name && (
            <li>
              <span>Gallery</span>
              {exhibit.gallery_name}
            </li>
          )}
          <li>
            <span>Price</span>
            {priceLabel}
          </li>
        </ul>

        {exhibit.tldr && <p className="detail-tldr">{exhibit.tldr}</p>}
        {exhibit.full_text && <p className="detail-fulltext">{exhibit.full_text}</p>}

        {exhibit.provenance && (
          <section className="detail-section">
            <h2>Provenance</h2>
            <p>{exhibit.provenance}</p>
          </section>
        )}

        {(exhibit.audio_url || exhibit.video_url) && (
          <section className="detail-section">
            <h2>Media</h2>
            <ul className="detail-links">
              {exhibit.audio_url && (
                <li>
                  <a href={exhibit.audio_url} target="_blank" rel="noreferrer">
                    Audio guide
                  </a>
                </li>
              )}
              {exhibit.video_url && (
                <li>
                  <a href={exhibit.video_url} target="_blank" rel="noreferrer">
                    Video
                  </a>
                </li>
              )}
            </ul>
          </section>
        )}

        <footer className="detail-footer">
          {publishDate && <span>Published {publishDate}</span>}
          {exhibit.qr_identifier && <span>QR #{exhibit.qr_identifier}</span>}
        </footer>
      </div>
      </article>
    </>
  )
}

export default ExhibitDetail
