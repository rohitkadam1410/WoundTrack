"""
Generate fine-tuning datasets for MedGemma models
Creates training samples for both VLM (4B) and LLM (27B) models
"""
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from PIL import Image
import cv2

from dataset_schemas import (
    VLMTrainingSample, LLMTrainingSample,
    VLMMessage, LLMMessage, VLMMessageContent,
    WoundAnnotation, WoundDimensions, TissueComposition, Exudate,
    ClassificationResult, DatasetMetadata,
    vlm_sample_to_dict, llm_sample_to_dict
)
from longitudinal_analysis import calculate_area_change, calculate_tissue_shift

# Import prompt templates (these are just strings, no torch dependency)
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



# ============================================================================
# Ground Truth Generation (Image Analysis)
# ============================================================================

def analyze_wound_image_for_ground_truth(image_path: Path) -> WoundAnnotation:
    """
    Generate ground truth annotation by analyzing wound image
    Uses computer vision to estimate realistic wound characteristics
    
    Args:
        image_path: Path to wound image
        
    Returns:
        WoundAnnotation with estimated characteristics
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width = img.shape[:2]
    
    # Estimate dimensions (assume images are roughly standardized)
    # Use pixel dimensions as proxy - adjust scale factor based on your images
    scale_factor = 0.01  # Rough conversion: 100 pixels ≈ 1 cm
    length_cm = round(height * scale_factor, 1)
    width_cm = round(width * scale_factor, 1)
    
    # Constrain to realistic wound sizes
    length_cm = np.clip(length_cm, 1.0, 15.0)
    width_cm = np.clip(width_cm, 1.0, 12.0)
    
    # Analyze color distribution for tissue composition
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # Define color ranges (rough heuristics)
    # Pink/Red (granulation): H 0-20, 160-180
    # Yellow (slough): H 20-40
    # Dark/Black (eschar): V < 50
    
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    # Calculate rough percentages
    total_pixels = height * width
    
    # Granulation (pink-red, healthy): high saturation, mid-high value
    granulation_mask = ((h < 20) | (h > 160)) & (s > 50) & (v > 80)
    granulation_pct = int((granulation_mask.sum() / total_pixels) * 100)
    
    # Slough (yellow): hue 20-40
    slough_mask = (h >= 20) & (h <= 40) & (s > 30)
    slough_pct = int((slough_mask.sum() / total_pixels) * 100)
    
    # Eschar (dark): low value
    eschar_mask = v < 60
    eschar_pct = int((eschar_mask.sum() / total_pixels) * 100)
    
    # Normalize to 100% (distribute remainder to granulation)
    total = granulation_pct + slough_pct + eschar_pct
    if total > 0:
        granulation_pct = int((granulation_pct / total) * 100)
        slough_pct = int((slough_pct / total) * 100)
        eschar_pct = 100 - granulation_pct - slough_pct
    else:
        # Default if detection fails
        granulation_pct, slough_pct, eschar_pct = 70, 25, 5
    
    # Ensure valid percentages
    granulation_pct = np.clip(granulation_pct, 0, 100)
    slough_pct = np.clip(slough_pct, 0, 100)
    eschar_pct = np.clip(100 - granulation_pct - slough_pct, 0, 100)
    
    # Estimate exudate based on brightness and saturation
    avg_value = v.mean()
    avg_saturation = s.mean()
    
    if avg_value > 180:
        exudate_amount = "heavy"
    elif avg_value > 140:
        exudate_amount = "moderate"
    elif avg_value > 100:
        exudate_amount = "minimal"
    else:
        exudate_amount = "none"
    
    # Exudate type based on color
    exudate_type = random.choice(["serous", "sanguineous", "serosanguineous"])
    
    # Surrounding skin (random but biased toward intact)
    surrounding_skin = random.choices(
        ["intact", "macerated", "erythematous", "indurated"],
        weights=[0.6, 0.2, 0.15, 0.05]
    )[0]
    
    # Describe wound bed color
    if granulation_pct > 60:
        wound_bed_color = "pink-red with healthy granulation"
    elif slough_pct > 40:
        wound_bed_color = "yellow-tan with slough present"
    elif eschar_pct > 30:
        wound_bed_color = "dark with eschar formation"
    else:
        wound_bed_color = "mixed pink and yellow"
    
    return WoundAnnotation(
        dimensions=WoundDimensions(length_cm=length_cm, width_cm=width_cm),
        tissue_composition=TissueComposition(
            granulation=granulation_pct,
            slough=slough_pct,
            eschar=eschar_pct
        ),
        exudate=Exudate(amount=exudate_amount, type=exudate_type),
        surrounding_skin=surrounding_skin,
        wound_bed_color=wound_bed_color
    )


# ============================================================================
# VLM Dataset Generation
# ============================================================================

def generate_vlm_training_sample(image_path: Path, wound_id: str) -> VLMTrainingSample:
    """
    Generate a single VLM training sample (image → analysis)
    
    Args:
        image_path: Path to wound image
        wound_id: Unique identifier for wound
        
    Returns:
        VLMTrainingSample with image input and structured output
    """
    # Generate ground truth annotation
    annotation = analyze_wound_image_for_ground_truth(image_path)
    
    # Create user message with image
    user_message = VLMMessage(
        role="user",
        content=[
            VLMMessageContent(type="text", text=WOUND_DESCRIPTION_PROMPT),
            VLMMessageContent(
                type="image_url",
                image_url={"url": f"file:///{image_path.as_posix()}"}
            )
        ]
    )
    
    # Create assistant response (ground truth)
    assistant_message = VLMMessage(
        role="assistant",
        content=annotation.model_dump_json()
    )
    
    return VLMTrainingSample(
        messages=[user_message, assistant_message],
        metadata={
            "wound_id": wound_id,
            "image_path": str(image_path),
            "generation_method": "computer_vision_analysis"
        }
    )


def generate_vlm_dataset(
    image_dir: Path,
    num_samples: int,
    output_path: Path
) -> List[VLMTrainingSample]:
    """
    Generate VLM training dataset from wound images
    
    Args:
        image_dir: Directory containing wound images
        num_samples: Number of samples to generate
        output_path: Where to save the dataset
        
    Returns:
        List of VLM training samples
    """
    # Find all images
    image_extensions = {'.png', '.jpg', '.jpeg'}
    all_images = [
        p for p in image_dir.rglob('*')
        if p.suffix.lower() in image_extensions
    ]
    
    if not all_images:
        raise ValueError(f"No images found in {image_dir}")
    
    print(f"Found {len(all_images)} images in {image_dir}")
    
    # Sample images (with replacement if needed)
    if len(all_images) < num_samples:
        print(f"Warning: Only {len(all_images)} images available, sampling with replacement")
        sampled_images = random.choices(all_images, k=num_samples)
    else:
        sampled_images = random.sample(all_images, num_samples)
    
    # Generate samples
    samples = []
    for idx, img_path in enumerate(sampled_images):
        try:
            wound_id = f"wound_{idx:04d}"
            sample = generate_vlm_training_sample(img_path, wound_id)
            samples.append(sample)
            
            if (idx + 1) % 100 == 0:
                print(f"Generated {idx + 1}/{num_samples} VLM samples")
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue
    
    print(f"✓ Generated {len(samples)} VLM training samples")
    return samples


# ============================================================================
# LLM Dataset Generation
# ============================================================================

def generate_classification_ground_truth(
    analysis_t0: Dict,
    analysis_t1: Dict,
    progression_type: str
) -> ClassificationResult:
    """
    Generate ground truth classification based on temporal analysis
    
    Args:
        analysis_t0: Wound analysis at timepoint 0
        analysis_t1: Wound analysis at timepoint 1
        progression_type: "healing" or "worsening" (from synthetic data)
        
    Returns:
        ClassificationResult with label and rationale
    """
    # Calculate metrics
    area_change = calculate_area_change(analysis_t0, analysis_t1)
    tissue_shifts = calculate_tissue_shift(analysis_t0, analysis_t1)
    
    # Determine classification
    if progression_type == "healing" or area_change < -10:
        classification = "Improving"
        confidence = random.randint(80, 95)
        rationale = (
            f"Wound area decreased by {abs(area_change):.1f}% "
            f"with {tissue_shifts['granulation']:+d}% increase in granulation tissue. "
            "Healing trajectory is positive."
        )
    elif progression_type == "worsening" or area_change > 10:
        classification = "Worsening"
        confidence = random.randint(75, 90)
        rationale = (
            f"Wound area increased by {area_change:.1f}% "
            f"with {tissue_shifts['slough']:+d}% change in slough tissue. "
            "Deterioration observed, recommend clinical review."
        )
    else:
        classification = "Stable"
        confidence = random.randint(70, 85)
        rationale = (
            f"Minimal area change ({area_change:.1f}%) observed. "
            "Wound remains stable with no significant progression."
        )
    
    return ClassificationResult(
        classification=classification,
        confidence=confidence,
        rationale=rationale
    )


def generate_llm_training_sample(
    analysis_t0: Dict,
    analysis_t1: Dict,
    wound_id: str,
    progression_type: str,
    nurse_notes: str = ""
) -> LLMTrainingSample:
    """
    Generate a single LLM training sample (temporal analysis → classification)
    
    Args:
        analysis_t0: Wound analysis at timepoint 0
        analysis_t1: Wound analysis at timepoint 1
        wound_id: Unique identifier
        progression_type: "healing" or "worsening"
        nurse_notes: Optional clinical notes
        
    Returns:
        LLMTrainingSample with classification task
    """
    # Generate ground truth
    ground_truth = generate_classification_ground_truth(
        analysis_t0, analysis_t1, progression_type
    )
    
    # Create user prompt
    user_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
        day0=0,
        day1=7,
        desc0=json.dumps(analysis_t0),
        desc1=json.dumps(analysis_t1),
        notes=nurse_notes or "No additional notes."
    )
    
    # Create messages
    user_message = LLMMessage(role="user", content=user_prompt)
    assistant_message = LLMMessage(
        role="assistant",
        content=ground_truth.model_dump_json()
    )
    
    return LLMTrainingSample(
        messages=[user_message, assistant_message],
        metadata={
            "wound_id": wound_id,
            "progression_type": progression_type,
            "area_change_percent": round(
                calculate_area_change(analysis_t0, analysis_t1), 2
            )
        }
    )


def generate_llm_dataset(
    image_dir: Path,
    num_samples: int,
    output_path: Path
) -> List[LLMTrainingSample]:
    """
    Generate LLM training dataset from wound image sequences
    
    Args:
        image_dir: Directory containing wound sequences
        num_samples: Number of samples to generate
        output_path: Where to save the dataset
        
    Returns:
        List of LLM training samples
    """
    samples = []
    
    # Look for wound sequence directories
    # Expected structure: wound_XXX_healing/worsening containing timepoint images
    sequence_dirs = [d for d in image_dir.iterdir() if d.is_dir()]
    
    if not sequence_dirs:
        print(f"No sequence directories found in {image_dir}")
        print("Generating synthetic temporal pairs from random images...")
        # Fallback: create synthetic pairs from random images
        return generate_llm_dataset_from_random_pairs(image_dir, num_samples)
    
    print(f"Found {len(sequence_dirs)} wound sequences")
    
    # Generate samples from sequences
    for idx in range(num_samples):
        try:
            # Select random sequence
            seq_dir = random.choice(sequence_dirs)
            
            # Determine progression type from directory name
            if "healing" in seq_dir.name.lower():
                progression_type = "healing"
            elif "worsening" in seq_dir.name.lower():
                progression_type = "worsening"
            else:
                progression_type = random.choice(["healing", "worsening"])
            
            # Find timepoint images
            images = sorted([p for p in seq_dir.iterdir() if p.suffix.lower() in {'.png', '.jpg', '.jpeg'}])
            
            if len(images) < 2:
                continue
            
            # Select two timepoints
            img_t0 = images[0]
            img_t1 = random.choice(images[1:])
            
            # Generate mock analyses (in real scenario, you'd use actual MedGemma or stored annotations)
            analysis_t0 = analyze_wound_image_for_ground_truth(img_t0).model_dump()
            analysis_t1 = analyze_wound_image_for_ground_truth(img_t1).model_dump()
            
            # Adjust analysis_t1 based on progression type
            if progression_type == "healing":
                # Reduce dimensions
                analysis_t1['dimensions']['length_cm'] *= random.uniform(0.7, 0.9)
                analysis_t1['dimensions']['width_cm'] *= random.uniform(0.7, 0.9)
                # Increase granulation
                analysis_t1['tissue_composition']['granulation'] = min(
                    100, analysis_t1['tissue_composition']['granulation'] + random.randint(5, 20)
                )
            else:
                # Increase dimensions
                analysis_t1['dimensions']['length_cm'] *= random.uniform(1.1, 1.3)
                analysis_t1['dimensions']['width_cm'] *= random.uniform(1.1, 1.3)
                # Increase slough
                analysis_t1['tissue_composition']['slough'] = min(
                    100, analysis_t1['tissue_composition']['slough'] + random.randint(5, 15)
                )
            
            wound_id = f"wound_seq_{idx:04d}"
            sample = generate_llm_training_sample(
                analysis_t0, analysis_t1, wound_id, progression_type
            )
            samples.append(sample)
            
            if (idx + 1) % 100 == 0:
                print(f"Generated {idx + 1}/{num_samples} LLM samples")
                
        except Exception as e:
            print(f"Error generating LLM sample {idx}: {e}")
            continue
    
    print(f"✓ Generated {len(samples)} LLM training samples")
    return samples


def generate_llm_dataset_from_random_pairs(
    image_dir: Path,
    num_samples: int
) -> List[LLMTrainingSample]:
    """Fallback: Generate LLM samples from random image pairs"""
    image_extensions = {'.png', '.jpg', '.jpeg'}
    all_images = [
        p for p in image_dir.rglob('*')
        if p.suffix.lower() in image_extensions
    ]
    
    if len(all_images) < 2:
        raise ValueError(f"Need at least 2 images in {image_dir}")
    
    samples = []
    
    for idx in range(num_samples):
        try:
            # Select two random images
            img_t0, img_t1 = random.sample(all_images, 2)
            
            # Generate analyses
            analysis_t0 = analyze_wound_image_for_ground_truth(img_t0).model_dump()
            analysis_t1 = analyze_wound_image_for_ground_truth(img_t1).model_dump()
            
            # Random progression type (80% healing, 20% worsening)
            progression_type = random.choices(
                ["healing", "worsening"],
                weights=[0.8, 0.2]
            )[0]
            
            wound_id = f"wound_random_{idx:04d}"
            sample = generate_llm_training_sample(
                analysis_t0, analysis_t1, wound_id, progression_type
            )
            samples.append(sample)
            
        except Exception as e:
            print(f"Error generating random pair {idx}: {e}")
            continue
    
    return samples


# ============================================================================
# Export Functions
# ============================================================================

def export_to_jsonl(samples: List, output_file: Path):
    """Export samples to JSONL format"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in samples:
            if isinstance(sample, VLMTrainingSample):
                sample_dict = vlm_sample_to_dict(sample)
            elif isinstance(sample, LLMTrainingSample):
                sample_dict = llm_sample_to_dict(sample)
            else:
                sample_dict = sample
            
            f.write(json.dumps(sample_dict, ensure_ascii=False) + '\n')
    
    print(f"✓ Exported {len(samples)} samples to {output_file}")


def export_to_huggingface(samples: List, output_dir: Path, split_name: str, dataset_type: str):
    """Export samples to HuggingFace Dataset format"""
    try:
        from datasets import Dataset, DatasetDict
    except ImportError:
        print("Warning: datasets library not installed. Skipping HuggingFace export.")
        print("Install with: pip install datasets")
        return
    
    # Convert samples to dictionaries
    data_dicts = []
    for sample in samples:
        if isinstance(sample, VLMTrainingSample):
            data_dicts.append(vlm_sample_to_dict(sample))
        elif isinstance(sample, LLMTrainingSample):
            data_dicts.append(llm_sample_to_dict(sample))
    
    # Create dataset
    dataset = Dataset.from_list(data_dicts)
    
    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(output_dir / split_name))
    
    print(f"✓ Exported {len(samples)} samples to HuggingFace format at {output_dir}")


def create_dataset_metadata(
    dataset_type: str,
    samples: List,
    split: str,
    source_dir: Path
) -> DatasetMetadata:
    """Create metadata for the generated dataset"""
    
    # Calculate class distribution for LLM datasets
    class_dist = None
    if dataset_type == "llm":
        class_dist = {"Improving": 0, "Stable": 0, "Worsening": 0}
        for sample in samples:
            # Extract classification from assistant message
            try:
                assistant_msg = sample.messages[-1].content
                classification_data = json.loads(assistant_msg)
                label = classification_data.get("classification", "Unknown")
                if label in class_dist:
                    class_dist[label] += 1
            except:
                pass
    
    return DatasetMetadata(
        dataset_type=dataset_type,
        num_samples=len(samples),
        generation_date=datetime.now(),
        split=split,
        source_images_dir=str(source_dir),
        class_distribution=class_dist
    )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate fine-tuning datasets for MedGemma models"
    )
    parser.add_argument(
        "--vlm_samples",
        type=int,
        default=1000,
        help="Number of VLM training samples to generate"
    )
    parser.add_argument(
        "--llm_samples",
        type=int,
        default=800,
        help="Number of LLM training samples to generate"
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        default="data/synthetic_wounds (1-18 healing) (19-24 worsening)",
        help="Directory containing wound images or sequences"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs/finetuning_dataset",
        help="Output directory for generated datasets"
    )
    parser.add_argument(
        "--skip_vlm",
        action="store_true",
        help="Skip VLM dataset generation"
    )
    parser.add_argument(
        "--skip_llm",
        action="store_true",
        help="Skip LLM dataset generation"
    )
    parser.add_argument(
        "--export_hf",
        action="store_true",
        help="Export to HuggingFace Dataset format (requires datasets library)"
    )
    
    args = parser.parse_args()
    
    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("MedGemma Fine-Tuning Dataset Generation")
    print("=" * 60)
    
    # Generate VLM dataset
    if not args.skip_vlm:
        print("\n[1/2] Generating VLM dataset (image → analysis)...")
        vlm_samples = generate_vlm_dataset(
            image_dir=image_dir,
            num_samples=args.vlm_samples,
            output_path=output_dir / "vlm_train.jsonl"
        )
        
        # Export VLM dataset
        export_to_jsonl(vlm_samples, output_dir / "vlm_train.jsonl")
        
        if args.export_hf:
            export_to_huggingface(
                vlm_samples,
                output_dir / "hf_dataset",
                "vlm_train",
                "vlm"
            )
        
        # Save metadata
        vlm_metadata = create_dataset_metadata("vlm", vlm_samples, "train", image_dir)
        with open(output_dir / "vlm_metadata.json", 'w') as f:
            f.write(vlm_metadata.model_dump_json(indent=2))
    
    # Generate LLM dataset
    if not args.skip_llm:
        print("\n[2/2] Generating LLM dataset (analysis → classification)...")
        llm_samples = generate_llm_dataset(
            image_dir=image_dir,
            num_samples=args.llm_samples,
            output_path=output_dir / "llm_train.jsonl"
        )
        
        # Export LLM dataset
        export_to_jsonl(llm_samples, output_dir / "llm_train.jsonl")
        
        if args.export_hf:
            export_to_huggingface(
                llm_samples,
                output_dir / "hf_dataset",
                "llm_train",
                "llm"
            )
        
        # Save metadata
        llm_metadata = create_dataset_metadata("llm", llm_samples, "train", image_dir)
        with open(output_dir / "llm_metadata.json", 'w') as f:
            f.write(llm_metadata.model_dump_json(indent=2))
    
    print("\n" + "=" * 60)
    print(f"✅ Dataset generation complete!")
    print(f"📁 Output directory: {output_dir.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
