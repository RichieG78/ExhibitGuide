import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function toAbsoluteUrl(url) {
  if (!url) {
    return ''
  }
  if (/^https?:\/\//i.test(url)) {
    return url
  }
  if (url.startsWith('/')) {
    return `${API_BASE}${url}`
  }
  return url
}

function toWikimediaOriginal(url) {
  const marker = '/wikipedia/commons/thumb/'
  if (!url.includes(marker)) {
    return ''
  }

  const [prefix, remainder] = url.split(marker)
  const parts = remainder.split('/')
  if (parts.length < 4) {
    return ''
  }

  return `${prefix}/wikipedia/commons/${parts[0]}/${parts[1]}/${parts[2]}`
}

function toWikimediaThumb1280(url) {
  const originalMarker = '/wikipedia/commons/'
  if (!url.includes(originalMarker) || url.includes('/wikipedia/commons/thumb/')) {
    return ''
  }

  const [prefix, remainder] = url.split(originalMarker)
  const parts = remainder.split('/')
  if (parts.length < 3) {
    return ''
  }

  const filename = parts[2]
  return `${prefix}/wikipedia/commons/thumb/${parts[0]}/${parts[1]}/${filename}/1280px-${filename}`
}

function expandImageSources(rawSources) {
  const expanded = []

  rawSources.forEach((candidate) => {
    const source = toAbsoluteUrl(candidate)
    if (!source) {
      return
    }

    if (source.includes('/wikipedia/commons/thumb/')) {
      const original = toWikimediaOriginal(source)
      const preferred = original ? toWikimediaThumb1280(original) : ''

      if (preferred) {
        expanded.push(preferred)
      }
      expanded.push(source)
      if (original) {
        expanded.push(original)
      }
      return
    }

    if (source.includes('/wikipedia/commons/')) {
      const thumb = toWikimediaThumb1280(source)
      if (thumb) {
        expanded.push(thumb)
      }
      expanded.push(source)
      return
    }

    expanded.push(source)
  })

  return [...new Set(expanded)]
}

// Renders an exhibit's image with upload-first precedence (when a non-default
// upload exists), then falls back to image_url, and finally to a placeholder.
// This keeps gallery-owner uploads authoritative while preserving URL fallback.
function ExhibitImage({ exhibit, className }) {
  const hasUploadedImage = Boolean(exhibit.image) && !String(exhibit.image).includes('/default.jpg')
  const rawSources = hasUploadedImage
    ? [exhibit.image, exhibit.image_url].filter(Boolean)
    : [exhibit.image_url, exhibit.image].filter(Boolean)
  const sources = expandImageSources(rawSources)
  const [index, setIndex] = useState(0)
  const altText = [exhibit.title, exhibit.artist].filter(Boolean).join(' by ') || 'Exhibit image'

  // Ran out of sources to try (or there were none): show a placeholder.
  if (index >= sources.length) {
    return (
      <div className={`${className} exhibit-image--placeholder`}>
        <span>No image available</span>
      </div>
    )
  }

  return (
    <img
      className={className}
      src={sources[index]}
      alt={altText}
      loading="lazy"
      decoding="async"
      onError={() => setIndex((current) => current + 1)}
    />
  )
}

export default ExhibitImage
