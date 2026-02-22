from sqlalchemy.orm import Session
import models
from typing import Dict, List, Any

def get_or_create_patient(db: Session, patient_dict: dict) -> models.Patient:
    patient_id = patient_dict.get("patient_id", "PT-UNKNOWN")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        patient = models.Patient(
            id=patient_id,
            name=patient_dict.get("name"),
            age=patient_dict.get("age", 0),
            hba1c=patient_dict.get("HbA1c", 0.0),
            smoker=patient_dict.get("smoker", False),
            diabetes_duration_years=patient_dict.get("diabetes_duration_years", 0)
        )
        db.add(patient)
    else:
        # Update blank/missing fields
        updated = False
        if not patient.name or patient.name == "Unknown":
            new_name = patient_dict.get("name")
            if new_name and new_name != "Unknown":
                patient.name = new_name
                updated = True
        if updated:
            db.add(patient)
            
    db.commit()
    db.refresh(patient)
    return patient

def get_or_create_wound(db: Session, patient_id: str, location: str) -> models.Wound:
    wound = db.query(models.Wound).filter(
        models.Wound.patient_id == patient_id, 
        models.Wound.location == location
    ).first()
    
    if not wound:
        wound = models.Wound(patient_id=patient_id, location=location)
        db.add(wound)
        db.commit()
        db.refresh(wound)
    return wound

def create_assessment(db: Session, wound_id: int, day: int, analysis_data: Dict, image_path: str = None, notes: str = None) -> models.WoundAssessment:
    assessment = models.WoundAssessment(
        wound_id=wound_id,
        day=day,
        analysis_data=analysis_data,
        image_path=image_path,
        notes=notes
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

def get_patient_assessments(db: Session, patient_id: str) -> List[models.WoundAssessment]:
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        return []
    
    # Return all assessments flattened (for prototype, assumes 1 wound per patient for simplicity)
    assessments = []
    for wound in patient.wounds:
        assessments.extend(wound.assessments)
        
    # Sort by day
    assessments.sort(key=lambda x: x.day)
    return assessments

def update_patient_status(db: Session, patient_id: str, status: str, summary: str, alerts: list):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if patient:
        patient.last_status = status
        patient.last_summary = summary
        patient.last_alerts = alerts
        db.add(patient)
        db.commit()
