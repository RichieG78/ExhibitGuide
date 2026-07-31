import { useState } from 'react'

// Renders an exhibit's image with upload-first precedence (when a non-default
// upload exists), then falls back to image_url, and finally to a placeholder.
// This keeps gallery-owner uploads authoritative while preserving URL fallback.
function ExhibitImage({ exhibit, className }) {
  const hasUploadedImage = Boolean(exhibit.image) && !String(exhibit.image).includes('/default.jpg')
  const sources = hasUploadedImage
    ? [exhibit.image, exhibit.image_url].filter(Boolean)
    : [exhibit.image_url, exhibit.image].filter(Boolean)
  const [index, setIndex] = useState(0)

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
      alt={exhibit.artist || 'Exhibit'}
      onError={() => setIndex((current) => current + 1)}
    />
  )
}

export default ExhibitImage
