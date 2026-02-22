import { useState, useEffect } from 'react';
import type { PatientListItem } from '../types';
import { fetchAllPatients } from '../api';

export function AshaHome({ onNewPatient, onRecent }: { onNewPatient: () => void, onRecent: (id: string) => void }) {
    const [patients, setPatients] = useState<PatientListItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAllPatients()
            .then(data => setPatients(data))
            .catch(err => console.error("Failed to fetch patients", err))
            .finally(() => setLoading(false));
    }, []);

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
                    <h3 className="section-title" style={{ fontSize: 16, margin: 0 }}>My Patients</h3>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '32px 0' }}>
                        <div className="spinner" style={{ width: 24, height: 24, borderWidth: 3, margin: '0 auto' }} />
                    </div>
                ) : patients.length > 0 ? (
                    <div className="timeline" style={{ marginTop: 16 }}>
                        {patients.map(p => (
                            <div key={p.patient_id} className="tp-item" style={{ cursor: 'pointer' }} onClick={() => onRecent(p.patient_id)}>
                                <div className="tp-day" style={{ background: 'linear-gradient(135deg, #10b981, #065f46)' }}>
                                    <span style={{ fontSize: 12 }}>PT</span>
                                    <span style={{ fontSize: 13 }}>{p.patient_id.replace('PT-', '').slice(0, 3)}</span>
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                                        <span style={{ fontWeight: 700, fontSize: 15, color: '#0f172a' }}>{p.name || p.patient_id}</span>
                                        <span className={`badge ${p.status.includes('Critical') ? 'badge-urgent' : p.status.includes('Monitor') ? 'badge-escalate' : 'badge-stable'}`}>
                                            {p.status}
                                        </span>
                                    </div>
                                    <p style={{ fontSize: 13, color: '#64748b', margin: 0 }}>
                                        {p.num_visits > 0 ? `Visits: ${p.num_visits} • Last visit: Day ${p.last_visit_day}` : "No assessments yet"}
                                    </p>
                                </div>
                                <div style={{ fontSize: 20, color: '#cbd5e1' }}>›</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '32px 0 16px', borderTop: '1px solid rgba(0,0,0,0.05)', marginTop: 24 }}>
                        <p style={{ color: '#64748b', fontSize: 14 }}>No patients found. Tap "+ Assess New Patient" to start a field visit.</p>
                    </div>
                )}
            </div>
        </div>
    )
}
