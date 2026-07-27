import { Routes, Route, useParams } from 'react-router-dom'
import './App.css'
import ExhibitList from './ExhibitList'
import ExhibitDetail from './ExhibitDetail'
import ScanScreen from './ScanScreen'

// Small wrapper: pulls the :id out of the URL and hands it to ExhibitDetail,
// keeping ExhibitDetail itself a plain, reusable id-driven component.
function ExhibitDetailRoute() {
  const { id } = useParams()
  return <ExhibitDetail id={id} />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<ExhibitList />} />
      <Route path="/exhibits/:id" element={<ExhibitDetailRoute />} />
      <Route path="/scan" element={<ScanScreen />} />
      <Route path="/scan/:id" element={<ScanScreen />} />
    </Routes>
  )
}

export default App
