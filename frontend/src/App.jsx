import { Routes, Route, useParams } from 'react-router-dom'
import './App.css'
import ExhibitList from './ExhibitList'
import ExhibitDetail from './ExhibitDetail'
import ScanScreen from './ScanScreen'
import Dashboard from './Dashboard'
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage'
import RequireAuth from './RequireAuth'
import RequireStaff from './RequireStaff'
import ManageExhibits from './ManageExhibits'
import ExhibitForm from './ExhibitForm'

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
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        }
      />
      <Route path="/manage" element={<RequireStaff><ManageExhibits /></RequireStaff>} />
      <Route path="/manage/new" element={<RequireStaff><ExhibitForm /></RequireStaff>} />
      <Route path="/manage/:id/edit" element={<RequireStaff><ExhibitForm /></RequireStaff>} />
    </Routes>
  )
}

export default App
