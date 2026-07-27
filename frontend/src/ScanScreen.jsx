import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ExhibitImage from './ExhibitImage'
import './ScanScreen.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Build a deterministic QR-like matrix (decorative — the real action is the
// "Simulate Scan" button). Proper finder patterns in three corners + a fixed
// pseudo-random field between them.
function buildQrMatrix(n) {
  const m = Array.from({ length: n }, () => Array(n).fill(false))
  const setFinder = (r0, c0) => {
    for (let r = 0; r < 7; r++) {
      for (let c = 0; c < 7; c++) {
        const ring = r === 0 || r === 6 || c === 0 || c === 6
        const center = r >= 2 && r <= 4 && c >= 2 && c <= 4
        m[r0 + r][c0 + c] = ring || center
      }
    }
  }
  setFinder(0, 0)
  setFinder(0, n - 7)
  setFinder(n - 7, 0)
  const inFinderZone = (r, c) =>
    (r < 8 && c < 8) || (r < 8 && c >= n - 8) || (r >= n - 8 && c < 8)
  let s = 987654321
  const rand = () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff
    return (s >>> 0) / 0xffffffff
  }
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (inFinderZone(r, c)) continue
      m[r][c] = rand() > 0.55
    }
  }
  return m
}

const QR_MATRIX = buildQrMatrix(21)

function QrPattern({ size = 84 }) {
  const n = QR_MATRIX.length
  const cell = size / n
  const rects = []
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (QR_MATRIX[r][c]) {
        rects.push(
          <rect key={`${r}-${c}`} x={c * cell} y={r * cell} width={cell} height={cell} />
        )
      }
    }
  }
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} fill="#1c1816" aria-hidden="true">
      {rects}
    </svg>
  )
}

const IconScan = () => (
  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3M4 12h16" />
  </svg>
)

function ScanScreen() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [exhibit, setExhibit] = useState(null)
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [error, setError] = useState('')

  useEffect(() => {
    setStatus('loading')
    // With an id, load that exhibit; otherwise feature the first exhibit.
    const url = id ? `${API_BASE}/api/exhibits/${id}/` : `${API_BASE}/api/exhibits/`
    fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error(`API responded with ${response.status}`)
        return response.json()
      })
      .then((data) => {
        const record = id ? data : data[0]
        if (!record) throw new Error('No exhibits available')
        setExhibit(record)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  if (status === 'loading') {
    return <div className="scan-screen scan-screen--center"><p className="scan-status">Entering the gallery…</p></div>
  }
  if (status === 'error') {
    return <div className="scan-screen scan-screen--center"><p className="scan-status">Could not load: {error}</p></div>
  }

  const year = exhibit.publish_date ? new Date(exhibit.publish_date).getFullYear() : null
  const dimensions =
    exhibit.dimensions_height && exhibit.dimensions_width
      ? `${exhibit.dimensions_height} × ${exhibit.dimensions_width} cm`
      : null
  const metaLine = [exhibit.medium, dimensions, year].filter(Boolean).join(' · ')

  return (
    <div className="scan-screen">
      {/* Blurred artwork backdrop + dark scrim */}
      <div className="scan-bg" aria-hidden="true">
        <ExhibitImage exhibit={exhibit} className="scan-bg__img" />
      </div>
      <div className="scan-scrim" aria-hidden="true" />

      {/* Instruction pill */}
      <p className="scan-pill">
        You are standing in the gallery — tap the QR code to explore this work
      </p>

      <div className="scan-content">
        {/* Framed artwork on the wall */}
        <div className="scan-frame">
          <ExhibitImage exhibit={exhibit} className="scan-frame__img" />
        </div>

        {/* Wall label card */}
        <div className="scan-card">
          <p className="scan-card__gallery">{exhibit.gallery_name || 'ExhibitGuide'}</p>
          <h1 className="scan-card__title">{exhibit.title || exhibit.artist || 'Untitled'}</h1>
          {exhibit.artist && <p className="scan-card__artist">{exhibit.artist}</p>}
          {metaLine && <p className="scan-card__meta">{metaLine}</p>}

          <div className="scan-card__divider" />

          <div className="scan-card__qr-row">
            <div className="scan-qr">
              <QrPattern size={72} />
            </div>
            <div>
              <p className="scan-qr__title">Scan for the story</p>
              <p className="scan-qr__sub">Audio, text &amp; video — no download required.</p>
            </div>
          </div>

          <button
            className="scan-button"
            type="button"
            onClick={() => navigate(`/exhibits/${exhibit.id}`)}
          >
            <IconScan />
            Simulate Scan
          </button>
        </div>
      </div>
    </div>
  )
}

export default ScanScreen
