import React, { useState, Suspense } from 'react'
import type { AnalysisResult, Page, PatientForm } from './types'
import { ErrorBoundary } from './components/ErrorBoundary'
import { fetchPatientHistory } from './api'

// ── Lazy-loaded Pages ─────────────────────────────────────────────
const LandingPage = React.lazy(() => import('./pages/LandingPage').then(module => ({ default: module.LandingPage })))
const LoginPage = React.lazy(() => import('./pages/LoginPage').then(module => ({ default: module.LoginPage })))
const AshaHome = React.lazy(() => import('./pages/AshaHome').then(module => ({ default: module.AshaHome })))
const PatientSearch = React.lazy(() => import('./pages/PatientSearch').then(module => ({ default: module.PatientSearch })))
const UploadPage = React.lazy(() => import('./pages/UploadPage').then(module => ({ default: module.UploadPage })))
const DashboardPage = React.lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })))


// ── Nav ───────────────────────────────────────────────────────────
function Nav({ onNav, page }: { page: Page; onNav: (p: Page) => void }) {
  const isLoggedIn = ['home', 'patient_search', 'upload', 'dashboard'].includes(page)
  return (
    <nav className="nav">
      <div className="container">
        <div className="nav-inner">
          <a className="nav-brand" href="#" onClick={e => { e.preventDefault(); onNav(isLoggedIn ? 'home' : 'landing') }}>
            <span style={{ fontSize: 26 }}>🏥</span>
            <div>
              <div className="nav-logo">WoundTrack</div>
              <div className="nav-sub">ASHA DFU ANALYTICS</div>
            </div>
          </a>
          <div className="nav-links">
            {isLoggedIn ? (
              <>
                <button className="btn btn-ghost btn-sm" onClick={() => onNav('home')}>ASHA Dashboard</button>
                <button className="btn btn-outline btn-sm" onClick={() => onNav('landing')}>Logout</button>
              </>
            ) : (
              <>
                <button className="btn btn-ghost btn-sm" onClick={() => onNav('landing')}>Home</button>
                <button className="btn btn-outline btn-sm" onClick={() => onNav('login')}>ASHA Login</button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

// ── App root ──────────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState<Page>('landing')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [patient, setPatient] = useState<PatientForm | null>(null)

  const handleResult = (r: AnalysisResult) => { setResult(r); setPage('dashboard') }

  return (
    <>
      <Nav page={page} onNav={p => {
        setPage(p)
        if (p === 'landing') { setResult(null); setPatient(null); }
      }} />

      <ErrorBoundary>
        <Suspense fallback={
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
            <div className="spinner" style={{ width: 40, height: 40, borderWidth: 3 }} />
          </div>
        }>
          {page === 'landing' && (
            <LandingPage onLogin={() => setPage('login')} />
          )}
          {page === 'login' && (
            <LoginPage onLogin={() => setPage('home')} />
          )}
          {page === 'home' && (
            <AshaHome onNewPatient={() => setPage('patient_search')} onRecent={async () => {
              const p = {
                patient_id: 'PT-042', age: 62, HbA1c: 7.1, smoker: false,
                diabetes_duration_years: 8, wound_location: 'Dorsal'
              };
              setPatient(p);
              try {
                const history = await fetchPatientHistory(p.patient_id);
                if (history && history.timepoints && history.timepoints.length > 0) {
                  setResult(history);
                  setPage('dashboard');
                } else {
                  setPage('upload');
                }
              } catch (e) {
                setPage('upload');
              }
            }} />
          )}
          {page === 'patient_search' && (
            <PatientSearch
              onPatientFound={(p) => { setPatient(p); setPage('upload') }}
              onHistoryFound={(p, history) => { setPatient(p); setResult(history); setPage('dashboard') }}
            />
          )}
          {page === 'upload' && patient && (
            <UploadPage patient={patient} onResult={handleResult} onBack={() => setPage('home')} />
          )}
          {page === 'dashboard' && result && (
            <DashboardPage result={result} onBack={() => setPage('home')} onNewUpload={() => setPage('upload')} />
          )}
        </Suspense>
      </ErrorBoundary>
    </>
  )
}
