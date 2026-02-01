"""
Azure ML Pipeline: Synthetic Wound Image Generator
Generates temporal wound progression sequences using Stable Diffusion
"""
import os
import argparse
import json
from pathlib import Path
from typing import List, Tuple

import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import numpy as np


# Medical-specific prompts for wound progression
HEALING_PROMPTS = {
    "day_7": "medical wound photo, 15% smaller wound, increased pink granulation tissue, reduced exudate, healthier wound bed, clinical photography",
    "day_14": "medical wound photo, 35% smaller wound, epithelial tissue forming at edges, pink healthy granulation, reduced inflammation, clinical photography",
    "day_21": "medical wound photo, 60% smaller wound, re-epithelialization progressing, healthy pink tissue, minimal exudate, healing margins, clinical photography"
}

WORSENING_PROMPTS = {
    "day_7": "medical wound photo, 10% larger wound, increased slough tissue, yellow exudate, inflamed surrounding skin, clinical photography",
    "day_14": "medical wound photo, 25% larger wound, necrotic tissue present, purulent exudate, macerated edges, clinical photography",
    "day_21": "medical wound photo, 40% larger wound, significant necrosis, heavy purulent drainage, erythematous surrounding tissue, clinical photography"
}

NEGATIVE_PROMPT = "cartoon, drawing, illustration, text, watermark, low quality, blurry, distorted, unrealistic"


def setup_pipeline(model_id: str = "stabilityai/stable-diffusion-2-1") -> StableDiffusionImg2ImgPipeline:
    """
    Initialize Stable Diffusion pipeline
    
    Args:
        model_id: Hugging Face model identifier
        
    Returns:
        Configured pipeline
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if device == "cpu":
        print("WARNING: Running on CPU will be very slow!")
    
    print(f"Loading model: {model_id}")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        safety_checker=None
    )
    pipe = pipe.to(device)
    
    # Enable memory optimizations
    if device == "cuda":
        pipe.enable_attention_slicing()
    
    print("✓ Pipeline loaded successfully")
    return pipe


def generate_progression_sequence(
    pipe: StableDiffusionImg2ImgPipeline,
    baseline_image_path: str,
    wound_id: str,
    progression_type: str = "healing",
    output_dir: str = "synthetic_wounds"
) -> dict:
    """
    Generate temporal sequence for a wound
    
    Args:
        pipe: Stable Diffusion pipeline
        baseline_image_path: Path to Day 0 image
        wound_id: Unique identifier
        progression_type: 'healing' or 'worsening'
        output_dir: Output directory
        
    Returns:
        dict: Metadata for generated sequence
    """
    # Load baseline
    baseline_img = Image.open(baseline_image_path).convert('RGB')
    baseline_img = baseline_img.resize((512, 512))
    
    # Select prompts
    prompts = HEALING_PROMPTS if progression_type == "healing" else WORSENING_PROMPTS
    
    # Create output directory
    sequence_dir = Path(output_dir) / wound_id
    sequence_dir.mkdir(parents=True, exist_ok=True)
    
    # Save baseline (Day 0)
    baseline_img.save(sequence_dir / "day_0.png")
    
    metadata = {
        "wound_id": wound_id,
        "progression_type": progression_type,
        "baseline_path": baseline_image_path,
        "timepoints": ["day_0"]
    }
    
    # Generate progression
    for timepoint, prompt in prompts.items():
        print(f"  Generating {timepoint}...")
        
        generated = pipe(
            prompt=prompt,
            image=baseline_img,
            strength=0.3,  # Keep 70% of original structure
            guidance_scale=7.5,
            negative_prompt=NEGATIVE_PROMPT,
            num_inference_steps=30
        ).images[0]
        
        # Save image
        output_path = sequence_dir / f"{timepoint}.png"
        generated.save(output_path)
        metadata["timepoints"].append(timepoint)
    
    # Save metadata
    with open(sequence_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Saved sequence to {sequence_dir}")
    return metadata


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(description="Generate synthetic wound progressions")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory with baseline images")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    parser.add_argument("--model_id", type=str, default="stabilityai/stable-diffusion-2-1", help="Model ID")
    parser.add_argument("--healing_ratio", type=float, default=0.8, help="Ratio of healing sequences")
    parser.add_argument("--num_sequences", type=int, default=50, help="Number of sequences to generate")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Azure ML: Synthetic Wound Progression Generator")
    print("=" * 80)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Target sequences: {args.num_sequences}")
    print()
    
    # Setup pipeline
    pipe = setup_pipeline(args.model_id)
    
    # Find baseline images
    input_path = Path(args.input_dir)
    image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
    
    if len(image_files) == 0:
        raise ValueError(f"No images found in {args.input_dir}")
    
    print(f"Found {len(image_files)} baseline images")
    
    # Select subset if needed
    if len(image_files) > args.num_sequences:
        np.random.seed(42)
        image_files = np.random.choice(image_files, args.num_sequences, replace=False)
    
    # Calculate split
    num_healing = int(len(image_files) * args.healing_ratio)
    num_worsening = len(image_files) - num_healing
    
    print(f"Generating {num_healing} healing and {num_worsening} worsening sequences")
    print()
    
    # Generate sequences
    all_metadata = []
    
    for idx, img_path in enumerate(image_files):
        wound_id = f"wound_{idx:03d}"
        progression_type = "healing" if idx < num_healing else "worsening"
        
        print(f"[{idx+1}/{len(image_files)}] {wound_id} ({progression_type})")
        
        try:
            metadata = generate_progression_sequence(
                pipe, 
                str(img_path), 
                wound_id, 
                progression_type,
                args.output_dir
            )
            all_metadata.append(metadata)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    # Save summary
    summary = {
        "total_sequences": len(all_metadata),
        "healing_sequences": num_healing,
        "worsening_sequences": num_worsening,
        "model_id": args.model_id,
        "sequences": all_metadata
    }
    
    summary_path = Path(args.output_dir) / "generation_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()
    print("=" * 80)
    print(f"✅ Generation complete!")
    print(f"Generated {len(all_metadata)} sequences")
    print(f"Output: {args.output_dir}")
    print(f"Summary: {summary_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
