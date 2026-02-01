"""
Longitudinal analysis for wound progression tracking
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


def calculate_area_change(analysis_t0, analysis_t1):
    """
    Calculate percentage change in wound area between two timepoints
    
    Args:
        analysis_t0: Analysis dict for timepoint 0
        analysis_t1: Analysis dict for timepoint 1
        
    Returns:
        float: Percentage change (negative = healing, positive = worsening)
    """
    area_t0 = analysis_t0['dimensions']['length_cm'] * analysis_t0['dimensions']['width_cm']
    area_t1 = analysis_t1['dimensions']['length_cm'] * analysis_t1['dimensions']['width_cm']
    
    if area_t0 == 0:
        return 0.0
    
    change_percent = ((area_t1 - area_t0) / area_t0) * 100
    return change_percent


def calculate_tissue_shift(analysis_t0, analysis_t1):
    """
    Calculate changes in tissue composition between timepoints
    
    Args:
        analysis_t0: Analysis dict for timepoint 0
        analysis_t1: Analysis dict for timepoint 1
        
    Returns:
        dict: Tissue composition changes (granulation, slough, eschar)
    """
    shifts = {}
    for tissue_type in ['granulation', 'slough', 'eschar']:
        change = (analysis_t1['tissue_composition'].get(tissue_type, 0) - 
                 analysis_t0['tissue_composition'].get(tissue_type, 0))
        shifts[tissue_type] = change
    return shifts


def calculate_healing_velocity(sequence_data):
    """
    Calculate average healing rate (cm²/week)
    
    Args:
        sequence_data: List of timepoint analyses with 'day' and 'analysis' keys
        
    Returns:
        float: Healing velocity in cm²/week
    """
    if len(sequence_data) < 2:
        return 0.0
    
    first = sequence_data[0]
    last = sequence_data[-1]
    
    area_first = first['analysis']['dimensions']['length_cm'] * first['analysis']['dimensions']['width_cm']
    area_last = last['analysis']['dimensions']['length_cm'] * last['analysis']['dimensions']['width_cm']
    
    days_elapsed = last['day'] - first['day']
    if days_elapsed == 0:
        return 0.0
    
    weeks_elapsed = days_elapsed / 7
    velocity = (area_last - area_first) / weeks_elapsed
    
    return velocity


def create_wound_sequence_metadata(wound_id, baseline_img_path, num_timepoints=4, interval_days=7):
    """
    Create metadata structure for a wound sequence
    
    Args:
        wound_id: Unique identifier for the wound
        baseline_img_path: Path to Day 0 image
        num_timepoints: Number of timepoints in sequence
        interval_days: Days between timepoints
        
    Returns:
        list: Sequence metadata with timepoint info
    """
    sequence = []
    base_date = datetime.now()
    
    for i in range(num_timepoints):
        sequence.append({
            "wound_id": wound_id,
            "timepoint": i,
            "day": i * interval_days,
            "image_path": str(baseline_img_path) if i == 0 else f"synthetic/{wound_id}_day{i*interval_days}.png",
            "timestamp": (base_date + timedelta(days=i*interval_days)).isoformat()
        })
    
    return sequence


def generate_progression_summary(sequence_data):
    """
    Generate human-readable summary of wound progression
    
    Args:
        sequence_data: List of timepoint analyses
        
    Returns:
        dict: Summary statistics and assessment
    """
    if not sequence_data:
        return {}
    
    first_analysis = sequence_data[0]['analysis']
    last_analysis = sequence_data[-1]['analysis']
    
    area_change = calculate_area_change(first_analysis, last_analysis)
    tissue_shifts = calculate_tissue_shift(first_analysis, last_analysis)
    velocity = calculate_healing_velocity(sequence_data)
    
    # Determine overall trend
    if area_change < -15:
        trend = "Significant improvement"
    elif area_change < -5:
        trend = "Moderate improvement"
    elif area_change > 15:
        trend = "Significant deterioration"
    elif area_change > 5:
        trend = "Moderate deterioration"
    else:
        trend = "Stable"
    
    summary = {
        "overall_trend": trend,
        "total_area_change_percent": round(area_change, 1),
        "healing_velocity_cm2_per_week": round(velocity, 2),
        "tissue_composition_changes": tissue_shifts,
        "duration_days": sequence_data[-1]['day'] - sequence_data[0]['day'],
        "num_timepoints": len(sequence_data)
    }
    
    return summary
