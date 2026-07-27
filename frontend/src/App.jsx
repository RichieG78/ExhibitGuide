import { Routes, Route, useParams, Link } from 'react-router-dom'
import './App.css'
import ExhibitList from './ExhibitList'
import ExhibitDetail from './ExhibitDetail'

// Small wrapper: pulls the :id out of the URL and hands it to ExhibitDetail,
// keeping ExhibitDetail itself a plain, reusable id-driven component.
function ExhibitDetailRoute() {
  const { id } = useParams()
  return <ExhibitDetail id={id} />
}

function App() {
  return (
    <main className="page">
      <header className="page-header">
        <Link to="/" className="page-title-link">
          <h1>ExhibitGuide</h1>
        </Link>
        <p>Served live from the Django REST API</p>
      </header>

      <Routes>
        <Route path="/" element={<ExhibitList />} />
        <Route path="/exhibits/:id" element={<ExhibitDetailRoute />} />
      </Routes>
    </main>
  )
}

export default App
