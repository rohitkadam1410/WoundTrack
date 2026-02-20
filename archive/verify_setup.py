import sys
import os
sys.path.append(os.getcwd())

try:
    from src.medgemma_inference import MedGemmaWoundAnalyzer
    analyzer = MedGemmaWoundAnalyzer()
    print("Successfully imported and instantiated MedGemmaWoundAnalyzer")
    
    # Test mock path
    res = analyzer.analyze_wound_image("sample_wound.jpg", use_mock=True)
    print("Mock analysis result keys:", res.keys())
    
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
