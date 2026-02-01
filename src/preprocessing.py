"""
Image preprocessing pipeline for WoundTrack
"""
from PIL import Image
from pathlib import Path
import numpy as np


class WoundImagePreprocessor:
    """Standardize wound images for analysis"""
    
    def __init__(self, target_size=(512, 512)):
        self.target_size = target_size
    
    def preprocess(self, image_path):
        """
        Load and preprocess a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL Image: Preprocessed image
        """
        img = Image.open(image_path).convert('RGB')
        
        # Resize while maintaining aspect ratio
        img.thumbnail(self.target_size, Image.Resampling.LANCZOS)
        
        # Create padded square image
        padded = Image.new('RGB', self.target_size, (0, 0, 0))
        offset = ((self.target_size[0] - img.size[0]) // 2,
                  (self.target_size[1] - img.size[1]) // 2)
        padded.paste(img, offset)
        
        return padded
    
    def batch_preprocess(self, image_paths, output_dir):
        """
        Preprocess multiple images
        
        Args:
            image_paths: List of paths to images
            output_dir: Directory to save processed images
            
        Returns:
            List of output paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        processed = []
        for img_path in image_paths:
            processed_img = self.preprocess(img_path)
            output_path = output_dir / Path(img_path).name
            processed_img.save(output_path)
            processed.append(output_path)
        
        return processed


def normalize_image(image):
    """Normalize image to [0, 1] range"""
    img_array = np.array(image, dtype=np.float32)
    return img_array / 255.0


def denormalize_image(normalized_array):
    """Convert normalized array back to PIL Image"""
    img_array = (normalized_array * 255).astype(np.uint8)
    return Image.fromarray(img_array)
