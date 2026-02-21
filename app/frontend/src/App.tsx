import React, { useState, useRef, useCallback } from 'react'
import type { AnalysisResult } from './types'
import { runDemo, analyzeSingle, analyzeSequence } from './api'
import {
  AreaProgressionChart, TissueCompositionChart, PushScoreChart,
  RiskChart, HealingVelocityChart, TissueTrendChart,
  AlertsPanel, SummaryStats, TimepointTimeline,
} from './components/Charts'

// ── Types ─────────────────────────────────────────────────────────
type Page = 'landing' | 'login' | 'home' | 'patient_search' | 'upload' | 'dashboard'
type UploadMode = 'single' | 'sequence' | 'demo'

interface PatientForm {
  patient_id: string; age: number; HbA1c: number; smoker: boolean
  diabetes_duration_years: number; wound_location: string; name?: string
}

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

// ── Landing Page ──────────────────────────────────────────────────
function LandingPage({ onLogin, onDemo }: { onLogin: () => void; onDemo: () => void }) {
  return (
    <>
      <section className="hero container">
        <div className="animate-fade-up">
          <div className="hero-eyebrow">
            <span>🤖</span> Powered by Google MedGemma 1.5 & 27B
          </div>
          <h1>AI-Powered DFU<br />Assessment for ASHAs</h1>
          <p>
            WoundTrack empowers community health workers in India with clinical-grade Diabetic Foot Ulcer assessments.
            Capture standard wound scores, forecast healing, and receive actionable alerts to escalate care to PHC doctors
            — preventing up to 85% of lower limb amputations.
          </p>
          <div className="hero-cta">
            <button className="btn btn-primary btn-lg" onClick={onLogin}>
              ASHA Worker Login
            </button>
            <button id="try-demo-btn" className="btn btn-outline btn-lg" onClick={onDemo}>
              <span>▶</span> Run Live Demo
            </button>
          </div>
        </div>
      </section>

      {/* Feature pills */}
      <div className="container">
        <div className="features-row animate-fade-up-delay">
          {[
            ['🔬', 'WoundVision (1.5 VLM)'],
            ['📊', 'PUSH & Wagner Scoring'],
            ['⚠️', 'Amputation Risk (RiskFusion)'],
            ['🔮', 'HealCast Forecasting'],
            ['🏥', 'PHC Escalation Alerts'],
            ['📄', 'Longitudinal Reports'],
          ].map(([icon, label]) => (
            <div className="feature-pill" key={label as string}>
              <span>{icon}</span>
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture cards */}
      <div className="container mt-8" style={{ paddingBottom: 80 }}>
        <h2 className="section-title text-center" style={{ fontSize: 28, marginBottom: 32 }}>
          5-Component <span>AI Pipeline</span>
        </h2>
        <div className="grid-3 animate-fade-up-delay">
          {[
            {
              icon: '🔬', title: 'WoundVision',
              desc: 'MedGemma 1.5 VLM analyses DFU images to extract dimensions, tissue composition, exudate characteristics, and surrounding skin condition.',
              badge: '1.5 VLM',
            },
            {
              icon: '📊', title: 'WoundScore',
              desc: 'Computes clinical scores: PUSH (Pressure Ulcer Scale for Healing) and Wagner Grade — standardised metrics used by clinicians globally.',
              badge: 'Clinical',
            },
            {
              icon: '⚠️', title: 'RiskFusion',
              desc: 'Fuses wound features with patient history (HbA1c, smoking, age) to produce a real-time amputation risk probability.',
              badge: 'Risk AI',
            },
            {
              icon: '🔮', title: 'HealCast',
              desc: 'Projects days-to-closure using historical area data and healing rate — enabling proactive care planning.',
              badge: 'Forecast',
            },
            {
              icon: '🏥', title: 'CareGuide',
              desc: 'Generates evidence-based care recommendations and escalation decisions (Routine / Escalate to PHC Doctor / Urgent) tailored for ASHA workflows.',
              badge: 'Action',
            },
            {
              icon: '📈', title: 'Longitudinal Engine',
              desc: 'Tracks 10+ metrics across visits, runs trend analysis, detects anomalies, and generates clinical alerts automatically.',
              badge: 'Tracking',
            },
          ].map(c => (
            <div className="card" key={c.title} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: 28 }}>{c.icon}</span>
                <div>
                  <h3 style={{ fontWeight: 700, fontSize: 16 }}>{c.title}</h3>
                  <span className="badge badge-teal" style={{ fontSize: 10 }}>{c.badge}</span>
                </div>
              </div>
              <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.7 }}>{c.desc}</p>
            </div>
          ))}
        </div>

        {/* Tech stack */}
        <div className="card mt-8" style={{ textAlign: 'center' }}>
          <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Technology Stack</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Google MedGemma 1.5 + 27B', 'PyTorch + HuggingFace', 'FastAPI', 'React + Vite', 'Recharts'].map(t => (
              <span className="badge badge-teal" key={t} style={{ fontSize: 13, padding: '6px 14px' }}>{t}</span>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

// ── Login Page ────────────────────────────────────────────────────
function LoginPage({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="container" style={{ paddingTop: 80, paddingBottom: 60, maxWidth: 460 }}>
      <div className="card animate-fade-up text-center">
        <span style={{ fontSize: 48, display: 'block', marginBottom: 16 }}>👩🏽‍⚕️</span>
        <h2 className="section-title" style={{ fontSize: 24, marginBottom: 8 }}>ASHA Worker <span>Login</span></h2>
        <p style={{ color: '#64748b', fontSize: 14, marginBottom: 32 }}>Secure login for community health workers.</p>

        <div className="form-group mb-4" style={{ textAlign: 'left' }}>
          <label className="form-label">Phone Number / ASHA ID</label>
          <input className="form-input" defaultValue="9876543210" />
        </div>
        <div className="form-group mb-6" style={{ textAlign: 'left' }}>
          <label className="form-label">OTP / Password</label>
          <input className="form-input" type="password" defaultValue="1234" />
        </div>

        <button className="btn btn-primary w-full" style={{ padding: 14 }} onClick={onLogin}>
          Verify & Login
        </button>
      </div>
    </div>
  )
}

// ── Home Page ─────────────────────────────────────────────────────
function AshaHome({ onNewPatient, onRecent }: { onNewPatient: () => void, onRecent: () => void }) {
  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <div className="flex justify-between items-center mb-6 animate-fade-up" style={{ flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 className="section-title" style={{ margin: 0, fontSize: 28 }}>Welcome, <span>Sunita</span> (ASHA)</h1>
          <p style={{ color: '#64748b', fontSize: 14, marginTop: 4 }}>Primary Health Center: Shirur, Maharashtra</p>
        </div>
        <button className="btn btn-primary" onClick={onNewPatient}>+ Assess New Patient</button>
      </div>

      <div className="card animate-fade-up-delay">
        <div className="flex justify-between items-center mb-4">
          <h3 className="section-title" style={{ fontSize: 16, margin: 0 }}>Recent Field Visits</h3>
        </div>

        <div className="timeline" style={{ marginTop: 16 }}>
          {/* Mock recent patient */}
          <div className="tp-item" style={{ cursor: 'pointer' }} onClick={onRecent}>
            <div className="tp-day" style={{ background: 'linear-gradient(135deg, #10b981, #065f46)' }}>
              <span style={{ fontSize: 12 }}>PT</span>
              <span style={{ fontSize: 14 }}>042</span>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontWeight: 700, fontSize: 15, color: '#0f172a' }}>Rajesh Kumar</span>
                <span className="badge badge-stable">Follow-up</span>
              </div>
              <p style={{ fontSize: 13, color: '#64748b' }}>Last visited: 2 days ago • Status: Healing Well</p>
            </div>
            <div style={{ fontSize: 20, color: '#cbd5e1' }}>›</div>
          </div>
        </div>

        <div style={{ textAlign: 'center', padding: '32px 0 16px', borderTop: '1px solid rgba(0,0,0,0.05)', marginTop: 24 }}>
          <p style={{ color: '#64748b', fontSize: 14 }}>No more patients for today. Tap "+ Assess New Patient" to start a field visit.</p>
        </div>
      </div>
    </div>
  )
}

// ── Patient Search Page ───────────────────────────────────────────
function PatientSearch({ onPatientFound }: { onPatientFound: (p: PatientForm) => void }) {
  const [abha, setAbha] = useState('14-0453-2342-9901')
  const [loading, setLoading] = useState(false)

  const handleFetch = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      onPatientFound({
        patient_id: 'PT-Ramesh-001', name: 'Ramesh (रमेश)', age: 58, HbA1c: 8.5, smoker: false,
        diabetes_duration_years: 10, wound_location: 'Plantar right foot',
      })
    }, 1200)
  }

  return (
    <div className="container" style={{ paddingTop: 60, paddingBottom: 60, maxWidth: 500 }}>
      <div className="card animate-fade-up">
        <h3 className="section-title" style={{ fontSize: 22, margin: 0 }}>Patient <span>Lookup</span></h3>
        <p style={{ color: '#64748b', fontSize: 14, marginTop: 8, marginBottom: 24 }}>
          Fetch patient details and longitudinal history directly from the Ayushman Bharat Digital Mission (ABDM) platform.
        </p>

        <div className="form-group mb-6">
          <label className="form-label">ABHA ID / Mobile Number</label>
          <input className="form-input" value={abha} onChange={e => setAbha(e.target.value)} />
        </div>

        <button className="btn btn-primary w-full" onClick={handleFetch} disabled={loading}>
          {loading ? (
            <><div className="spinner" style={{ width: 16, height: 16, borderTopColor: '#fff', borderWidth: 2 }} /><span>Fetching ABDM Records...</span></>
          ) : (
            <><span>🔍</span><span>Fetch Patient Details</span></>
          )}
        </button>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <button className="btn btn-ghost btn-sm" onClick={() => onPatientFound({
            patient_id: 'PT-NEW-001', age: 0, HbA1c: 0, smoker: false, diabetes_duration_years: 0, wound_location: ''
          })}>Skip / Manual Entry</button>
        </div>
      </div>
    </div>
  )
}


// ── Upload Form ───────────────────────────────────────────────────
function UploadPage({ patient, onResult, onBack }: { patient: PatientForm, onResult: (r: AnalysisResult) => void, onBack: () => void }) {
  const [mode, setMode] = useState<UploadMode>('single')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFiles = useCallback((incoming: FileList | null) => {
    if (!incoming) return
    setFiles(Array.from(incoming))
  }, [])

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const submit = async () => {
    setLoading(true); setError('')
    try {
      let result: AnalysisResult
      if (mode === 'demo') {
        result = await runDemo({ patient_id: patient.patient_id, age: patient.age || 58, HbA1c: patient.HbA1c || 8.5, smoker: patient.smoker })
      } else if (mode === 'single') {
        if (!files.length) throw new Error('Please capture a foot ulcer image')
        result = await analyzeSingle(files[0], patient)
      } else {
        if (!files.length) throw new Error('Please upload at least one image')
        result = await analyzeSequence(files, [0], patient) // simplification
      }
      onResult(result)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 60, maxWidth: 800 }}>
      <button className="btn btn-ghost btn-sm mb-4" onClick={onBack}>← Back</button>

      {/* Patient Summary Card */}
      <div className="card mb-6 animate-fade-up" style={{ padding: '16px 24px', background: 'rgba(45, 143, 142, 0.05)', borderColor: 'rgba(45, 143, 142, 0.2)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: 0 }}>
              {patient.name || 'New Patient'} <span style={{ color: '#64748b', fontWeight: 500 }}>({patient.patient_id})</span>
            </h3>
            <p style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>
              Age: {patient.age || '--'} • HbA1c: {patient.HbA1c || '--'}% • Diabetes: {patient.diabetes_duration_years || '--'} yrs
            </p>
          </div>
          <span className="badge badge-teal">ABDM Verified ✅</span>
        </div>
      </div>

      <div className="grid-2 animate-fade-up-delay">
        {/* Left: Action Mode */}
        <div className="card">
          <h3 className="section-title" style={{ fontSize: 16, marginBottom: 16 }}>Assessment Type</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {([['single', '📷 Capture Field Photo (New Visit)'], ['demo', '🎬 Run Story Demo (Ramesh)']] as [UploadMode, string][]).map(([m, label]) => (
              <button key={m} id={`mode-${m}`}
                className={`btn ${mode === m ? 'btn-primary' : 'btn-ghost'}`}
                style={{ justifyContent: 'flex-start' }}
                onClick={() => setMode(m)}>
                {label}
              </button>
            ))}
          </div>

          <div style={{ marginTop: 24, padding: 16, background: 'rgba(0,0,0,0.03)', borderRadius: 8 }}>
            <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
              Ensure the wound is well lit and the camera is held approx 15cm away. The AI will handle color calibration automatically.
            </p>
          </div>
        </div>

        {/* Right: Upload zone */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {mode !== 'demo' && (
            <div className="card" style={{ flex: 1 }}>
              <h3 className="section-title" style={{ fontSize: 16, marginBottom: 16 }}>
                Image Capture
              </h3>

              <div
                id="upload-dropzone"
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                style={{ padding: '32px 20px', height: 'auto' }}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  onChange={e => handleFiles(e.target.files)}
                />
                <div style={{ fontSize: 36, marginBottom: 8 }}>📸</div>
                <p style={{ fontWeight: 600, marginBottom: 4 }}>
                  {files.length ? `${files.length} file(s) selected` : 'Tap to Open Camera'}
                </p>
              </div>

              {files.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {files.map((f, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#64748b' }}>
                      <span>🖼️</span>
                      <span style={{ color: '#0f172a', flex: 1 }}>{f.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {mode === 'demo' && (
            <div className="card" style={{ flex: 1, textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <span style={{ fontSize: 48, marginBottom: 12 }}>👨🏽‍🌾</span>
              <h3 style={{ fontWeight: 700, margin: 0 }}>Demo: Ramesh's Story</h3>
              <p style={{ color: '#64748b', fontSize: 13, marginTop: 8 }}>
                Simulate the case of Ramesh, a 58-year-old farmer assessed by Sunita (ASHA). Watch the AI escalate high-risk factors to a PHC.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 animate-fade-up-delay">
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: 10, padding: '12px 16px', color: '#ef4444', fontSize: 14, marginBottom: 16
          }}>
            ⚠️ {error}
          </div>
        )}

        <button id="run-analysis-btn" className="btn btn-primary btn-lg w-full"
          onClick={submit} disabled={loading}>
          {loading ? (
            <><div className="spinner" style={{ width: 20, height: 20, borderTopColor: '#fff', borderWidth: 2 }} /><span>Analyzing DFU via MedGemma...</span></>
          ) : (
            <><span>⚡</span><span>Run AI Assessment</span></>
          )}
        </button>
      </div>
    </div>
  )
}

// ── Dashboard Page ────────────────────────────────────────────────
function DashboardPage({ result, onBack }: { result: AnalysisResult; onBack: () => void }) {
  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 80 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back to Home</button>
            <span className="badge badge-teal">{result.mode?.toUpperCase()} MODE</span>
          </div>
          <h1 className="section-title" style={{ fontSize: 28, margin: 0 }}>
            Analysis <span>Dashboard</span>
          </h1>
          <p style={{ color: '#64748b', fontSize: 14, marginTop: 4 }}>
            Patient: <b style={{ color: '#0f172a' }}>{result.wound_id}</b> &nbsp;·&nbsp;
            {result.timepoints.length} timepoints &nbsp;·&nbsp;
            {result.duration_days}-day span
          </p>
        </div>
      </div>

      {/* Summary stats */}
      <SummaryStats result={result} />

      {/* Charts row 1 */}
      <div className="grid-2 mt-6">
        <AreaProgressionChart result={result} />
        <TissueCompositionChart result={result} />
      </div>

      {/* Charts row 2 */}
      <div className="grid-2 mt-4">
        <PushScoreChart result={result} />
        <RiskChart result={result} />
      </div>

      {/* Charts row 3 */}
      <div className="grid-2 mt-4">
        <HealingVelocityChart result={result} />
        <TissueTrendChart result={result} />
      </div>

      {/* Alerts */}
      <div className="mt-4">
        <AlertsPanel alerts={result.alerts} />
      </div>

      {/* Timeline */}
      <div className="mt-4">
        <TimepointTimeline result={result} />
      </div>

      {/* Patient info */}
      <div className="card mt-4">
        <h3 className="section-title" style={{ fontSize: 16, marginBottom: 12 }}>Patient Context</h3>
        <div className="grid-4">
          {Object.entries(result.patient_history || {}).map(([k, v]) => (
            <div key={k}>
              <p style={{ fontSize: 11, color: '#64748b', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k.replace(/_/g, ' ')}</p>
              <p style={{ fontWeight: 600, fontSize: 14, color: '#0f172a', marginTop: 2 }}>{String(v)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── App root ──────────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState<Page>('landing')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [patient, setPatient] = useState<PatientForm | null>(null)

  const handleResult = (r: AnalysisResult) => { setResult(r); setPage('dashboard') }

  const handleDemo = async () => {
    setLoading(true)
    try {
      const r = await runDemo()
      setResult(r)
      setPage('dashboard')
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Nav page={page} onNav={p => {
        setPage(p)
        if (p === 'landing') { setResult(null); setPatient(null); }
      }} />

      {/* Global loading overlay */}
      {loading && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(255,255,255,0.85)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, backdropFilter: 'blur(8px)',
        }}>
          <div className="spinner" style={{ width: 48, height: 48, borderWidth: 4 }} />
          <p style={{ marginTop: 20, color: '#2d8f8e', fontWeight: 600, fontSize: 16 }}>
            Running AI Pipeline…
          </p>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            WoundVision → WoundScore → RiskFusion → HealCast → CareGuide
          </p>
        </div>
      )}

      {page === 'landing' && (
        <LandingPage onLogin={() => setPage('login')} onDemo={handleDemo} />
      )}
      {page === 'login' && (
        <LoginPage onLogin={() => setPage('home')} />
      )}
      {page === 'home' && (
        <AshaHome onNewPatient={() => setPage('patient_search')} onRecent={() => {
          setPatient({
            patient_id: 'PT-042', age: 62, HbA1c: 7.1, smoker: false,
            diabetes_duration_years: 8, wound_location: 'Dorsal'
          })
          setPage('upload')
        }} />
      )}
      {page === 'patient_search' && (
        <PatientSearch onPatientFound={(p) => { setPatient(p); setPage('upload') }} />
      )}
      {page === 'upload' && patient && (
        <UploadPage patient={patient} onResult={handleResult} onBack={() => setPage('home')} />
      )}
      {page === 'dashboard' && result && (
        <DashboardPage result={result} onBack={() => setPage('home')} />
      )}
    </>
  )
}
