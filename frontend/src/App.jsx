import { Routes, Route, useParams } from 'react-router-dom'
import './App.css'
import ExhibitList from './ExhibitList'
import ExhibitDetail from './ExhibitDetail'
import ScanScreen from './ScanScreen'
import Dashboard from './Dashboard'
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage'
import PasswordResetRequestPage from './PasswordResetRequestPage'
import PasswordResetConfirmPage from './PasswordResetConfirmPage'
import ProfilePage from './ProfilePage'
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

// Entry point for printed QR codes: /qr/<qr_identifier> resolves the work by its
// printed identifier and shows the same public exhibit page. No login required.
function QrRoute() {
  const { qrId } = useParams()
  return <ExhibitDetail qrId={qrId} />
}

function App() {
  // Central route map for all public pages, member pages, and staff pages.
  return (
    <Routes>
      <Route path="/" element={<ExhibitList />} />
      <Route path="/exhibits/:id" element={<ExhibitDetailRoute />} />
      <Route path="/qr/:qrId" element={<QrRoute />} />
      <Route path="/scan" element={<ScanScreen />} />
      <Route path="/scan/:id" element={<ScanScreen />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/password-reset" element={<PasswordResetRequestPage />} />
      <Route path="/reset-password" element={<PasswordResetConfirmPage />} />
      <Route
        path="/dashboard"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        }
      />
      <Route
        path="/profile"
        element={
          <RequireAuth>
            <ProfilePage />
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
