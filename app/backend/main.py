"""
WoundTrack Enhanced FastAPI Backend
Serves the enhanced wound analysis pipeline for the web application.
"""

import os
import sys
import json
import shutil
import tempfile
import logging
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Add parent to path so we can import src modules
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests
import base64
import uuid

import models
import crud
from database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Persistent Image Uploads Setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Import unified_pipeline directly (avoids src/__init__ which requires torch) ─
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "unified_pipeline",
    str(ROOT / "src" / "unified_pipeline.py"),
)
_mod = _ilu.module_from_spec(_spec)  # type: ignore
_spec.loader.exec_module(_mod)  # type: ignore
analyze_wound_progression = _mod.analyze_wound_progression
WoundSequenceAnalysis      = _mod.WoundSequenceAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── AI & Clinical Engines ──────────────────────────────────────────────

class OllamaWoundVision:
    def __init__(self, model_name="thiagomoraes/medgemma-1.5-4b-it:Q4_K_S"):
        self.model_name = model_name
        self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

    def analyze(self, image_path: str) -> Dict:
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
                
            prompt = (
                "Task: Extract visual attributes from the wound image. Output strictly JSON.\n"
                "Required format:\n"
                '{"dimensions": {"length_cm": number, "width_cm": number}, '
                '"tissue_composition": {"granulation_percent": number, "slough_percent": number, "eschar_percent": number}, '
                '"exudate": {"amount": "none|minimal|moderate|heavy", "type": "serous|sanguineous|purulent"}, '
                '"surrounding_skin": "intact|macerated|erythematous|indurated", '
                '"wound_bed_color": "description"}'
            )
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False,
                "format": "json"
            }
            
            msg = f"\n\n=========================================\n🚀 SENDING REQUEST TO OLLAMA MODEL: {self.model_name}\n=========================================\n"
            print(msg, flush=True)
            logger.info(msg)
            
            resp = requests.post(self.api_url, json=payload, timeout=60)
            resp.raise_for_status()
            
            raw_response = resp.json().get("response", "{}")
            
            res_msg = f"\n=========================================\n📥 RECEIVED OLLAMA RESPONSE:\n{raw_response}\n=========================================\n\n"
            print(res_msg, flush=True)
            logger.info(res_msg)
            
            return json.loads(raw_response)
        except Exception as e:
            logger.error(f"Ollama inference failed: {e}. Returning heuristic defaults.")
            # Fallback to defaults to prevent pipeline crash if Ollama isn't running
            return {
                "dimensions": {"length_cm": 4.0, "width_cm": 2.5},
                "tissue_composition": {"granulation_percent": 60, "slough_percent": 30, "eschar_percent": 10},
                "exudate": {"amount": "moderate", "type": "serous"},
                "surrounding_skin": "erythematous",
                "wound_bed_color": "red-pink"
            }


class ClinicalWoundScore:
    def calculate_push_score(self, features: Dict) -> int:
        area = features.get("area_cm2", 0)
        if area == 0:      area_score = 0
        elif area < 0.3:   area_score = 1
        elif area < 0.7:   area_score = 2
        elif area < 1.0:   area_score = 3
        elif area < 3.0:   area_score = 4
        elif area < 6.0:   area_score = 5
        elif area < 12.0:  area_score = 6
        elif area < 24.0:  area_score = 8
        else:              area_score = 10
        exudate_score  = max(3 - int(area / 5), 0)
        necrosis       = features.get("necrosis_pct", 0)
        if necrosis > 50:                                           tissue_score = 4
        elif necrosis > 25:                                         tissue_score = 3
        elif features.get("slough_pct", 0) > 50:                   tissue_score = 2
        elif features.get("granulation_pct", 0) > 75:              tissue_score = 0
        else:                                                       tissue_score = 1
        return area_score + exudate_score + tissue_score

    def calculate_wagner_grade(self, features: Dict) -> int:
        area    = features.get("area_cm2", 0)
        necrosis = features.get("necrosis_pct", 0)
        if area == 0:      return 0
        elif necrosis > 30: return 3
        elif area > 10:    return 2
        else:              return 1


class RiskFusionEngine:
    def assess_risk(self, patient_history: Dict, wound_features: Dict) -> float:
        base = 0.40
        if patient_history.get("HbA1c", 0) > 8.0: base += 0.15
        if patient_history.get("Smoker", False):    base += 0.10
        if patient_history.get("age", 0) > 70:      base += 0.05
        area = wound_features.get("area_cm2", 10)
        if area < 5: base -= 0.15
        if area < 2: base -= 0.10
        return round(max(0.10, min(0.90, base)), 3)


class HealCastPredictor:
    def predict_closure(self, days_history: List[int], area_history: List[float]) -> int:
        if len(area_history) < 2: return 60
        area_change   = area_history[-1] - area_history[0]
        days_elapsed  = days_history[-1] - days_history[0]
        if days_elapsed == 0 or area_change >= 0: return 90
        rate = abs(area_change) / days_elapsed
        if rate == 0: return 120
        return min(int(area_history[-1] / rate), 120)


class ActionableCareGuide:
    def determine_action(self, risk_prob: float, push_score: int, days_to_close: int,
                         granulation_pct: float = 50.0, slough_pct: float = 30.0,
                         exudate: str = "moderate", wound_area: float = 5.0) -> Dict:
        """Generate patient-specific care actions based on wound condition."""

        # ── Priority & rationale ────────────────────────────────────────
        if risk_prob > 0.7 or push_score > 12:
            priority  = "Urgent"
            rationale = (
                f"High risk (score {risk_prob:.2f}) with severe wound score ({push_score}). "
                f"Estimated closure in {days_to_close}d – immediate escalation needed."
            )
        elif risk_prob > 0.5 or push_score > 8:
            priority  = "Escalate"
            rationale = (
                f"Moderate risk (score {risk_prob:.2f}), PUSH score {push_score}. "
                f"Targeted wound care required; expected closure in {days_to_close} days."
            )
        else:
            priority  = "Routine"
            rationale = (
                f"Low risk (score {risk_prob:.2f}), PUSH score {push_score}. "
                f"Wound on track – estimate closure in {days_to_close} days."
            )

        # ── Build specific action list based on wound metrics ───────────
        actions: list[str] = []

        # Exudate-specific
        if exudate == "heavy":
            actions.append("Apply high-absorbency foam/alginate dressing; change q24–48h")
        elif exudate == "moderate":
            actions.append("Apply moisture-balancing dressing; change every 48–72h")
        else:
            actions.append("Maintain hydrocolloid dressing; change every 3–5 days")

        # Tissue-composition specific
        if slough_pct > 40:
            actions.append(f"Debride slough tissue ({slough_pct:.0f}% coverage) – autolytic or sharp")
        elif granulation_pct > 70:
            actions.append(f"Protect granulation bed ({granulation_pct:.0f}%) – avoid trauma during dressing change")
        else:
            actions.append("Monitor tissue balance; photograph wound weekly for comparison")

        # Risk-level specific
        if priority == "Urgent":
            actions.append("Refer to PHC doctor immediately for vascular/surgical assessment")
        elif priority == "Escalate":
            actions.append("Schedule follow-up within 48h; check for perilesional erythema/warmth")
        else:
            actions.append("Reinforce offloading footwear adherence and daily self-inspection")

        # Healing velocity specific
        if days_to_close > 90:
            actions.append("Consider specialist referral – prolonged healing forecast (>90 days)")
        elif days_to_close < 21 and priority == "Routine":
            actions.append("Wound progressing well – maintain current protocol")

        return {
            "priority": priority,
            "rationale": rationale,
            "actions": actions[:4],   # max 4 actions on dashboard
        }


# Singleton components
_wound_vision = OllamaWoundVision()
_wound_score  = ClinicalWoundScore()
_risk_fusion  = RiskFusionEngine()
_heal_cast    = HealCastPredictor()
_care_guide   = ActionableCareGuide()


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="WoundTrack AI API",
    description="AI-powered wound healing analysis and longitudinal tracking",
    version="2.0.0",
)

# Parse allowed origins from ENV (CORS Fix)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ──────────────────────────────────────────────────────────

class PatientInfo(BaseModel):
    patient_id: str = "PT-DEMO-001"
    age: int = 65
    HbA1c: float = 8.2
    Smoker: bool = False
    diabetes_duration_years: int = 15
    wound_location: str = "Plantar foot"


class TimePointMeta(BaseModel):
    day: int
    notes: str = ""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _analysis_to_dict(analysis: WoundSequenceAnalysis) -> Dict:
    """Convert WoundSequenceAnalysis to a JSON-serialisable dict."""
    m = analysis.longitudinal_metrics
    t = analysis.trends

    timepoints_out = []
    for tp in analysis.timepoints:
        timepoints_out.append({
            "day": tp.day,
            "notes": tp.notes,
            "wound_area": round(tp.wound_area, 3),
            "vision_analysis": tp.vision_analysis,
            "clinical_scores": tp.clinical_scores,
            "risk_assessment": tp.risk_assessment,
            "healing_forecast_days": tp.healing_forecast,
            "care_recommendation": tp.care_recommendation,
            "tissue_composition": tp.tissue_composition,
        })

    alerts_out = []
    for a in analysis.alerts:
        alerts_out.append({
            "severity": a.severity,
            "category": a.category,
            "message": a.message,
            "triggered_at_day": a.triggered_at_day,
            "recommendations": a.recommendations,
        })

    return {
        "wound_id": analysis.wound_id,
        "patient_history": analysis.patient_history,
        "overall_status": analysis.overall_status,
        "duration_days": analysis.timepoints[-1].day if analysis.timepoints else 0,
        "timepoints": timepoints_out,
        "longitudinal_metrics": {
            "area_progression": [round(x, 3) for x in m.area_progression],
            "area_changes": [round(x, 2) for x in m.area_changes],
            "total_area_change_pct": round(m.total_area_change_pct, 2),
            "push_score_history": m.push_score_history,
            "wagner_grade_history": m.wagner_grade_history,
            "risk_history": [round(x, 3) for x in m.risk_history],
            "avg_risk": round(m.avg_risk, 3),
            "healing_velocity": [round(v, 3) for v in m.healing_velocity],
            "avg_healing_velocity": round(
                float(np.mean(m.healing_velocity)) if m.healing_velocity else 0.0, 3
            ),
            "priority_history": m.priority_history,
            "tissue_trends": {k: [round(v2, 1) for v2 in v] for k, v in m.tissue_trends.items()},
            "risk_trend": m.risk_trend,
        },
        "trends": {
            "healing_trend": t.healing_trend,
            "area_trend": t.area_trend,
            "risk_trend": t.risk_trend,
            "acceleration": t.acceleration,
            "anomalies_detected": t.anomalies_detected,
        },
        "alerts": alerts_out,
        "summary": analysis.get_summary(),
    }


def _run_pipeline(sequence: List[Dict], patient_history: Dict) -> Dict:
    """Run the full unified pipeline."""
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=_wound_vision,
        wound_score=_wound_score,
        risk_fusion=_risk_fusion,
        heal_cast=_heal_cast,
        care_guide=_care_guide,
    )
    return _analysis_to_dict(analysis)


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()}

# Removed /api/demo endpoint per implementation plan



@app.post("/api/analyze")
async def analyze_single(
    file: UploadFile = File(...),
    patient_id: str = Form("PT-001"),
    name: str = Form(""),
    age: int = Form(65),
    HbA1c: float = Form(8.2),
    smoker: bool = Form(False),
    diabetes_duration_years: int = Form(0),
    wound_location: str = Form("Unknown"),
    db: Session = Depends(get_db)
):
    """
    Analyse a single uploaded wound image and append it to the patient's sequence in SQLite.
    Returns the updated longitudinal dashboard analysis.
    """
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    
    suffix = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if suffix not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG and PNG allowed.")

    # Generate a persistent valid path for the newly uploaded image
    unique_filename = f"{uuid.uuid4()}{suffix}"
    perm_path = UPLOAD_DIR / unique_filename

    with open(perm_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # DB: Get or create patient & wound
        patient_dict = {
            "patient_id": patient_id, "name": name, "age": age, "HbA1c": HbA1c, "smoker": smoker,
            "diabetes_duration_years": diabetes_duration_years
        }
        crud.get_or_create_patient(db, patient_dict)
        wound = crud.get_or_create_wound(db, patient_id, wound_location)
        
        # Load historical assessments for this patient
        past_assessments = crud.get_patient_assessments(db, patient_id)
        
        # Calculate sequential day offset (assume 7 days between visits for prototype if exact timestamps aren't sent)
        current_day = past_assessments[-1].day + 7 if past_assessments else 0
        
        # Build the sequential analysis input pipeline
        sequence = [{"image_path": a.image_path, "day": a.day, "notes": a.notes} for a in past_assessments]
        sequence.append({"image_path": str(perm_path), "day": current_day, "notes": "New upload via Dashboard"})
        
        # Run AI Pipeline on full longitudinal history
        result = _run_pipeline(sequence, patient_dict)
        result["mode"] = "sequence" if len(sequence) > 1 else "single"
        
        # Ensure we capture the VLM JSON string / features back from the pipeline
        latest_timepoint = result["timepoints"][-1]
        
        # Save this new assessment into the DB 
        crud.create_assessment(
            db, 
            wound_id=wound.id, 
            day=current_day, 
            analysis_data=latest_timepoint, 
            image_path=str(perm_path), 
            notes="New upload via Dashboard"
        )
        
        # Store per-patient status derived from this MedGemma assessment
        care_rec = latest_timepoint.get("care_recommendation", {})
        if isinstance(care_rec, dict):
            priority = care_rec.get("priority", "Routine")
            _status_map = {"Routine": "Healing Well", "Escalate": "Monitor Closely", "Urgent": "Critical - Needs Action"}
            ai_status = _status_map.get(priority, "Follow-up Needed")
            ai_summary = care_rec.get("rationale", "")
            ai_alerts = care_rec.get("actions", [])[:3]
        else:
            # Fallback from risk score
            risk_val = latest_timepoint.get("risk_assessment", 5)
            try:
                risk = float(risk_val) if not isinstance(risk_val, dict) else risk_val.get("risk_score", 5)
            except (TypeError, ValueError):
                risk = 5.0
            ai_status = "Healing Well" if risk < 4 else ("Monitor Closely" if risk < 7 else "Critical - Needs Action")
            ai_summary = ""
            ai_alerts = []
        crud.update_patient_status(db, patient_id, ai_status, ai_summary, ai_alerts)
        
        return result
    except Exception as e:
        logger.exception("Analysis pipeline error")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/api/patient/{patient_id}/history")
def get_patient_history(patient_id: str, db: Session = Depends(get_db)):
    """Fetch all sequential analyses for a patient without running inference again"""
    from src.unified_pipeline import WoundSequenceAnalysis, TimePointAnalysis
    import traceback
    
    try:
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        assessments = crud.get_patient_assessments(db, patient_id)
        
        if not assessments or not patient:
            return None
            
        patient_dict = {
            "patient_id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "HbA1c": patient.hba1c,
            "smoker": patient.smoker,
            "diabetes_duration_years": patient.diabetes_duration_years,
            "wound_location": "Unknown"
        }
        
        wound = db.query(models.Wound).filter(models.Wound.patient_id == patient_id).first()
        if wound:
            patient_dict["wound_location"] = wound.location
        
        wound_id = f"WOUND-{patient.id}-1"
        sequence_analysis = WoundSequenceAnalysis(wound_id=wound_id, patient_history=patient_dict)
        
        # Reconstruct the TimePointAnalysis history
        for a in assessments:
            data = a.analysis_data
            vision = data.get("vision_analysis", {})
            
            # Normalize risk_assessment: stored as float or dict {risk_score: x}
            raw_risk = data.get("risk_assessment")
            if isinstance(raw_risk, dict):
                risk_float = float(raw_risk.get("risk_score", raw_risk.get("risk", 0.5)))
            elif raw_risk is not None:
                try:
                    risk_float = float(raw_risk)
                except (TypeError, ValueError):
                    risk_float = 0.5
            else:
                risk_float = None

            # Build vision dict with standardised keys __post_init__ expects
            raw_tissue = vision.get("tissue_composition", {})
            # Normalise tissue keys (DB may store granulation/slough without _percent suffix)
            norm_tissue = {
                "granulation_percent": raw_tissue.get("granulation_percent",
                    raw_tissue.get("granulation", 0)),
                "slough_percent": raw_tissue.get("slough_percent",
                    raw_tissue.get("slough", 0)),
                "eschar_percent": raw_tissue.get("eschar_percent",
                    raw_tissue.get("eschar", 0)),
            }
            dims = vision.get("dimensions", {})

            tp = TimePointAnalysis(
                day=a.day,
                image_path=a.image_path,
                notes=a.notes,
                vision_analysis={"dimensions": dims, "tissue_composition": norm_tissue},
                clinical_scores=data.get("clinical_scores"),
                risk_assessment=risk_float,
                healing_forecast=data.get("healing_forecast_days"),
                care_recommendation=data.get("care_recommendation")
            )
            
            # The __post_init__ will extract wound_area and tissue_composition correctly
            sequence_analysis.add_timepoint(tp)
            
        sequence_analysis.analyze_trends()
        sequence_analysis.generate_alerts()
        sequence_analysis.set_overall_status()
        
        # Construct matching output dict format 
        result = {
            "wound_id": wound_id,
            "patient_history": patient_dict,
            "timepoints": [a.analysis_data for a in assessments],
            "overall_status": sequence_analysis.overall_status,
            "trends": sequence_analysis.trends.__dict__,
            "longitudinal_metrics": sequence_analysis.longitudinal_metrics.__dict__,
            "alerts": [a.__dict__ for a in sequence_analysis.alerts],
            "duration_days": assessments[-1].day - assessments[0].day if len(assessments) > 1 else 0,
            "mode": "sequence" if len(assessments) > 1 else "single"
        }
        return result
    except Exception as e:
        error_msg = f"Error reconstructing history: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/patients")
def get_all_patients(db: Session = Depends(get_db)):
    """Fetch all registered patients and a summary of their latest assessment."""
    patients = db.query(models.Patient).all()
    results = []
    for p in patients:
        assessments = crud.get_patient_assessments(db, p.id)
        num_visits = len(assessments)
        last_visit_day = assessments[-1].day if assessments else None
        
        status = "Follow-up Needed"
        if assessments:
            data = assessments[-1].analysis_data
            if data and "care_recommendation" in data:
                care_rec = data.get("care_recommendation", {})
                priority = care_rec.get("priority", "Routine")
                if priority == "Routine":
                    status = "Healing Well"
                elif priority == "Escalate":
                    status = "Monitor Closely"
                elif priority == "Urgent":
                    status = "Critical - Needs Action"
                else:
                    status = "Follow-up Needed"
            else:
                # Fallback to risk score heuristic if explicit care recommendation is missing
                if data and "risk_assessment" in data:
                    risk_val = data.get("risk_assessment", 5)
                    if isinstance(risk_val, dict):
                        risk = risk_val.get("risk_score", 5)
                    else:
                        try:
                            risk = float(risk_val)
                        except (TypeError, ValueError):
                            risk = 5.0
                    if risk < 4:
                        status = "Healing Well"
                    elif risk < 7:
                        status = "Monitor Closely"
                    else:
                        status = "Critical - Needs Action"

        # Use stored AI status (from MedGemma via last assessment), fallback to computation
        if p.last_status:
            status = p.last_status
            summary = p.last_summary or ""
            alert_actions = p.last_alerts or []
        else:
            status = "Follow-up Needed"
            summary = ""
            alert_actions = []
            if assessments:
                data = assessments[-1].analysis_data
                if data and "care_recommendation" in data:
                    care_rec = data.get("care_recommendation", {})
                    if isinstance(care_rec, dict):
                        priority = care_rec.get("priority", "Routine")
                        _status_map = {"Routine": "Healing Well", "Escalate": "Monitor Closely", "Urgent": "Critical - Needs Action"}
                        status = _status_map.get(priority, "Follow-up Needed")
                        summary = care_rec.get("rationale", "")
                        alert_actions = care_rec.get("actions", [])[:3]

        results.append({
            "patient_id": p.id,
            "name": p.name or "Unknown",
            "age": p.age,
            "num_visits": num_visits,
            "last_visit_day": last_visit_day,
            "status": status,
            "summary": summary,
            "alerts": alert_actions,
            "HbA1c": p.hba1c,
            "smoker": p.smoker,
            "diabetes_duration_years": p.diabetes_duration_years
        })
    return results

@app.post("/api/analyze-sequence")
async def analyze_sequence(
    files: List[UploadFile] = File(...),
    days: str = Form("0,7,14,21,28"),
    patient_id: str = Form("PT-001"),
    name: str = Form(""),
    age: int = Form(65),
    HbA1c: float = Form(8.2),
    smoker: bool = Form(False),
    diabetes_duration_years: int = Form(10),
    wound_location: str = Form("Plantar foot"),
    notes: str = Form(""),
):
    """
    Analyse a sequence of wound images for longitudinal tracking.
    Files and days must be in matching order.
    """
    day_list   = [int(d.strip()) for d in days.split(",")]
    tmp_paths  = []

    try:
        # Save uploaded files to temp
        for f in files:
            if f.size and f.size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="A file is too large. Max 10MB per file.")
            suffix = Path(f.filename).suffix.lower() if f.filename else ".jpg"
            if suffix not in [".jpg", ".jpeg", ".png"]:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPG and PNG allowed.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(f.file, tmp)
                tmp_paths.append(tmp.name)

        if len(tmp_paths) != len(day_list):
            raise HTTPException(
                status_code=400,
                detail=f"Number of files ({len(tmp_paths)}) must match number of days ({len(day_list)})"
            )

        patient_history = {
            "patient_id": patient_id, "age": age, "HbA1c": HbA1c, "Smoker": smoker,
            "diabetes_duration_years": diabetes_duration_years,
            "wound_location": wound_location,
        }

        sequence = [
            {"image_path": path, "day": day, "notes": notes or f"Assessment – Day {day}"}
            for path, day in zip(tmp_paths, day_list)
        ]

        result = _run_pipeline(sequence, patient_history)
        result["mode"] = "sequence"
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Sequence analysis error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for p in tmp_paths:
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
