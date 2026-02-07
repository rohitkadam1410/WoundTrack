"""
Tests for dataset generation functionality
"""
import pytest
import json
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dataset_schemas import (
    VLMTrainingSample, LLMTrainingSample,
    WoundAnnotation, WoundDimensions, TissueComposition, Exudate,
    DatasetMetadata
)
from generate_finetuning_dataset import (
    analyze_wound_image_for_ground_truth,
    generate_vlm_training_sample,
    generate_llm_training_sample,
    export_to_jsonl
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_wound_image(temp_dir):
    """Create a mock wound image for testing"""
    # Create a simple test image (pink/red wound with some yellow)
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    
    # Pink wound bed (granulation)
    img[50:150, 50:150] = [200, 100, 120]  # Pink-red
    
    # Yellow slough area
    img[80:120, 80:120] = [200, 200, 100]  # Yellow
    
    # Save image
    img_path = temp_dir / "test_wound.png"
    Image.fromarray(img).save(img_path)
    
    return img_path


# ============================================================================
# Schema Validation Tests
# ============================================================================

def test_wound_dimensions_validation():
    """Test WoundDimensions schema validation"""
    # Valid dimensions
    dims = WoundDimensions(length_cm=5.0, width_cm=3.0)
    assert dims.length_cm == 5.0
    assert dims.width_cm == 3.0
    
    # Invalid: negative dimensions
    with pytest.raises(ValueError):
        WoundDimensions(length_cm=-1.0, width_cm=3.0)
    
    # Invalid: too large
    with pytest.raises(ValueError):
        WoundDimensions(length_cm=100.0, width_cm=3.0)


def test_tissue_composition_validation():
    """Test TissueComposition schema validation"""
    # Valid composition
    tissue = TissueComposition(granulation=70, slough=25, eschar=5)
    assert tissue.granulation == 70
    
    # Invalid: over 100%
    with pytest.raises(ValueError):
        TissueComposition(granulation=120, slough=25, eschar=5)
    
    # Invalid: negative
    with pytest.raises(ValueError):
        TissueComposition(granulation=-10, slough=25, eschar=5)


def test_vlm_sample_validation():
    """Test VLM sample schema validation"""
    from dataset_schemas import VLMMessage, VLMMessageContent
    
    # Valid sample
    sample = VLMTrainingSample(
        messages=[
            VLMMessage(
                role="user",
                content=[
                    VLMMessageContent(type="text", text="Analyze this wound"),
                    VLMMessageContent(type="image_url", image_url={"url": "file:///test.png"})
                ]
            ),
            VLMMessage(
                role="assistant",
                content='{"dimensions": {"length_cm": 5.0, "width_cm": 3.0}}'
            )
        ]
    )
    assert len(sample.messages) == 2
    
    # Invalid: missing assistant message
    with pytest.raises(ValueError):
        VLMTrainingSample(
            messages=[
                VLMMessage(role="user", content="test")
            ]
        )


def test_llm_sample_validation():
    """Test LLM sample schema validation"""
    from dataset_schemas import LLMMessage
    
    # Valid sample
    sample = LLMTrainingSample(
        messages=[
            LLMMessage(role="user", content="Classify this wound progression"),
            LLMMessage(role="assistant", content='{"classification": "Improving", "confidence": 85, "rationale": "Wound is healing well"}')
        ]
    )
    assert len(sample.messages) == 2
    
    # Invalid: too few messages
    with pytest.raises(ValueError):
        LLMTrainingSample(messages=[LLMMessage(role="user", content="test")])


# ============================================================================
# Ground Truth Generation Tests
# ============================================================================

def test_analyze_wound_image_for_ground_truth(mock_wound_image):
    """Test image analysis for ground truth generation"""
    annotation = analyze_wound_image_for_ground_truth(mock_wound_image)
    
    # Check that annotation is valid
    assert isinstance(annotation, WoundAnnotation)
    assert annotation.dimensions.length_cm > 0
    assert annotation.dimensions.width_cm > 0
    
    # Check tissue composition sums to reasonable value
    total = (annotation.tissue_composition.granulation + 
            annotation.tissue_composition.slough + 
            annotation.tissue_composition.eschar)
    assert 95 <= total <= 105  # Allow small rounding errors
    
    # Check exudate is valid
    assert annotation.exudate.amount in ["none", "minimal", "moderate", "heavy"]
    assert annotation.exudate.type in ["serous", "sanguineous", "purulent", "serosanguineous"]


# ============================================================================
# Sample Generation Tests
# ============================================================================

def test_generate_vlm_training_sample(mock_wound_image):
    """Test VLM training sample generation"""
    sample = generate_vlm_training_sample(mock_wound_image, "wound_001")
    
    # Validate structure
    assert isinstance(sample, VLMTrainingSample)
    assert len(sample.messages) == 2
    assert sample.messages[0].role == "user"
    assert sample.messages[-1].role == "assistant"
    
    # Validate metadata
    assert sample.metadata["wound_id"] == "wound_001"
    
    # Validate assistant response is valid JSON
    assistant_content = sample.messages[-1].content
    data = json.loads(assistant_content)
    assert "dimensions" in data
    assert "tissue_composition" in data


def test_generate_llm_training_sample():
    """Test LLM training sample generation"""
    # Mock analyses
    analysis_t0 = {
        "dimensions": {"length_cm": 5.0, "width_cm": 3.0},
        "tissue_composition": {"granulation": 60, "slough": 35, "eschar": 5}
    }
    analysis_t1 = {
        "dimensions": {"length_cm": 4.0, "width_cm": 2.5},
        "tissue_composition": {"granulation": 75, "slough": 20, "eschar": 5}
    }
    
    sample = generate_llm_training_sample(
        analysis_t0, analysis_t1, "wound_002", "healing"
    )
    
    # Validate structure
    assert isinstance(sample, LLMTrainingSample)
    assert len(sample.messages) == 2
    assert sample.messages[0].role == "user"
    assert sample.messages[-1].role == "assistant"
    
    # Validate classification
    assistant_content = sample.messages[-1].content
    data = json.loads(assistant_content)
    assert data["classification"] in ["Improving", "Stable", "Worsening"]
    assert 0 <= data["confidence"] <= 100
    assert len(data["rationale"]) > 10


# ============================================================================
# Export Tests
# ============================================================================

def test_export_to_jsonl(temp_dir, mock_wound_image):
    """Test JSONL export functionality"""
    # Generate a sample
    sample = generate_vlm_training_sample(mock_wound_image, "wound_test")
    
    # Export
    output_file = temp_dir / "test_export.jsonl"
    export_to_jsonl([sample], output_file)
    
    # Verify file exists
    assert output_file.exists()
    
    # Load and verify content
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    assert len(lines) == 1
    
    # Verify JSON is valid
    data = json.loads(lines[0])
    assert "messages" in data
    assert len(data["messages"]) == 2


def test_dataset_completeness(temp_dir, mock_wound_image):
    """Test that generated datasets are complete"""
    # Generate sample
    sample = generate_vlm_training_sample(mock_wound_image, "wound_complete")
    
    # Export
    output_file = temp_dir / "complete_test.jsonl"
    export_to_jsonl([sample], output_file)
    
    # Load and validate
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.loads(f.readline())
    
    # Check all required fields are present
    assert "messages" in data
    assert "metadata" in data
    assert data["metadata"]["wound_id"] == "wound_complete"
    
    # Check messages structure
    user_msg = data["messages"][0]
    assert user_msg["role"] == "user"
    assert isinstance(user_msg["content"], list)
    
    assistant_msg = data["messages"][1]
    assert assistant_msg["role"] == "assistant"
    
    # Validate assistant response
    annotation = json.loads(assistant_msg["content"])
    assert all(key in annotation for key in [
        "dimensions", "tissue_composition", "exudate", 
        "surrounding_skin", "wound_bed_color"
    ])


def test_no_duplicate_samples(temp_dir, mock_wound_image):
    """Test that generated samples have unique IDs"""
    samples = []
    for i in range(10):
        sample = generate_vlm_training_sample(mock_wound_image, f"wound_{i:03d}")
        samples.append(sample)
    
    # Export
    output_file = temp_dir / "duplicate_test.jsonl"
    export_to_jsonl(samples, output_file)
    
    # Load and check IDs
    wound_ids = set()
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            wound_id = data["metadata"]["wound_id"]
            assert wound_id not in wound_ids, f"Duplicate ID found: {wound_id}"
            wound_ids.add(wound_id)
    
    assert len(wound_ids) == 10


# ============================================================================
# Dataset Metadata Tests
# ============================================================================

def test_dataset_metadata_creation():
    """Test dataset metadata creation"""
    metadata = DatasetMetadata(
        dataset_type="vlm",
        num_samples=100,
        generation_date="2026-02-07T23:00:00",
        split="train",
        source_images_dir="data/test",
        class_distribution=None
    )
    
    assert metadata.dataset_type == "vlm"
    assert metadata.num_samples == 100
    assert metadata.schema_version == "1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
