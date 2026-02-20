"""
Quick script to select diverse baseline wound images from Kaggle datasets
Run this locally to prepare images for Colab upload
"""
import random
from pathlib import Path
import shutil


def select_diverse_baselines(dataset_path, output_dir, num_samples=50, seed=42):
    """
    Select diverse wound images from a dataset
    
    Args:
        dataset_path: Path to extracted Kaggle dataset
        output_dir: Where to save selected images
        num_samples: Number of images to select
        seed: Random seed for reproducibility
    """
    dataset_path = Path(dataset_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    all_images = []
    
    for ext in image_extensions:
        all_images.extend(dataset_path.rglob(f'*{ext}'))
        all_images.extend(dataset_path.rglob(f'*{ext.upper()}'))
    
    print(f"Found {len(all_images)} total images in {dataset_path}")
    
    if len(all_images) == 0:
        print("❌ No images found! Check the dataset path.")
        return
    
    # Randomly select diverse samples
    random.seed(seed)
    selected = random.sample(all_images, min(num_samples, len(all_images)))
    
    # Copy to output directory
    for idx, img_path in enumerate(selected):
        new_name = f"baseline_{idx:03d}{img_path.suffix}"
        shutil.copy2(img_path, output_dir / new_name)
        print(f"✓ Copied: {img_path.name} → {new_name}")
    
    print(f"\n✅ Selected {len(selected)} baseline images")
    print(f"📁 Saved to: {output_dir.absolute()}")
    print(f"\n🚀 Ready to upload to Colab!")


if __name__ == "__main__":
    # Example usage - update these paths
    
    # Path to your extracted Kaggle dataset
    DATASET_PATH = "path/to/wound-segmentation-images"  # UPDATE THIS
    
    # Where to save selected baselines
    OUTPUT_DIR = "d:/projects/WoundTrack/data/baseline_wounds"
    
    # Number of images to select
    NUM_SAMPLES = 50
    
    print("=" * 60)
    print("WoundTrack: Baseline Image Selector")
    print("=" * 60)
    print()
    
    select_diverse_baselines(DATASET_PATH, OUTPUT_DIR, NUM_SAMPLES)
    
    print()
    print("=" * 60)
    print("Next steps:")
    print("1. Review selected images in:", OUTPUT_DIR)
    print("2. Remove any poor quality images")
    print("3. Upload folder to Google Colab")
    print("=" * 60)
