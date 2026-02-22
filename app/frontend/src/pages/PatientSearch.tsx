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
    const [formData, setFormData] = useState<PatientForm>({
        patient_id: '',
        name: '',
        age: 0,
        HbA1c: 0,
        smoker: false,
        diabetes_duration_years: 0,
        wound_location: ''
    });
    const [loading, setLoading] = useState(false);

    const handleLookup = async () => {
        if (!formData.patient_id) return;
        setLoading(true);
        try {
            const history = await fetchPatientHistory(formData.patient_id);
            if (history && history.patient_history) {
                const ph = history.patient_history as Record<string, any>;
                setFormData(prev => ({
                    ...prev,
                    name: ph.name || '',
                    age: ph.age || prev.age,
                    HbA1c: ph.HbA1c || prev.HbA1c,
                    smoker: ph.smoker || false,
                    diabetes_duration_years: ph.diabetes_duration_years || prev.diabetes_duration_years,
                    wound_location: ph.wound_location || prev.wound_location
                }));
            } else {
                alert("No existing patient found with this ID.");
            }
        } catch (e) {
            console.error("Lookup failed:", e);
            alert("Error fetching patient details.");
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const history = await fetchPatientHistory(formData.patient_id);
            if (history && history.timepoints && history.timepoints.length > 0) {
                onHistoryFound(formData, history);
            } else {
                onPatientFound(formData);
            }
        } catch (e) {
            console.error("Failed to fetch history:", e);
            onPatientFound(formData);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="container" style={{ paddingTop: 60, paddingBottom: 60, maxWidth: 600 }}>
            <div className="card animate-fade-up">
                <h3 className="section-title" style={{ fontSize: 22, margin: 0 }}>Patient <span>Registration / Lookup</span></h3>
                <p style={{ color: '#64748b', fontSize: 14, marginTop: 8, marginBottom: 24 }}>
                    Enter patient details to start a new assessment or fetch their history.
                </p>

                <form onSubmit={handleSubmit}>
                    <div className="grid-2" style={{ gap: '16px' }}>
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label className="form-label">Patient ID</label>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <input required className="form-input" value={formData.patient_id} onChange={e => setFormData({ ...formData, patient_id: e.target.value })} placeholder="e.g. PT-042" />
                                <button type="button" className="btn btn-outline" onClick={handleLookup} disabled={loading || !formData.patient_id} style={{ whiteSpace: 'nowrap' }}>
                                    Search ID
                                </button>
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Name</label>
                            <input required className="form-input" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Age</label>
                            <input required type="number" className="form-input" value={formData.age || ''} onChange={e => setFormData({ ...formData, age: Number(e.target.value) })} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Wound Location / Type</label>
                            <input required className="form-input" value={formData.wound_location} onChange={e => setFormData({ ...formData, wound_location: e.target.value })} placeholder="e.g. Right lower leg, Burn" />
                        </div>

                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label className="form-label" style={{ marginBottom: 8 }}>Additional Context (Optional)</label>
                            <div className="grid-3" style={{ gap: '12px' }}>
                                <div>
                                    <label style={{ fontSize: 12, color: '#64748b' }}>HbA1c</label>
                                    <input type="number" step="0.1" className="form-input" value={formData.HbA1c || ''} onChange={e => setFormData({ ...formData, HbA1c: Number(e.target.value) })} />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: '#64748b' }}>Diabetes (Years)</label>
                                    <input type="number" className="form-input" value={formData.diabetes_duration_years || ''} onChange={e => setFormData({ ...formData, diabetes_duration_years: Number(e.target.value) })} />
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', paddingTop: 20 }}>
                                    <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                                        <input type="checkbox" checked={formData.smoker} onChange={e => setFormData({ ...formData, smoker: e.target.checked })} />
                                        Smoker
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary w-full mt-6" disabled={loading}>
                        {loading ? (
                            <><div className="spinner" style={{ width: 16, height: 16, borderTopColor: '#fff', borderWidth: 2 }} /><span>Processing...</span></>
                        ) : (
                            <><span>✅</span><span>Save & Continue</span></>
                        )}
                    </button>
                </form>
            </div>
        </div>
    )
}
