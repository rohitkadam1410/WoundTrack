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
