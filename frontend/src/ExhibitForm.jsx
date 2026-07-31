import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './Manage.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const CURRENCIES = ['USD', 'EUR', 'GBP']

const EMPTY = {
  gallery_name: '',
  artwork: '',
  show: '',
  price: '',
  currency: 'USD',
  tldr: '',
  full_text: '',
  audio_url: '',
  video_url: '',
  image_url: '',
  publish_date: '',
}

// Create or edit an exhibit (staff only). Artwork/Show are chosen from existing
// records (managed in Django admin); an image can be uploaded via multipart.
function ExhibitForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const { authFetch } = useAuth()
  const navigate = useNavigate()

  const [artworks, setArtworks] = useState([])
  const [shows, setShows] = useState([])
  const [form, setForm] = useState(EMPTY)
  const [imageFile, setImageFile] = useState(null)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    // Load dropdown options and existing exhibit data (when editing).
    fetch(`${API_BASE}/api/artworks/`).then((r) => r.json()).then(setArtworks)
    fetch(`${API_BASE}/api/shows/`).then((r) => r.json()).then(setShows)
    if (isEdit) {
      fetch(`${API_BASE}/api/exhibits/${id}/`)
        .then((r) => r.json())
        .then((d) =>
          setForm({
            gallery_name: d.gallery_name || '',
            artwork: d.artwork || '',
            show: d.show || '',
            price: d.price ?? '',
            currency: d.currency || 'USD',
            tldr: d.tldr || '',
            full_text: d.full_text || '',
            audio_url: d.audio_url || '',
            video_url: d.video_url || '',
            image_url: d.image_url || '',
            publish_date: d.publish_date ? d.publish_date.slice(0, 16) : '',
          })
        )
    }
  }, [id, isEdit])

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const submit = (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    // Multipart payload allows optional image upload plus text fields.
    const fd = new FormData()
    fd.append('gallery_name', form.gallery_name)
    if (form.artwork) fd.append('artwork', form.artwork)
    if (form.show) fd.append('show', form.show)
    fd.append('price', form.price || 0)
    fd.append('currency', form.currency)
    fd.append('tldr', form.tldr)
    fd.append('full_text', form.full_text)
    fd.append('audio_url', form.audio_url)
    fd.append('video_url', form.video_url)
    fd.append('image_url', form.image_url)
    if (form.publish_date) fd.append('publish_date', form.publish_date)
    if (imageFile) fd.append('image', imageFile)

    authFetch(isEdit ? `/api/exhibits/${id}/` : '/api/exhibits/', {
      method: isEdit ? 'PATCH' : 'POST',
      body: fd,
    })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((d) => {
            throw new Error(Object.entries(d).map(([k, v]) => `${k}: ${v}`).join('; '))
          })
        }
        return res.json()
      })
      .then(() => navigate('/manage'))
      .catch((err) => {
        setError(err.message)
        setSubmitting(false)
      })
  }

  return (
    <main className="manage">
      <header className="manage-header">
        <div>
          <Link to="/manage" className="manage-back">← Back to manage</Link>
          <h1 className="manage-title">{isEdit ? 'Edit exhibit' : 'New exhibit'}</h1>
        </div>
      </header>

      <form className="manage-form" onSubmit={submit}>
        <label className="mf">
          Gallery name
          <input value={form.gallery_name} onChange={set('gallery_name')} />
        </label>
        <label className="mf">
          Artwork
          <select value={form.artwork} onChange={set('artwork')}>
            <option value="">— select —</option>
            {artworks.map((a) => (
              <option key={a.artwork_id} value={a.artwork_id}>
                {a.title} — {a.artist_name}
              </option>
            ))}
          </select>
        </label>
        <label className="mf">
          Show
          <select value={form.show} onChange={set('show')}>
            <option value="">— none —</option>
            {shows.map((s) => (
              <option key={s.show_id} value={s.show_id}>{s.show_name}</option>
            ))}
          </select>
        </label>
        <div className="mf-row">
          <label className="mf">
            Price
            <input type="number" min="0" value={form.price} onChange={set('price')} />
          </label>
          <label className="mf">
            Currency
            <select value={form.currency} onChange={set('currency')}>
              {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
        </div>
        <label className="mf">
          Summary
          <textarea rows="2" value={form.tldr} onChange={set('tldr')} />
        </label>
        <label className="mf">
          Full text
          <textarea rows="4" value={form.full_text} onChange={set('full_text')} />
        </label>
        <label className="mf">
          Image URL (external)
          <input value={form.image_url} onChange={set('image_url')} placeholder="https://…" />
        </label>
        <label className="mf">
          Upload image
          <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0] || null)} />
        </label>
        <div className="mf-row">
          <label className="mf">
            Audio URL
            <input value={form.audio_url} onChange={set('audio_url')} placeholder="https://…" />
          </label>
          <label className="mf">
            Video URL
            <input value={form.video_url} onChange={set('video_url')} placeholder="https://…" />
          </label>
        </div>
        <label className="mf">
          Publish date
          <input type="datetime-local" value={form.publish_date} onChange={set('publish_date')} />
        </label>

        {error && <p className="manage-error">{error}</p>}
        <button className="manage-submit" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : isEdit ? 'Save changes' : 'Create exhibit'}
        </button>
      </form>
    </main>
  )
}

export default ExhibitForm
