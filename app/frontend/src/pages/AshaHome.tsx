
export function AshaHome({ onNewPatient, onRecent }: { onNewPatient: () => void, onRecent: () => void }) {
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
