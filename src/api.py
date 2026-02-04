from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import shutil
import tempfile
import os
import json
from contextlib import asynccontextmanager

from src.medgemma_inference import MedGemmaWoundAnalyzer
from src.preprocessing import WoundImagePreprocessor
from src.longitudinal_analysis import generate_progression_summary

# Global state
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup"""
    print("Loading MedGemma models...")
    # Initialize with None for now - real loading requires significant resources
    # In production, we would load the actual 4B/27B models here
    # or pass paths/IDs via env vars.
    # For now, we rely on the class's ability to mock or load if ID provided.
    
    # Example logic to load if env var is set
    model_id_4b = os.getenv("MEDGEMMA_4B_ID", "google/paligemma-3b-mix-224") 
    
    # We will instantiate the analyzer here.
    # Note: Loading the full model takes time and GPU RAM. 
    # For dev/demo, we might want to default to mock=True logic usage
    # but the Analyzer object needs to exist.
    
    # If we want to support real inference in the API, we need to load them:
    # try:
    #     processor_4b = AutoProcessor.from_pretrained(model_id_4b)
    #     model_4b = PaliGemmaForConditionalGeneration.from_pretrained(model_id_4b).to("cuda")
    #     models["analyzer"] = MedGemmaWoundAnalyzer(model_4b=model_4b, processor_4b=processor_4b)
    # except:
    models["analyzer"] = MedGemmaWoundAnalyzer() # Default fallback (potentially mocks or empty)
    
    print("Models loaded.")
    yield
    print("Shutting down...")
    models.clear()

app = FastAPI(title="WoundTrack API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WoundResponse(BaseModel):
    dimensions: Dict[str, float]
    tissue_composition: Dict[str, float]
    exudate: Dict[str, str]
    surrounding_skin: str
    wound_bed_color: str

class LongitudinalRequest(BaseModel):
    sequence_data: List[Dict] # List of timepoint analyses

class ClassificationRequest(BaseModel):
    analysis_t0: Dict
    analysis_t1: Dict
    nurse_notes: Optional[str] = ""

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=WoundResponse)
async def analyze_wound(file: UploadFile = File(...), use_mock: bool = False):
    """
    Analyze an uploaded wound image.
    """
    analyzer = models.get("analyzer")
    if not analyzer:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Preprocessing (optional, but good practice if model expects specific size)
        # preprocessor = WoundImagePreprocessor()
        # processed_img = preprocessor.preprocess(tmp_path)
        # processed_img.save(tmp_path) # Overwrite or save to new path
        
        result = analyzer.analyze_wound_image(tmp_path, use_mock=use_mock)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/classify")
async def classify_progress(request: ClassificationRequest, use_mock: bool = True):
    """
    Classify wound progression between two timepoints.
    """
    analyzer = models.get("analyzer")
    if not analyzer:
        raise HTTPException(status_code=503, detail="Model not initialized")
        
    try:
        result = analyzer.classify_wound_status(
            request.analysis_t0, 
            request.analysis_t1, 
            request.nurse_notes,
            use_mock=use_mock
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/longitudinal")
async def longitudinal_summary(request: LongitudinalRequest):
    """
    Generate summary stats for a sequence of wound analyses.
    """
    try:
        summary = generate_progression_summary(request.sequence_data)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
