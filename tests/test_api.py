from fastapi.testclient import TestClient
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.getcwd())

from src.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("src.api.MedGemmaWoundAnalyzer")
def test_analyze_wound_mock(MockAnalyzer):
    # Setup mock
    mock_instance = MockAnalyzer.return_value
    mock_instance.analyze_wound_image.return_value = {
        "dimensions": {"length_cm": 5.0, "width_cm": 3.0},
        "tissue_composition": {"granulation": 60, "slough": 40, "eschar": 0},
        "exudate": {"amount": "minimal", "type": "serous"},
        "surrounding_skin": "intact",
        "wound_bed_color": "pink"
    }
    
    # Needs to patch module.models dict or rely on lifespan logic
    # Since lifespan runs on startup, 'models' global is populated
    # But TestClient with lifespan should handle it. 
    # However, patching MedGemmaWoundAnalyzer class *before* app startup logic might be tricky if lifespan is already evaluated or if import happens at top level.
    # In src/api.py, MedGemmaWoundAnalyzer is imported at top level.
    # Lifespan instantiates it.
    
    # We'll use a slightly different approach: patch the global 'models' dict in src.api
    with patch("src.api.models", {"analyzer": mock_instance}):
        # Create dummy file
        with open("dummy.jpg", "wb") as f:
            f.write(b"fake image data")
            
        try:
            with open("dummy.jpg", "rb") as f:
                response = client.post(
                    "/analyze?use_mock=true", 
                    files={"file": ("dummy.jpg", f, "image/jpeg")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert "dimensions" in data
            assert data["dimensions"]["length_cm"] == 5.0
        finally:
            if os.path.exists("dummy.jpg"):
                os.remove("dummy.jpg")

def test_classify_wound():
    # Test valid request
    payload = {
        "analysis_t0": {
            "dimensions": {"length_cm": 5.0, "width_cm": 5.0},
            "tissue_composition": {"granulation": 50, "slough": 50}
        },
        "analysis_t1": {
            "dimensions": {"length_cm": 4.0, "width_cm": 4.0}, # Improved
            "tissue_composition": {"granulation": 70, "slough": 30}
        },
        "nurse_notes": "Looks better"
    }
    
    response = client.post("/classify?use_mock=true", json=payload)
    # Even without patching, if use_mock=True, the real class returns data
    # But we need 'analyzer' in models dict.
    # The TestClient(app) calls lifespan, which sets models['analyzer'] = MedGemmaWoundAnalyzer()
    # So this should work with the real class's mock method.
    
    if response.status_code != 200:
        print("Error:", response.text)
        
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    # Logic in code: area change < -10 -> Improving
    # 25 vs 16 -> decrease by ~36% -> Improving
    assert data["classification"] == "Improving"

def test_longitudinal_summary():
    payload = {
        "sequence_data": [
            {
                "day": 0,
                "analysis": {
                    "dimensions": {"length_cm": 5.0, "width_cm": 5.0},
                    "tissue_composition": {"granulation": 50}
                }
            },
            {
                "day": 7,
                "analysis": {
                    "dimensions": {"length_cm": 4.0, "width_cm": 4.0},
                    "tissue_composition": {"granulation": 70}
                }
            }
        ]
    }
    
    response = client.post("/longitudinal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_trend" in data
    assert data["num_timepoints"] == 2

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_health_check()
        test_classify_wound()
        test_longitudinal_summary()
        # Skipped file upload test in manual run to avoid complex patching setup
        print("Basic tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)
