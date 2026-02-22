import type { AnalysisResult } from '../types';
import {
    AreaProgressionChart, TissueCompositionChart, PushScoreChart,
    RiskChart, HealingVelocityChart, TissueTrendChart,
    AlertsPanel, SummaryStats, TimepointTimeline,
} from '../components/Charts';

export function DashboardPage({ result, onBack, onNewUpload }: { result: AnalysisResult; onBack: () => void; onNewUpload?: () => void }) {
    return (
        <div className="container" style={{ paddingTop: 32, paddingBottom: 80 }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 32 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                        <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back to Home</button>
                        {onNewUpload && (
                            <button className="btn btn-primary btn-sm" onClick={onNewUpload}>📸 Capture New Assessment</button>
                        )}
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

            {/* Care Recommendations */}
            {(() => {
                const latest = result.timepoints?.[result.timepoints.length - 1];
                const rec = latest?.care_recommendation as Record<string, any> | undefined;
                if (!rec) return null;
                const priority = rec.priority as string;
                const badgeClass = priority === 'Urgent' ? 'badge-urgent' : priority === 'Escalate' ? 'badge-escalate' : 'badge-stable';
                const accentBg = priority === 'Urgent' ? '#fff1f2' : priority === 'Escalate' ? '#fffbeb' : '#f0fdf4';
                const accentCol = priority === 'Urgent' ? '#991b1b' : priority === 'Escalate' ? '#92400e' : '#065f46';
                return (
                    <div className="card mt-4" style={{ background: accentBg, border: `1px solid ${accentCol}22` }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                            <h3 className="section-title" style={{ fontSize: 16, margin: 0 }}>Care Recommendations</h3>
                            <span className={`badge ${badgeClass}`}>{priority}</span>
                        </div>
                        {rec.rationale && (
                            <p style={{ fontSize: 13, color: '#475569', fontStyle: 'italic', marginBottom: 12 }}>
                                {rec.rationale}
                            </p>
                        )}
                        {Array.isArray(rec.actions) && rec.actions.length > 0 && (
                            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
                                {(rec.actions as string[]).map((action, i) => (
                                    <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                                        <span style={{ color: accentCol, fontWeight: 700, fontSize: 16, lineHeight: 1.3 }}>→</span>
                                        <span style={{ fontSize: 13, color: '#1e293b', lineHeight: 1.5 }}>{action}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                );
            })()}

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
