import { useState } from 'react';
import type { PatientForm, AnalysisResult } from '../types';
import { fetchPatientHistory } from '../api';

export function PatientSearch({
    onPatientFound,
    onHistoryFound
}: {
    onPatientFound: (p: PatientForm) => void,
    onHistoryFound: (p: PatientForm, history: AnalysisResult) => void
}) {
    const [abha, setAbha] = useState('14-0453-2342-9901')
    const [loading, setLoading] = useState(false)

    const handleFetch = async () => {
        setLoading(true)
        try {
            await new Promise(r => setTimeout(r, 600)); // Mock API delay
            const p = {
                patient_id: 'PT-042', name: 'Ramesh (रमेश)', age: 65, HbA1c: 8.2, smoker: false,
                diabetes_duration_years: 15, wound_location: 'Plantar foot',
            };

            const history = await fetchPatientHistory(p.patient_id);
            if (history && history.timepoints && history.timepoints.length > 0) {
                onHistoryFound(p, history);
            } else {
                onPatientFound(p);
            }
        } catch (e) {
            console.error("Failed to fetch history from SQLite:", e);
            onPatientFound({
                patient_id: 'PT-042', name: 'Ramesh (रमेश)', age: 65, HbA1c: 8.2, smoker: false,
                diabetes_duration_years: 15, wound_location: 'Plantar foot',
            });
        } finally {
            setLoading(false)
        }
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
