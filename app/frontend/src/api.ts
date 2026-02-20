import axios from 'axios'
import type { AnalysisResult } from './types'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function runDemo(params?: {
    patient_id?: string
    age?: number
    HbA1c?: number
    smoker?: boolean
    days?: string
}): Promise<AnalysisResult> {
    const { data } = await axios.get<AnalysisResult>(`${BASE}/api/demo`, { params })
    return data
}

export async function analyzeSingle(
    file: File,
    patient: { patient_id: string; age: number; HbA1c: number; smoker: boolean }
): Promise<AnalysisResult> {
    const form = new FormData()
    form.append('file', file)
    form.append('patient_id', patient.patient_id)
    form.append('age', String(patient.age))
    form.append('HbA1c', String(patient.HbA1c))
    form.append('smoker', String(patient.smoker))
    const { data } = await axios.post<AnalysisResult>(`${BASE}/api/analyze`, form)
    return data
}

export async function analyzeSequence(
    files: File[],
    days: number[],
    patient: {
        patient_id: string; age: number; HbA1c: number; smoker: boolean
        diabetes_duration_years: number; wound_location: string
    }
): Promise<AnalysisResult> {
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    form.append('days', days.join(','))
    form.append('patient_id', patient.patient_id)
    form.append('age', String(patient.age))
    form.append('HbA1c', String(patient.HbA1c))
    form.append('smoker', String(patient.smoker))
    form.append('diabetes_duration_years', String(patient.diabetes_duration_years))
    form.append('wound_location', patient.wound_location)
    const { data } = await axios.post<AnalysisResult>(`${BASE}/api/analyze-sequence`, form)
    return data
}
