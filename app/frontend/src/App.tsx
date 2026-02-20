import React, { useState, useRef, useCallback } from 'react'
import type { AnalysisResult } from './types'
import { runDemo, analyzeSingle, analyzeSequence } from './api'
import {
  AreaProgressionChart, TissueCompositionChart, PushScoreChart,
  RiskChart, HealingVelocityChart, TissueTrendChart,
  AlertsPanel, SummaryStats, TimepointTimeline,
} from './components/Charts'

// ── Types ─────────────────────────────────────────────────────────
type Page = 'landing' | 'upload' | 'dashboard'
type UploadMode = 'single' | 'sequence' | 'demo'

// ── Nav ───────────────────────────────────────────────────────────
function Nav({ onNav }: { page: Page; onNav: (p: Page) => void }) {
  return (
    <nav className="nav">
      <div className="container">
        <div className="nav-inner">
          <a className="nav-brand" href="#" onClick={e => { e.preventDefault(); onNav('landing') }}>
            <span style={{ fontSize: 26 }}>🏥</span>
            <div>
              <div className="nav-logo">WoundTrack</div>
              <div className="nav-sub">AI WOUND ANALYTICS</div>
            </div>
          </a>
          <div className="nav-links">
            <button className="btn btn-ghost btn-sm" onClick={() => onNav('landing')}>Home</button>
            <button className="btn btn-outline btn-sm" onClick={() => onNav('upload')}>Try Analysis</button>
            <a
              href="https://kaggle.com" target="_blank" rel="noopener noreferrer"
              className="btn btn-ghost btn-sm"
            >Kaggle ↗</a>
          </div>
        </div>
      </div>
    </nav>
  )
}

// ── Landing Page ──────────────────────────────────────────────────
function LandingPage({ onStart, onDemo }: { onStart: () => void; onDemo: () => void }) {
  return (
    <>
      <section className="hero container">
        <div className="animate-fade-up">
          <div className="hero-eyebrow">
            <span>🤖</span> Powered by Google MedGemma AI
          </div>
          <h1>AI-Powered<br />Wound Healing Tracker</h1>
          <p>
            WoundTrack automates wound assessment using MedGemma vision-language models,
            tracking healing progression over time, scoring clinical severity, and alerting
            caregivers before deterioration occurs.
          </p>
          <div className="hero-cta">
            <button id="try-demo-btn" className="btn btn-primary btn-lg" onClick={onDemo}>
              <span>▶</span> Run Live Demo
            </button>
            <button className="btn btn-outline btn-lg" onClick={onStart}>
              Upload Images
            </button>
          </div>
        </div>
      </section>

      {/* Feature pills */}
      <div className="container">
        <div className="features-row animate-fade-up-delay">
          {[
            ['🔬', 'WoundVision (4B VLM)'],
            ['📊', 'PUSH & Wagner Scoring'],
            ['⚠️', 'Amputation Risk (RiskFusion)'],
            ['🔮', 'HealCast Forecasting'],
            ['🏥', 'Auto Clinical Alerts'],
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
              desc: 'MedGemma 4B VLM analyses wound images to extract dimensions, tissue composition, exudate characteristics, and surrounding skin condition.',
              badge: '4B VLM',
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
              desc: 'Generates evidence-based care recommendations and escalation decisions (Routine / Escalate / Urgent) based on all upstream signals.',
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
              <p style={{ fontSize: 13, color: '#7fa5a5', lineHeight: 1.7 }}>{c.desc}</p>
            </div>
          ))}
        </div>

        {/* Tech stack */}
        <div className="card mt-8" style={{ textAlign: 'center' }}>
          <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Technology Stack</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Google MedGemma 4B + 27B', 'PyTorch + HuggingFace', 'FastAPI', 'React + Vite', 'Recharts', 'Stable Diffusion XL'].map(t => (
              <span className="badge badge-teal" key={t} style={{ fontSize: 13, padding: '6px 14px' }}>{t}</span>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

// ── Upload Form ───────────────────────────────────────────────────
interface PatientForm {
  patient_id: string; age: number; HbA1c: number; smoker: boolean
  diabetes_duration_years: number; wound_location: string
}

function UploadPage({ onResult }: { onResult: (r: AnalysisResult) => void }) {
  const [mode, setMode] = useState<UploadMode>('sequence')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [days, setDays] = useState('0,7,14,21,28')
  const fileRef = useRef<HTMLInputElement>(null)
  const [patient, setPatient] = useState<PatientForm>({
    patient_id: 'PT-001', age: 65, HbA1c: 8.2, smoker: false,
    diabetes_duration_years: 10, wound_location: 'Plantar foot',
  })

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
        result = await runDemo({ patient_id: patient.patient_id, age: patient.age, HbA1c: patient.HbA1c, smoker: patient.smoker })
      } else if (mode === 'single') {
        if (!files.length) throw new Error('Please upload a wound image')
        result = await analyzeSingle(files[0], patient)
      } else {
        if (!files.length) throw new Error('Please upload at least one image')
        const dayList = days.split(',').map(d => parseInt(d.trim()))
        result = await analyzeSequence(files, dayList, patient)
      }
      onResult(result)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fp = (k: keyof PatientForm, v: string | number | boolean) =>
    setPatient(p => ({ ...p, [k]: v }))

  return (
    <div className="container" style={{ paddingTop: 40, paddingBottom: 60 }}>
      <h1 className="section-title animate-fade-up" style={{ fontSize: 32, marginBottom: 8 }}>
        Wound <span>Analysis</span>
      </h1>
      <p style={{ color: '#7fa5a5', marginBottom: 32 }} className="animate-fade-up">
        Upload wound images and patient information to run the AI analysis pipeline.
      </p>

      {/* Mode selector */}
      <div className="card animate-fade-up mb-4">
        <h3 className="section-title" style={{ fontSize: 16, marginBottom: 12 }}>Analysis Mode</h3>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {([['demo', '🎬 Run Demo (no upload)'], ['single', '🖼️ Single Image'], ['sequence', '📽️ Sequence (longitudinal)']] as [UploadMode, string][]).map(([m, label]) => (
            <button key={m} id={`mode-${m}`}
              className={`btn ${mode === m ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setMode(m)}>
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid-2">
        {/* Left: Patient info */}
        <div className="card animate-fade-up">
          <h3 className="section-title" style={{ fontSize: 16, marginBottom: 16 }}>
            Patient Information
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="form-group">
              <label className="form-label">Patient ID</label>
              <input id="patient-id-input" className="form-input" value={patient.patient_id}
                onChange={e => fp('patient_id', e.target.value)} />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Age</label>
                <input id="age-input" type="number" className="form-input" value={patient.age}
                  onChange={e => fp('age', +e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">HbA1c</label>
                <input id="hba1c-input" type="number" step="0.1" className="form-input" value={patient.HbA1c}
                  onChange={e => fp('HbA1c', +e.target.value)} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Wound Location</label>
              <input id="wound-location-input" className="form-input" value={patient.wound_location}
                onChange={e => fp('wound_location', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Diabetes Duration (years)</label>
              <input id="diabetes-duration-input" type="number" className="form-input" value={patient.diabetes_duration_years}
                onChange={e => fp('diabetes_duration_years', +e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Smoker</label>
              <select id="smoker-select" className="form-select" value={String(patient.smoker)}
                onChange={e => fp('smoker', e.target.value === 'true')}>
                <option value="false">No</option>
                <option value="true">Yes</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right: Upload zone */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {mode !== 'demo' && (
            <div className="card animate-fade-up">
              <h3 className="section-title" style={{ fontSize: 16, marginBottom: 16 }}>
                {mode === 'single' ? 'Upload Wound Image' : 'Upload Image Sequence'}
              </h3>

              {/* Days input for sequence */}
              {mode === 'sequence' && (
                <div className="form-group mb-4">
                  <label className="form-label">Days (comma-separated, match image order)</label>
                  <input id="days-input" className="form-input" value={days}
                    onChange={e => setDays(e.target.value)}
                    placeholder="0,7,14,21,28" />
                </div>
              )}

              <div
                id="upload-dropzone"
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
              >
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  multiple={mode === 'sequence'}
                  onChange={e => handleFiles(e.target.files)}
                />
                <div style={{ fontSize: 40, marginBottom: 8 }}>📤</div>
                <p style={{ fontWeight: 600, marginBottom: 4 }}>
                  {files.length ? `${files.length} file(s) selected` : 'Drop images here'}
                </p>
                <p style={{ color: '#7fa5a5', fontSize: 13 }}>
                  {mode === 'single' ? 'PNG, JPG, JPEG' : `Upload ${days.split(',').length} images in chronological order`}
                </p>
              </div>

              {files.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {files.map((f, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#7fa5a5' }}>
                      <span>🖼️</span>
                      <span style={{ color: '#e2f0f0', flex: 1 }}>{f.name}</span>
                      {mode === 'sequence' && (
                        <span className="badge badge-teal">Day {days.split(',')[i]?.trim()}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {mode === 'demo' && (
            <div className="card animate-fade-up" style={{ textAlign: 'center', padding: 40 }}>
              <span style={{ fontSize: 64 }}>🎬</span>
              <h3 style={{ fontWeight: 700, marginTop: 16, marginBottom: 8 }}>Demo Mode</h3>
              <p style={{ color: '#7fa5a5', fontSize: 14 }}>
                Runs the full 5-timepoint mock pipeline (Days 0, 7, 14, 21, 28) with realistic
                healing progression. No image upload needed — perfect for showcasing the system.
              </p>
            </div>
          )}

          {error && (
            <div style={{
              background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.4)',
              borderRadius: 10, padding: '12px 16px', color: '#f87171', fontSize: 14
            }}>
              ⚠️ {error}
            </div>
          )}

          <button id="run-analysis-btn" className="btn btn-primary" style={{ width: '100%', padding: 16 }}
            onClick={submit} disabled={loading}>
            {loading ? (
              <><div className="spinner" /><span>Running AI Analysis…</span></>
            ) : (
              <><span>▶</span><span>Run Analysis Pipeline</span></>
            )}
          </button>
        </div>
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
            <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back</button>
            <span className="badge badge-teal">{result.mode?.toUpperCase()} MODE</span>
          </div>
          <h1 className="section-title" style={{ fontSize: 28, margin: 0 }}>
            Analysis <span>Dashboard</span>
          </h1>
          <p style={{ color: '#7fa5a5', fontSize: 14, marginTop: 4 }}>
            Patient: <b style={{ color: '#e2f0f0' }}>{result.wound_id}</b> &nbsp;·&nbsp;
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
              <p style={{ fontSize: 11, color: '#7fa5a5', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k.replace(/_/g, ' ')}</p>
              <p style={{ fontWeight: 600, fontSize: 14, color: '#e2f0f0', marginTop: 2 }}>{String(v)}</p>
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
        if (p === 'landing') setResult(null)
      }} />

      {/* Global loading overlay */}
      {loading && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(6,13,27,0.85)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, backdropFilter: 'blur(8px)',
        }}>
          <div className="spinner" style={{ width: 48, height: 48, borderWidth: 4 }} />
          <p style={{ marginTop: 20, color: '#5cc4c3', fontWeight: 600, fontSize: 16 }}>
            Running AI Pipeline…
          </p>
          <p style={{ color: '#7fa5a5', fontSize: 13, marginTop: 4 }}>
            WoundVision → WoundScore → RiskFusion → HealCast → CareGuide
          </p>
        </div>
      )}

      {page === 'landing' && (
        <LandingPage onStart={() => setPage('upload')} onDemo={handleDemo} />
      )}
      {page === 'upload' && (
        <UploadPage onResult={handleResult} />
      )}
      {page === 'dashboard' && result && (
        <DashboardPage result={result} onBack={() => setPage('upload')} />
      )}
    </>
  )
}
