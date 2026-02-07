"""
Dataset schemas for MedGemma fine-tuning
Defines Pydantic models for data validation and serialization
"""
from typing import List, Dict, Literal, Union, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ============================================================================
# Wound Analysis Schemas (Ground Truth)
# ============================================================================

class WoundDimensions(BaseModel):
    """Wound dimensions in cm"""
    length_cm: float = Field(gt=0, le=50, description="Wound length in cm")
    width_cm: float = Field(gt=0, le=50, description="Wound width in cm")


class TissueComposition(BaseModel):
    """Tissue type percentages"""
    granulation: int = Field(ge=0, le=100, description="Granulation tissue %")
    slough: int = Field(ge=0, le=100, description="Slough tissue %")
    eschar: int = Field(ge=0, le=100, description="Eschar/necrotic tissue %")
    
    @field_validator('granulation', 'slough', 'eschar')
    @classmethod
    def validate_percentage(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Percentage must be between 0 and 100")
        return v


class Exudate(BaseModel):
    """Wound exudate characteristics"""
    amount: Literal["none", "minimal", "moderate", "heavy"]
    type: Literal["serous", "sanguineous", "purulent", "serosanguineous"]


class WoundAnnotation(BaseModel):
    """Complete wound analysis annotation (ground truth)"""
    dimensions: WoundDimensions
    tissue_composition: TissueComposition
    exudate: Exudate
    surrounding_skin: Literal["intact", "macerated", "erythematous", "indurated"]
    wound_bed_color: str = Field(min_length=3, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "dimensions": {"length_cm": 4.2, "width_cm": 3.1},
                "tissue_composition": {"granulation": 65, "slough": 30, "eschar": 5},
                "exudate": {"amount": "moderate", "type": "serous"},
                "surrounding_skin": "intact",
                "wound_bed_color": "pink-red with yellow patches"
            }
        }


# ============================================================================
# VLM Training Sample (Image → Structured Analysis)
# ============================================================================

class VLMMessageContent(BaseModel):
    """Content item in a VLM message"""
    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None


class VLMMessage(BaseModel):
    """Single message in VLM chat format"""
    role: Literal["user", "assistant", "system"]
    content: Union[str, List[VLMMessageContent]]


class VLMTrainingSample(BaseModel):
    """Training sample for VLM (MedGemma 4B)"""
    messages: List[VLMMessage]
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Additional metadata (wound_id, timepoint, etc.)"
    )
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        if len(v) < 2:
            raise ValueError("Must have at least user and assistant messages")
        if v[0].role != "user":
            raise ValueError("First message must be from user")
        if v[-1].role != "assistant":
            raise ValueError("Last message must be from assistant")
        return v


# ============================================================================
# LLM Training Sample (Text Analysis → Classification)
# ============================================================================

class LLMMessage(BaseModel):
    """Single message in LLM chat format"""
    role: Literal["user", "assistant", "system"]
    content: str


class ClassificationResult(BaseModel):
    """Ground truth classification result"""
    classification: Literal["Improving", "Stable", "Worsening"]
    confidence: int = Field(ge=0, le=100, description="Confidence score 0-100")
    rationale: str = Field(min_length=10, max_length=500)


class LLMTrainingSample(BaseModel):
    """Training sample for LLM (MedGemma 27B)"""
    messages: List[LLMMessage]
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Additional metadata (wound_id, timepoints, etc.)"
    )
    
    @field_validator('messages')
    @classmethod
    def validate_messages(cls, v):
        if len(v) < 2:
            raise ValueError("Must have at least user and assistant messages")
        return v


# ============================================================================
# Dataset Metadata
# ============================================================================

class DatasetMetadata(BaseModel):
    """Metadata for the generated dataset"""
    dataset_type: Literal["vlm", "llm"]
    num_samples: int = Field(ge=0)
    generation_date: datetime
    split: Literal["train", "validation", "test"]
    source_images_dir: str
    schema_version: str = "1.0"
    class_distribution: Optional[Dict[str, int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_type": "llm",
                "num_samples": 800,
                "generation_date": "2026-02-07T23:53:00",
                "split": "train",
                "source_images_dir": "data/synthetic_wounds",
                "schema_version": "1.0",
                "class_distribution": {
                    "Improving": 450,
                    "Stable": 200,
                    "Worsening": 150
                }
            }
        }


# ============================================================================
# Export Utilities
# ============================================================================

def vlm_sample_to_dict(sample: VLMTrainingSample) -> dict:
    """Convert VLM sample to dictionary for serialization"""
    return sample.model_dump(exclude_none=True)


def llm_sample_to_dict(sample: LLMTrainingSample) -> dict:
    """Convert LLM sample to dictionary for serialization"""
    return sample.model_dump(exclude_none=True)
