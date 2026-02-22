
export function LandingPage({ onLogin }: { onLogin: () => void }) {
    return (
        <>
            <section className="hero container">
                <div className="animate-fade-up">
                    <div className="hero-eyebrow">
                        <span>🤖</span> Powered by Google MedGemma 1.5 4B
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
                    </div>
                </div>
            </section>

            {/* Feature pills */}
            <div className="container">
                <div className="features-row animate-fade-up-delay">
                    {[
                        ['🔬', 'WoundVision (1.5 4B VLM)'],
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
                            desc: 'MedGemma 1.5 4B VLM analyses DFU images to extract dimensions, tissue composition, exudate characteristics, and surrounding skin condition.',
                            badge: '1.5 4B VLM',
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
                        {['Google MedGemma 1.5 4B', 'PyTorch + HuggingFace', 'FastAPI', 'React + Vite', 'Recharts'].map(t => (
                            <span className="badge badge-teal" key={t} style={{ fontSize: 13, padding: '6px 14px' }}>{t}</span>
                        ))}
                    </div>
                </div>
            </div>
        </>
    )
}
