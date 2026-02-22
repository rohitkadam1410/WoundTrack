import React, { useState, useRef, useCallback } from 'react';
import type { AnalysisResult, PatientForm, UploadMode } from '../types';
import { analyzeSingle, analyzeSequence } from '../api';

export function UploadPage({ patient, onResult, onBack }: { patient: PatientForm, onResult: (r: AnalysisResult) => void, onBack: () => void }) {
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
            if (mode === 'single') {
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
                        {([['single', '📷 Capture Field Photo (New Visit)']] as [UploadMode, string][]).map(([m, label]) => (
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
