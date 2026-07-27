import { useState } from 'react'

// Renders an exhibit's image, trying the external image_url first, then the
// local uploaded image, and finally a graceful placeholder if both fail — so a
// broken or blocked URL never shows the browser's default broken-image icon.
function ExhibitImage({ exhibit, className }) {
  const sources = [exhibit.image_url, exhibit.image].filter(Boolean)
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
