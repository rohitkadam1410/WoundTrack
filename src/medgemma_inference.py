"""
MedGemma model inference wrappers for WoundTrack
"""
import json
from typing import Dict, Optional
from PIL import Image
import torch
import re

# Prompt templates
WOUND_DESCRIPTION_PROMPT = """
<image_analysis_task>
Context: Research data extraction.
Task: Extract visual attributes from the wound image.
Output Format: Pure JSON only. No conversational text.

Required JSON Structure:
{
  "dimensions": {"length_cm": <number>, "width_cm": <number>},
  "tissue_composition": {"granulation_percent": <number>, "slough_percent": <number>, "eschar_percent": <number>},
  "exudate": {"amount": "none|minimal|moderate|heavy", "type": "serous|sanguineous|purulent"},
  "surrounding_skin": "intact|macerated|erythematous|indurated",
  "wound_bed_color": "<description>"
}

Instructions:
1. Estimate dimensions based on standard scale references if present, otherwise approximate.
2. Analyze pixel color distributions to estimate tissue percentages.
3. Classify exudate and skin appearance based on visual texture.
4. RETURN ONLY THE JSON OBJECT.
</image_analysis_task>
"""

CLASSIFICATION_PROMPT_TEMPLATE = """
Given the wound progression data and nurse notes, classify the healing status:

Timepoint 1 (Day {day0}): {desc0}
Timepoint 2 (Day {day1}): {desc1}
Nurse Notes: {notes}

Classification: Improving / Stable / Worsening
Confidence: 0-100%
Rationale: [brief explanation]

Guidelines:
- Improving: Wound area decreasing, granulation increasing, exudate decreasing
- Stable: Minimal changes in dimensions and tissue composition  
- Worsening: Wound expanding, necrotic tissue increasing, signs of infection

Respond in JSON format:
{
  "classification": "...",
  "confidence": X,
  "rationale": "..."
}
"""


class MedGemmaWoundAnalyzer:
    """Wrapper for MedGemma inference on wound images"""
    
    def __init__(self, model_4b=None, model_27b=None, tokenizer_4b=None, tokenizer_27b=None, processor_4b=None):
        """
        Initialize MedGemma models
        
        Args:
            model_4b: MedGemma 4B model for description (VLM)
            model_27b: MedGemma 27B model for classification (LLM)
            tokenizer_4b: Tokenizer for 4B model (optional if processor provided)
            tokenizer_27b: Tokenizer for 27B model
            processor_4b: Processor for 4B model (handles images)
        """
        self.model_4b = model_4b
        self.model_27b = model_27b
        self.tokenizer_4b = tokenizer_4b
        self.tokenizer_27b = tokenizer_27b
        self.processor_4b = processor_4b
    
    def analyze_wound_image(self, image_path: str, use_mock: bool = True) -> Dict:
        """
        Extract wound characteristics using MedGemma 4B
        
        Args:
            image_path: Path to wound image
            use_mock: Use mock data for testing
            
        Returns:
            dict: Structured wound analysis
        """
        if use_mock or self.model_4b is None:
            # Mock analysis for development
            import numpy as np
            return {
                "dimensions": {
                    "length_cm": round(np.random.uniform(2, 8), 1),
                    "width_cm": round(np.random.uniform(1.5, 6), 1)
                },
                "tissue_composition": {
                    "granulation": int(np.random.randint(40, 80)),
                    "slough": int(np.random.randint(10, 40)),
                    "eschar": int(np.random.randint(0, 20))
                },
                "exudate": {
                    "amount": np.random.choice(["minimal", "moderate", "heavy"]),
                    "type": "serous"
                },
                "surrounding_skin": "intact",
                "wound_bed_color": "pink-red"
            }
        
        try:
            image = Image.open(image_path).convert("RGB")
            
            # Prepare inputs
            if self.processor_4b:
                inputs = self.processor_4b(text=WOUND_DESCRIPTION_PROMPT, images=image, return_tensors="pt")
            elif self.tokenizer_4b:
                # Fallback if only tokenizer is provided (unlikely for VLM but kept for compatibility)
                 raise ValueError("Processor is required for VLM inference")
            else:
                raise ValueError("No processor or tokenizer provided for 4B model")

            # Move to device
            device = self.model_4b.device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                generate_ids = self.model_4b.generate(
                    **inputs, 
                    max_new_tokens=512,
                    do_sample=False  # Deterministic for analysis
                )
            
            # Decode
            # Skip the prompt in the output if included
            generated_text = self.processor_4b.batch_decode(generate_ids, skip_special_tokens=True)[0]
            
            # Attempt to clean up if the model echoes the prompt (depends on model behavior)
            # Simple heuristic: look for the first '{'
            result = self.parse_json_response(generated_text)
            return result

        except Exception as e:
            print(f"Error in analyze_wound_image: {e}")
            # Fallback to empty structure or re-raise
            raise e
        
    def classify_wound_status(
        self, 
        analysis_t0: Dict, 
        analysis_t1: Dict, 
        nurse_notes: str = "",
        use_mock: bool = True
    ) -> Dict:
        """
        Classify wound healing status using MedGemma 27B
        
        Args:
            analysis_t0: Analysis for timepoint 0
            analysis_t1: Analysis for timepoint 1
            nurse_notes: Optional clinical notes
            use_mock: Use mock classification
            
        Returns:
            dict: Classification result with confidence
        """
        if use_mock or self.model_27b is None:
            # Mock classification based on area change
            from src.longitudinal_analysis import calculate_area_change
            
            area_change = calculate_area_change(analysis_t0, analysis_t1)
            
            if area_change < -10:
                classification = "Improving"
                confidence = 85
                rationale = f"Wound area decreased by {abs(area_change):.1f}%, showing positive healing"
            elif area_change > 10:
                classification = "Worsening"
                confidence = 80
                rationale = f"Wound area increased by {area_change:.1f}%, indicating deterioration"
            else:
                classification = "Stable"
                confidence = 75
                rationale = f"Minimal area change ({area_change:.1f}%), wound status stable"
            
            return {
                "classification": classification,
                "confidence": confidence,
                "rationale": rationale
            }
        
        try:
            # Construct prompt
            prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
                day0="0", day1="7", # Simplified
                desc0=json.dumps(analysis_t0),
                desc1=json.dumps(analysis_t1),
                notes=nurse_notes
            )
            
            # Prepare inputs
            inputs = self.tokenizer_27b(prompt, return_tensors="pt").to(self.model_27b.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model_27b.generate(**inputs, max_new_tokens=256, temperature=0.1)
                
            generated_text = self.tokenizer_27b.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON part (often after the prompt)
            # Depending on model, we might need to split by prompt end
            # For now, just try to parse the whole thing or find JSON
            result = self.parse_json_response(generated_text)
            return result
            
        except Exception as e:
            print(f"Error in classify_wound_status: {e}")
            raise e
    
    @staticmethod
    def parse_json_response(text: str) -> Dict:
        """Parse JSON from model output"""
        try:
            # First try: precise JSON extraction
            # Find the first '{' and the last '}'
            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
            
            # If strictly valid JSON not found, try to clean markdown code blocks
            code_block_pattern = r"```json\s*(.*?)\s*```"
            match = re.search(code_block_pattern, text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
            # Fallback: Is the whole text JSON?
            return json.loads(text)
            
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from: {text[:100]}...")
            # Return a valid empty structure to prevent crashes
            return {}


def should_escalate(classification_result: Dict, area_change: float) -> bool:
    """
    Determine if wound requires clinical escalation
    
    Args:
        classification_result: Result from classify_wound_status
        area_change: Percentage area change
        
    Returns:
        bool: True if escalation needed
    """
    if classification_result['classification'] == "Worsening" and classification_result['confidence'] > 70:
        return True
    
    if area_change > 15:  # >15% increase
        return True
    
    return False
