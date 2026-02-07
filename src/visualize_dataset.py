"""
Visualize and analyze generated fine-tuning datasets
Provides tools to inspect dataset quality and distribution
"""
import json
import argparse
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image
import numpy as np


def load_jsonl_dataset(file_path: Path) -> List[Dict]:
    """Load JSONL dataset"""
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            samples.append(json.loads(line))
    return samples


def analyze_dataset_statistics(samples: List[Dict], dataset_type: str):
    """Print dataset statistics"""
    print(f"\n{'='*60}")
    print(f"{dataset_type.upper()} Dataset Statistics")
    print(f"{'='*60}")
    print(f"Total samples: {len(samples)}")
    
    if dataset_type == "llm":
        # Analyze classification distribution
        class_counts = {"Improving": 0, "Stable": 0, "Worsening": 0}
        confidences = []
        
        for sample in samples:
            try:
                assistant_msg = sample['messages'][-1]['content']
                data = json.loads(assistant_msg)
                label = data.get('classification', 'Unknown')
                if label in class_counts:
                    class_counts[label] += 1
                conf = data.get('confidence', 0)
                confidences.append(conf)
            except:
                pass
        
        print(f"\nClass Distribution:")
        for label, count in class_counts.items():
            pct = (count / len(samples)) * 100 if samples else 0
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        if confidences:
            print(f"\nConfidence Scores:")
            print(f"  Mean: {np.mean(confidences):.1f}")
            print(f"  Median: {np.median(confidences):.1f}")
            print(f"  Range: [{min(confidences)}, {max(confidences)}]")
    
    elif dataset_type == "vlm":
        # Analyze wound characteristics
        dimensions = []
        granulation_pcts = []
        
        for sample in samples:
            try:
                assistant_msg = sample['messages'][-1]['content']
                data = json.loads(assistant_msg)
                dims = data.get('dimensions', {})
                area = dims.get('length_cm', 0) * dims.get('width_cm', 0)
                dimensions.append(area)
                
                tissue = data.get('tissue_composition', {})
                gran = tissue.get('granulation', 0)
                granulation_pcts.append(gran)
            except:
                pass
        
        if dimensions:
            print(f"\nWound Dimensions (area in cm²):")
            print(f"  Mean: {np.mean(dimensions):.2f} cm²")
            print(f"  Median: {np.median(dimensions):.2f} cm²")
            print(f"  Range: [{min(dimensions):.2f}, {max(dimensions):.2f}]")
        
        if granulation_pcts:
            print(f"\nGranulation Tissue %:")
            print(f"  Mean: {np.mean(granulation_pcts):.1f}%")
            print(f"  Range: [{min(granulation_pcts)}, {max(granulation_pcts)}]")
    
    print(f"{'='*60}\n")


def visualize_vlm_samples(samples: List[Dict], num_samples: int = 5, output_dir: Path = None):
    """Visualize VLM training samples"""
    print(f"\nVisualizing {num_samples} VLM samples...")
    
    # Select random samples
    selected = np.random.choice(len(samples), min(num_samples, len(samples)), replace=False)
    
    fig, axes = plt.subplots(num_samples, 2, figsize=(14, 4 * num_samples))
    if num_samples == 1:
        axes = axes.reshape(1, -1)
    
    for idx, sample_idx in enumerate(selected):
        sample = samples[sample_idx]
        
        # Extract image path and annotation
        try:
            # Find image URL in user message
            user_content = sample['messages'][0]['content']
            image_url = None
            for item in user_content:
                if item.get('type') == 'image_url':
                    image_url = item['image_url']['url']
                    break
            
            # Load image
            if image_url:
                # Remove file:/// prefix
                image_path = image_url.replace('file:///', '')
                img = Image.open(image_path)
                
                # Display image
                axes[idx, 0].imshow(img)
                axes[idx, 0].axis('off')
                axes[idx, 0].set_title(f"Sample {sample_idx}: Wound Image", fontsize=10)
            
            # Parse annotation
            assistant_msg = sample['messages'][-1]['content']
            annotation = json.loads(assistant_msg)
            
            # Create annotation text
            dims = annotation.get('dimensions', {})
            tissue = annotation.get('tissue_composition', {})
            exudate = annotation.get('exudate', {})
            
            annotation_text = f"""
Dimensions:
  Length: {dims.get('length_cm', 0):.1f} cm
  Width: {dims.get('width_cm', 0):.1f} cm
  Area: {dims.get('length_cm', 0) * dims.get('width_cm', 0):.2f} cm²

Tissue Composition:
  Granulation: {tissue.get('granulation', 0)}%
  Slough: {tissue.get('slough', 0)}%
  Eschar: {tissue.get('eschar', 0)}%

Exudate:
  Amount: {exudate.get('amount', 'N/A')}
  Type: {exudate.get('type', 'N/A')}

Surrounding Skin:
  {annotation.get('surrounding_skin', 'N/A')}

Wound Bed Color:
  {annotation.get('wound_bed_color', 'N/A')}
            """.strip()
            
            axes[idx, 1].text(0.05, 0.95, annotation_text, 
                            transform=axes[idx, 1].transAxes,
                            fontsize=9, verticalalignment='top',
                            fontfamily='monospace',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            axes[idx, 1].axis('off')
            axes[idx, 1].set_title(f"Ground Truth Annotation", fontsize=10)
            
        except Exception as e:
            print(f"Error visualizing sample {sample_idx}: {e}")
            axes[idx, 0].text(0.5, 0.5, f"Error loading sample", 
                            ha='center', va='center')
            axes[idx, 0].axis('off')
            axes[idx, 1].axis('off')
    
    plt.tight_layout()
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "vlm_samples_visualization.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved visualization to {output_path}")
    else:
        plt.show()


def visualize_llm_distribution(samples: List[Dict], output_dir: Path = None):
    """Visualize LLM dataset class distribution"""
    print("\nVisualizing LLM class distribution...")
    
    # Extract classifications
    class_counts = {"Improving": 0, "Stable": 0, "Worsening": 0}
    area_changes_by_class = {"Improving": [], "Stable": [], "Worsening": []}
    
    for sample in samples:
        try:
            assistant_msg = sample['messages'][-1]['content']
            data = json.loads(assistant_msg)
            label = data.get('classification', 'Unknown')
            
            if label in class_counts:
                class_counts[label] += 1
            
            # Extract area change from metadata
            metadata = sample.get('metadata', {})
            area_change = metadata.get('area_change_percent', 0)
            if label in area_changes_by_class:
                area_changes_by_class[label].append(area_change)
        except:
            pass
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart of class distribution
    labels = list(class_counts.keys())
    counts = list(class_counts.values())
    colors = ['green', 'orange', 'red']
    
    axes[0].bar(labels, counts, color=colors, alpha=0.7)
    axes[0].set_ylabel('Number of Samples', fontsize=12)
    axes[0].set_title('Classification Distribution', fontsize=14, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    # Add counts on bars
    for i, count in enumerate(counts):
        axes[0].text(i, count + 5, str(count), ha='center', fontsize=10, fontweight='bold')
    
    # Box plot of area changes by class
    data_to_plot = [area_changes_by_class[label] for label in labels if area_changes_by_class[label]]
    
    bp = axes[1].boxplot(data_to_plot, labels=labels, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    axes[1].axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    axes[1].set_ylabel('Area Change (%)', fontsize=12)
    axes[1].set_title('Area Change by Classification', fontsize=14, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "llm_distribution_visualization.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Saved visualization to {output_path}")
    else:
        plt.show()


def display_sample_examples(samples: List[Dict], dataset_type: str, num_examples: int = 3):
    """Print text examples of samples"""
    print(f"\n{'='*60}")
    print(f"Sample {dataset_type.upper()} Examples")
    print(f"{'='*60}\n")
    
    selected = np.random.choice(len(samples), min(num_examples, len(samples)), replace=False)
    
    for idx, sample_idx in enumerate(selected):
        sample = samples[sample_idx]
        
        print(f"--- Example {idx + 1} (Sample #{sample_idx}) ---")
        
        # Display messages
        for msg in sample['messages']:
            role = msg['role'].upper()
            content = msg['content']
            
            if isinstance(content, list):
                # VLM format with image
                print(f"\n[{role}]:")
                for item in content:
                    if item['type'] == 'text':
                        print(item['text'][:200] + "..." if len(item['text']) > 200 else item['text'])
                    elif item['type'] == 'image_url':
                        print(f"<IMAGE: {item['image_url']['url']}>")
            else:
                # LLM format (text only)
                print(f"\n[{role}]:")
                if len(content) > 500:
                    print(content[:500] + "...")
                else:
                    print(content)
        
        print("\n" + "-"*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Visualize fine-tuning datasets")
    parser.add_argument(
        "--dataset_path",
        type=str,
        required=True,
        help="Path to JSONL dataset file"
    )
    parser.add_argument(
        "--dataset_type",
        type=str,
        choices=["vlm", "llm"],
        required=True,
        help="Type of dataset (vlm or llm)"
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=5,
        help="Number of samples to visualize"
    )
    parser.add_argument(
        "--num_examples",
        type=int,
        default=3,
        help="Number of text examples to display"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Directory to save visualizations (if not specified, will display)"
    )
    parser.add_argument(
        "--stats_only",
        action="store_true",
        help="Only show statistics, skip visualizations"
    )
    
    args = parser.parse_args()
    
    dataset_path = Path(args.dataset_path)
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    print(f"\nLoading dataset from {dataset_path}...")
    samples = load_jsonl_dataset(dataset_path)
    
    # Show statistics
    analyze_dataset_statistics(samples, args.dataset_type)
    
    if not args.stats_only:
        # Show text examples
        display_sample_examples(samples, args.dataset_type, args.num_examples)
        
        # Create visualizations
        if args.dataset_type == "vlm":
            visualize_vlm_samples(samples, args.num_samples, output_dir)
        elif args.dataset_type == "llm":
            visualize_llm_distribution(samples, output_dir)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
