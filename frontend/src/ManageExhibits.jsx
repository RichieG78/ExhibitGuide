import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './Manage.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Staff-only list of exhibits with edit / delete + a link to create new ones.
function ManageExhibits() {
  const { authFetch } = useAuth()
  const [exhibits, setExhibits] = useState([])
  const [status, setStatus] = useState('loading')

  const load = useCallback(() => {
    // Public list endpoint is reused here; write actions remain staff-protected.
    setStatus('loading')
    fetch(`${API_BASE}/api/exhibits/`)
      .then((r) => r.json())
      .then((d) => {
        setExhibits(d)
        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const remove = (id) => {
    if (!window.confirm('Delete this exhibit? This cannot be undone.')) return
    // Delete uses authenticated staff token via authFetch.
    authFetch(`/api/exhibits/${id}/`, { method: 'DELETE' }).then((res) => {
      if (res.ok) load()
    })
  }

  return (
    <main className="manage">
      <header className="manage-header">
        <div>
          <Link to="/" className="manage-back">← Back to gallery</Link>
          <h1 className="manage-title">Manage Exhibits</h1>
        </div>
        <Link to="/manage/new" className="manage-newbtn">+ New exhibit</Link>
      </header>

      {status === 'loading' && <p className="manage-status">Loading…</p>}
      {status === 'error' && <p className="manage-status">Could not load exhibits.</p>}
      {status === 'ready' && (
        <div className="manage-tablewrap">
          <table className="manage-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Artist</th>
                <th>Price</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {exhibits.map((ex) => (
                <tr key={ex.id}>
                  <td>{ex.title || '—'}</td>
                  <td>{ex.artist || '—'}</td>
                  <td>{ex.price ? `${ex.currency} ${ex.price.toLocaleString()}` : '—'}</td>
                  <td className="manage-actions">
                    <Link to={`/manage/${ex.id}/edit`} className="manage-link">Edit</Link>
                    <button className="manage-del" type="button" onClick={() => remove(ex.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}

export default ManageExhibits
