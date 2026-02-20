// eslint-disable-next-line @typescript-eslint/no-unused-vars
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
    AreaChart, Area, ReferenceLine
} from 'recharts'
import type { AnalysisResult, ClinicalAlert } from '../types'

// ── Palette ──────────────────────────────────────────────────────
const COLORS = {
    teal: '#5cc4c3',
    emerald: '#34d399',
    amber: '#fbbf24',
    red: '#f87171',
    blue: '#60a5fa',
    purple: '#a78bfa',
    muted: '#7fa5a5',
}

const PIE_COLORS = [COLORS.emerald, COLORS.amber, COLORS.red]

// ── Tooltip helper ────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null
    return (
        <div style={{
            background: 'rgba(15,28,54,0.95)', border: '1px solid rgba(92,196,195,0.3)',
            borderRadius: 10, padding: '10px 14px', fontSize: 13,
        }}>
            <p style={{ color: COLORS.teal, fontWeight: 700, marginBottom: 4 }}>Day {label}</p>
            {payload.map((p: any, i: number) => (
                <p key={i} style={{ color: p.color || '#fff' }}>
                    {p.name}: <strong>{typeof p.value === 'number' ? p.value.toFixed(2) : p.value}</strong>
                </p>
            ))}
        </div>
    )
}

// ── Area Progression Chart ────────────────────────────────────────
export function AreaProgressionChart({ result }: { result: AnalysisResult }) {
    const data = result.timepoints.map(tp => ({
        day: tp.day,
        area: tp.wound_area,
        risk: +(tp.risk_assessment * 100).toFixed(1),
    }))

    return (
        <div className="card animate-fade-up">
            <h3 className="section-title">📏 Wound Area <span>Progression</span></h3>
            <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <defs>
                        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.teal} stopOpacity={0.35} />
                            <stop offset="95%" stopColor={COLORS.teal} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="day" tick={{ fill: COLORS.muted, fontSize: 12 }} label={{ value: 'Day', position: 'insideBottom', offset: -2, fill: COLORS.muted }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} unit=" cm²" />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="area" stroke={COLORS.teal} strokeWidth={2.5} fill="url(#areaGrad)" name="Area (cm²)" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── Tissue Composition Pie ────────────────────────────────────────
export function TissueCompositionChart({ result }: { result: AnalysisResult }) {
    const latest = result.timepoints.at(-1)
    if (!latest?.tissue_composition) return null
    const tc = latest.tissue_composition
    const data = [
        { name: 'Granulation', value: tc.granulation_percent },
        { name: 'Slough', value: tc.slough_percent },
        { name: 'Eschar', value: tc.eschar_percent },
    ]

    return (
        <div className="card animate-fade-up" style={{ animationDelay: '0.05s' }}>
            <h3 className="section-title">🧬 Tissue <span>Composition</span></h3>
            <p style={{ fontSize: 12, color: COLORS.muted, marginBottom: 8 }}>Latest timepoint</p>
            <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                    <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                        dataKey="value" paddingAngle={3}>
                        {data.map((_, i) => (
                            <Cell key={i} fill={PIE_COLORS[i]} />
                        ))}
                    </Pie>
                    <Tooltip formatter={(v: any) => `${v}%`} />
                    <Legend iconType="circle" iconSize={10}
                        formatter={(v: string) => <span style={{ color: COLORS.muted, fontSize: 12 }}>{v}</span>} />
                </PieChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── PUSH Score Chart ──────────────────────────────────────────────
export function PushScoreChart({ result }: { result: AnalysisResult }) {
    const data = result.timepoints.map(tp => ({
        day: tp.day,
        push: tp.clinical_scores?.push ?? 0,
        wagner: tp.clinical_scores?.wagner ?? 0,
    }))

    return (
        <div className="card animate-fade-up" style={{ animationDelay: '0.10s' }}>
            <h3 className="section-title">🏥 Clinical <span>Scores</span></h3>
            <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="day" tick={{ fill: COLORS.muted, fontSize: 12 }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend iconType="circle" iconSize={10}
                        formatter={(v: string) => <span style={{ color: COLORS.muted, fontSize: 12 }}>{v}</span>} />
                    <Bar dataKey="push" name="PUSH Score" fill={COLORS.blue} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="wagner" name="Wagner Grade" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── Risk Trajectory Chart ─────────────────────────────────────────
export function RiskChart({ result }: { result: AnalysisResult }) {
    const data = result.timepoints.map(tp => ({
        day: tp.day,
        risk: +(tp.risk_assessment * 100).toFixed(1),
    }))

    return (
        <div className="card animate-fade-up" style={{ animationDelay: '0.15s' }}>
            <h3 className="section-title">⚠️ Amputation <span>Risk</span></h3>
            <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="day" tick={{ fill: COLORS.muted, fontSize: 12 }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} unit="%" domain={[0, 100]} />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine y={70} stroke={COLORS.red} strokeDasharray="4 4" label={{ value: 'High', fill: COLORS.red, fontSize: 11 }} />
                    <ReferenceLine y={50} stroke={COLORS.amber} strokeDasharray="4 4" label={{ value: 'Mod', fill: COLORS.amber, fontSize: 11 }} />
                    <Line type="monotone" dataKey="risk" stroke={COLORS.amber} strokeWidth={2.5}
                        dot={{ fill: COLORS.amber, r: 4 }} name="Risk (%)" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── Healing Velocity Chart ────────────────────────────────────────
export function HealingVelocityChart({ result }: { result: AnalysisResult }) {
    const vels = result.longitudinal_metrics.healing_velocity
    const days = result.timepoints
    const data = vels.map((v, i) => ({
        label: `Day ${days[i]?.day}→${days[i + 1]?.day}`,
        velocity: +v.toFixed(3),
    }))

    return (
        <div className="card animate-fade-up" style={{ animationDelay: '0.20s' }}>
            <h3 className="section-title">⚡ Healing <span>Velocity</span></h3>
            <p style={{ fontSize: 12, color: COLORS.muted, marginBottom: 8 }}>cm² / week (negative = healing)</p>
            <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="label" tick={{ fill: COLORS.muted, fontSize: 10 }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} unit=" cm²" />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine y={0} stroke="rgba(255,255,255,0.2)" />
                    <Bar dataKey="velocity" name="Velocity" fill={COLORS.emerald}
                        radius={[4, 4, 0, 0]}
                        label={false}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── Tissue Trend Over Time ────────────────────────────────────────
export function TissueTrendChart({ result }: { result: AnalysisResult }) {
    const tt = result.longitudinal_metrics.tissue_trends
    const days = result.timepoints.map(tp => tp.day)
    const data = days.map((day, i) => ({
        day,
        granulation: tt['granulation_percent']?.[i] ?? 0,
        slough: tt['slough_percent']?.[i] ?? 0,
        eschar: tt['eschar_percent']?.[i] ?? 0,
    }))

    return (
        <div className="card animate-fade-up" style={{ animationDelay: '0.25s' }}>
            <h3 className="section-title">📊 Tissue <span>Evolution</span></h3>
            <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="day" tick={{ fill: COLORS.muted, fontSize: 12 }} />
                    <YAxis tick={{ fill: COLORS.muted, fontSize: 12 }} unit="%" />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend iconType="circle" iconSize={10}
                        formatter={(v: string) => <span style={{ color: COLORS.muted, fontSize: 12 }}>{v}</span>} />
                    <Line type="monotone" dataKey="granulation" stroke={COLORS.emerald} strokeWidth={2} dot={{ r: 3 }} name="Granulation %" />
                    <Line type="monotone" dataKey="slough" stroke={COLORS.amber} strokeWidth={2} dot={{ r: 3 }} name="Slough %" />
                    <Line type="monotone" dataKey="eschar" stroke={COLORS.red} strokeWidth={2} dot={{ r: 3 }} name="Eschar %" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

// ── Clinical Alerts Panel ─────────────────────────────────────────
export function AlertsPanel({ alerts }: { alerts: ClinicalAlert[] }) {
    if (!alerts.length) {
        return (
            <div className="card animate-fade-up">
                <h3 className="section-title">🚦 Clinical <span>Alerts</span></h3>
                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                    <span style={{ fontSize: 32 }}>✅</span>
                    <p style={{ color: '#34d399', fontWeight: 600, marginTop: 8 }}>No clinical alerts triggered</p>
                    <p style={{ color: '#7fa5a5', fontSize: 13 }}>Wound is progressing within expected parameters</p>
                </div>
            </div>
        )
    }

    const icon = (s: string) => s === 'critical' ? '🔴' : s === 'warning' ? '🟡' : 'ℹ️'

    return (
        <div className="card animate-fade-up">
            <h3 className="section-title">🚦 Clinical <span>Alerts</span></h3>
            <div className="timeline" style={{ flexDirection: 'column', gap: 10 }}>
                {alerts.map((a, i) => (
                    <div key={i} className={`alert-item ${a.severity}`}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                            <span>{icon(a.severity)}</span>
                            <span style={{ fontWeight: 700, fontSize: 14 }}>{a.category}</span>
                            <span className={`badge badge-${a.severity}`}>{a.severity}</span>
                            <span style={{ marginLeft: 'auto', color: '#7fa5a5', fontSize: 12 }}>Day {a.triggered_at_day}</span>
                        </div>
                        <p style={{ fontSize: 14, color: '#e2f0f0', marginBottom: a.recommendations.length ? 8 : 0 }}>{a.message}</p>
                        {a.recommendations.slice(0, 3).map((r, j) => (
                            <p key={j} style={{ fontSize: 12, color: '#7fa5a5', paddingLeft: 16 }}>• {r}</p>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    )
}

// ── Summary Stats Row ─────────────────────────────────────────────
export function SummaryStats({ result }: { result: AnalysisResult }) {
    const m = result.longitudinal_metrics
    const statusColors: Record<string, string> = {
        healing_well: '#34d399', improving_high_risk: '#fbbf24',
        deteriorating: '#f87171', stagnant_needs_intervention: '#f87171',
        stable_small: '#60a5fa', unknown: '#7fa5a5',
    }
    const statusLabel: Record<string, string> = {
        healing_well: 'Healing Well', improving_high_risk: 'Improving (High Risk)',
        deteriorating: 'Deteriorating', stagnant_needs_intervention: 'Stagnant – Needs Intervention',
        stable_small: 'Stable (Small Wound)', unknown: 'Unknown',
    }
    const statusColor = statusColors[result.overall_status] || '#7fa5a5'
    const areaChange = m.total_area_change_pct
    const trendBadge = (t: string) => {
        if (t === 'improving') return 'badge-improving'
        if (t === 'worsening') return 'badge-worsening'
        return 'badge-stable'
    }

    return (
        <div className="animate-fade-up">
            {/* Status banner */}
            <div className="card mb-4" style={{ border: `1px solid ${statusColor}33`, background: `${statusColor}0d` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                    <div>
                        <p style={{ fontSize: 12, color: '#7fa5a5', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Overall Status</p>
                        <p style={{ fontSize: 24, fontWeight: 800, color: statusColor, marginTop: 2 }}>
                            {statusLabel[result.overall_status] || result.overall_status}
                        </p>
                    </div>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                        <span className={`badge ${trendBadge(result.trends.healing_trend)}`}>
                            Healing: {result.trends.healing_trend}
                        </span>
                        <span className={`badge ${trendBadge(result.trends.risk_trend)}`}>
                            Risk: {result.trends.risk_trend}
                        </span>
                    </div>
                </div>
            </div>

            {/* Stat grid */}
            <div className="grid-4">
                <div className="stat-card">
                    <span className="stat-label">Area Change</span>
                    <span className="stat-value" style={{ color: areaChange <= 0 ? '#34d399' : '#f87171' }}>
                        {areaChange > 0 ? '+' : ''}{areaChange.toFixed(1)}%
                    </span>
                    <span className="stat-sub">Initial → Current</span>
                    <div className="progress-wrap mt-2">
                        <div className="progress-bar"
                            style={{
                                width: `${Math.min(Math.abs(areaChange), 100)}%`,
                                background: areaChange <= 0 ? '#34d399' : '#f87171',
                            }} />
                    </div>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Avg Risk</span>
                    <span className="stat-value" style={{ color: m.avg_risk > 0.6 ? '#f87171' : m.avg_risk > 0.4 ? '#fbbf24' : '#34d399' }}>
                        {(m.avg_risk * 100).toFixed(0)}%
                    </span>
                    <span className="stat-sub">Amputation Risk</span>
                    <div className="progress-wrap mt-2">
                        <div className="progress-bar"
                            style={{
                                width: `${(m.avg_risk * 100)}%`,
                                background: m.avg_risk > 0.6 ? '#f87171' : m.avg_risk > 0.4 ? '#fbbf24' : '#34d399',
                            }} />
                    </div>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Healing Velocity</span>
                    <span className="stat-value" style={{ color: '#5cc4c3' }}>
                        {m.avg_healing_velocity.toFixed(2)}
                    </span>
                    <span className="stat-sub">cm² / week avg</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">Timepoints</span>
                    <span className="stat-value">{result.timepoints.length}</span>
                    <span className="stat-sub">{result.duration_days}-day span</span>
                </div>
            </div>
        </div>
    )
}

// ── Timepoint Timeline ───────────────────────────────────────────
export function TimepointTimeline({ result }: { result: AnalysisResult }) {
    const priorityClass: Record<string, string> = {
        Routine: 'badge-routine', Escalate: 'badge-escalate', Urgent: 'badge-urgent'
    }
    return (
        <div className="card animate-fade-up">
            <h3 className="section-title">📅 Visit <span>Timeline</span></h3>
            <div className="timeline">
                {result.timepoints.map((tp, i) => (
                    <div key={i} className="tp-item">
                        <div className="tp-day">
                            <span style={{ fontSize: 16 }}>D</span>
                            <span style={{ fontSize: 14 }}>{tp.day}</span>
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                                <span style={{ fontWeight: 700, fontSize: 14 }}>{tp.notes || `Assessment ${i + 1}`}</span>
                                <span className={`badge ${priorityClass[tp.care_recommendation?.priority] || 'badge-teal'}`}>
                                    {tp.care_recommendation?.priority || '—'}
                                </span>
                                <span className="badge badge-teal">{tp.wound_area.toFixed(2)} cm²</span>
                            </div>
                            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                                <span style={{ fontSize: 12, color: '#7fa5a5' }}>PUSH: <b style={{ color: '#e2f0f0' }}>{tp.clinical_scores?.push ?? '—'}</b></span>
                                <span style={{ fontSize: 12, color: '#7fa5a5' }}>Wagner: <b style={{ color: '#e2f0f0' }}>{tp.clinical_scores?.wagner ?? '—'}</b></span>
                                <span style={{ fontSize: 12, color: '#7fa5a5' }}>Risk: <b style={{ color: '#e2f0f0' }}>{((tp.risk_assessment ?? 0) * 100).toFixed(0)}%</b></span>
                                <span style={{ fontSize: 12, color: '#7fa5a5' }}>Forecast: <b style={{ color: '#e2f0f0' }}>{tp.healing_forecast_days}d to closure</b></span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
