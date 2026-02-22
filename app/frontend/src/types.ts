export interface Dimensions { length_cm: number; width_cm: number }
export interface TissueComposition {
    granulation_percent: number
    slough_percent: number
    eschar_percent: number
}
export interface Exudate { amount: string; type: string }
export interface VisionAnalysis {
    dimensions: Dimensions
    tissue_composition: TissueComposition
    exudate: Exudate
    surrounding_skin: string
    wound_bed_color: string
}
export interface ClinicalScores { push: number; wagner: number }
export interface CareRecommendation {
    priority: 'Routine' | 'Escalate' | 'Urgent'
    rationale: string
    actions: string[]
}
export interface TimePoint {
    day: number
    notes: string
    wound_area: number
    vision_analysis: VisionAnalysis
    clinical_scores: ClinicalScores
    risk_assessment: number
    healing_forecast_days: number
    care_recommendation: CareRecommendation
    tissue_composition: TissueComposition
}
export interface LongitudinalMetrics {
    area_progression: number[]
    area_changes: number[]
    total_area_change_pct: number
    push_score_history: number[]
    wagner_grade_history: number[]
    risk_history: number[]
    avg_risk: number
    healing_velocity: number[]
    avg_healing_velocity: number
    priority_history: string[]
    tissue_trends: Record<string, number[]>
    risk_trend: string
}
export interface Trends {
    healing_trend: string
    area_trend: string
    risk_trend: string
    acceleration: string
    anomalies_detected: unknown[]
}
export interface ClinicalAlert {
    severity: 'critical' | 'warning' | 'info'
    category: string
    message: string
    triggered_at_day: number
    recommendations: string[]
}
export interface AnalysisResult {
    wound_id: string
    patient_history: Record<string, unknown>
    overall_status: string
    duration_days: number
    timepoints: TimePoint[]
    longitudinal_metrics: LongitudinalMetrics
    trends: Trends
    alerts: ClinicalAlert[]
    summary: Record<string, unknown>
    mode: string
}

export type Page = 'landing' | 'login' | 'home' | 'patient_search' | 'upload' | 'dashboard'
export type UploadMode = 'single' | 'sequence'

export interface PatientForm {
    patient_id: string; age: number; HbA1c: number; smoker: boolean
    diabetes_duration_years: number; wound_location: string; name?: string
}

export interface PatientListItem {
    patient_id: string
    name: string
    age: number
    num_visits: number
    last_visit_day: number | null
    status: string
    summary: string
    alerts: string[]
    HbA1c: number
    smoker: boolean
    diabetes_duration_years: number
}
