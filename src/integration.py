"""
Integration Module for WoundTrack Enhanced Pipeline

This module provides integration between the existing notebook components
and the new enhanced pipeline.
"""

import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unified_pipeline import (
    analyze_wound_progression,
    WoundSequenceAnalysis,
    TimePointAnalysis,
    LongitudinalMetrics,
    TrendAnalysis,
    ClinicalAlert,
    generate_progression_summary
)

from report_generator import (
    WoundProgressionReport,
    generate_comprehensive_report
)


def integrate_with_notebook_components(
    wound_vision,
    preprocessor=None,
    core_instruction=None
):
    """
    Create integration helpers for notebook components.
    
    Args:
        wound_vision: WoundVision instance from notebook
        preprocessor: Optional WoundImagePreprocessor
        core_instruction: Optional CORE_INSTRUCTION string
        
    Returns:
        dict: Integration helpers
    """
    
    # Import or create mock components for missing parts
    try:
        from wound_score import WoundScore
    except ImportError:
        from .mock_components import MockWoundScore as WoundScore
    
    try:
        from risk_fusion import RiskFusion
    except ImportError:
        from .mock_components import MockRiskFusion as RiskFusion
    
    try:
        from heal_cast import HealCast
    except ImportError:
        from .mock_components import MockHealCast as HealCast
    
    try:
        from care_guide import CareGuide
    except ImportError:
        from .mock_components import MockCareGuide as CareGuide
    
    return {
        'wound_vision': wound_vision,
        'wound_score': WoundScore(),
        'risk_fusion': RiskFusion(),
        'heal_cast': HealCast(),
        'care_guide': CareGuide(),
        'preprocessor': preprocessor
    }


def analyze_notebook_sequence(
    sequence_images,
    patient_history,
    wound_vision,
    **kwargs
):
    """
    Wrapper function that matches notebook usage patterns.
    
    Args:
        sequence_images: List of image paths or dicts with 'image_path', 'day'
        patient_history: Patient clinical data dict
        wound_vision: WoundVision instance
        **kwargs: Additional components (wound_score, risk_fusion, etc.)
        
    Returns:
        WoundSequenceAnalysis: Complete analysis object
    """
    
    # Normalize sequence format
    if isinstance(sequence_images[0], str):
        # Just paths, create sequence dicts
        sequence = [
            {'image_path': img, 'day': i * 7}
            for i, img in enumerate(sequence_images)
        ]
    else:
        sequence = sequence_images
    
    # Get or create components
    components = integrate_with_notebook_components(wound_vision)
    components.update(kwargs)
    
    # Run analysis
    return analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        **components
    )


def quick_analysis_and_report(
    sequence_images,
    patient_history,
    wound_vision,
    output_dir='reports',
    **kwargs
):
    """
    One-line function for complete analysis + reports.
    
    Args:
        sequence_images: List of image paths or sequence dicts
        patient_history: Patient data
        wound_vision: WoundVision instance
        output_dir: Where to save reports
        **kwargs: Additional components
        
    Returns:
        tuple: (analysis, report_files)
    """
    
    # Run analysis
    analysis = analyze_notebook_sequence(
        sequence_images,
        patient_history,
        wound_vision,
        **kwargs
    )
    
    # Generate reports
    report_files = generate_comprehensive_report(
        analysis,
        output_dir=output_dir,
        include_detailed=True
    )
    
    return analysis, report_files


# Convenience functions for notebook usage

def get_wound_status(analysis):
    """Get concise status summary."""
    return {
        'status': analysis.overall_status,
        'area_change_pct': analysis.longitudinal_metrics.total_area_change_pct,
        'healing_trend': analysis.trends.healing_trend,
        'risk_trend': analysis.trends.risk_trend,
        'critical_alerts': len([a for a in analysis.alerts if a.severity == 'critical']),
        'current_area': analysis.timepoints[-1].wound_area if analysis.timepoints else 0
    }


def print_quick_summary(analysis):
    """Print quick summary to console."""
    summary = get_wound_status(analysis)
    
    print(f"\n{'='*60}")
    print(f"WOUND STATUS: {summary['status'].upper()}")
    print(f"{'='*60}")
    print(f"Area Change: {summary['area_change_pct']:+.1f}%")
    print(f"Current Area: {summary['current_area']:.2f} cm²")
    print(f"Healing Trend: {summary['healing_trend'].upper()}")
    print(f"Risk Trend: {summary['risk_trend'].upper()}")
    print(f"Critical Alerts: {summary['critical_alerts']}")
    print(f"{'='*60}\n")


def export_for_ehr(analysis, patient_id=None):
    """
    Export analysis in EHR-compatible format.
    
    Args:
        analysis: WoundSequenceAnalysis object
        patient_id: Optional patient ID override
        
    Returns:
        dict: EHR-compatible JSON structure
    """
    
    return {
        'patient_id': patient_id or analysis.patient_history.get('patient_id'),
        'wound_id': analysis.wound_id,
        'assessment_date': datetime.now().isoformat(),
        'analysis_period': {
            'start_day': 0,
            'end_day': analysis.timepoints[-1].day if analysis.timepoints else 0,
            'num_assessments': len(analysis.timepoints)
        },
        'current_status': {
            'overall': analysis.overall_status,
            'wound_area_cm2': analysis.timepoints[-1].wound_area if analysis.timepoints else 0,
            'push_score': analysis.timepoints[-1].clinical_scores['push'] if analysis.timepoints else None,
            'wagner_grade': analysis.timepoints[-1].clinical_scores['wagner'] if analysis.timepoints else None,
            'amputation_risk': analysis.longitudinal_metrics.risk_history[-1] if analysis.longitudinal_metrics.risk_history else None
        },
        'progression': {
            'area_change_percent': analysis.longitudinal_metrics.total_area_change_pct,
            'healing_velocity_cm2_per_week': np.mean(analysis.longitudinal_metrics.healing_velocity) if analysis.longitudinal_metrics.healing_velocity else 0,
            'trend': analysis.trends.healing_trend
        },
        'alerts': [
            {
                'severity': alert.severity,
                'category': alert.category,
                'message': alert.message,
                'day': alert.triggered_at_day,
                'recommendations': alert.recommendations
            }
            for alert in analysis.alerts
        ],
        'recommendations': self._get_recommendations(analysis)
    }


def _get_recommendations(analysis):
    """Extract clinical recommendations."""
    recs = []
    
    if analysis.overall_status == 'deteriorating':
        recs.append("Urgent clinical review required")
        recs.append("Consider wound culture and vascular assessment")
    elif analysis.overall_status == 'stagnant_needs_intervention':
        recs.append("Treatment modification recommended")
        recs.append("Consider adjunctive therapies")
    else:
        recs.append("Continue current treatment protocol")
        recs.append("Maintain monitoring schedule")
    
    return recs


# For backward compatibility with notebook
def run_enhanced_longitudinal_analysis(
    loaded_wound_sequences,
    preprocessor,
    wound_vision,
    patient_history=None
):
    """
    Drop-in replacement for notebook's process_wound_sequences
    with enhanced longitudinal tracking.
    
    Args:
        loaded_wound_sequences: List of wound sequences
        preprocessor: WoundImagePreprocessor
        wound_vision: WoundVision instance
        patient_history: Optional patient data
        
    Returns:
        list: List of WoundSequenceAnalysis objects
    """
    
    results = []
    
    for sequence in loaded_wound_sequences:
        if not sequence:
            continue
        
        # Extract patient history from first item if not provided
        if patient_history is None:
            patient_history = {
                'patient_id': sequence[0].get('wound_id', 'UNKNOWN'),
                'HbA1c': 7.5,  # Default values
                'Smoker': False,
                'age': 65
            }
        
        # Prepare sequence
        sequence_images = [
            {
                'image_path': item['image_path'],
                'day': item['day'],
                'notes': item.get('notes', '')
            }
            for item in sequence
        ]
        
        # Run analysis
        analysis = analyze_notebook_sequence(
            sequence_images,
            patient_history,
            wound_vision,
            preprocessor=preprocessor
        )
        
        results.append(analysis)
    
    return results


if __name__ == "__main__":
    print("WoundTrack Integration Module")
    print("Import this module in your notebook to use enhanced pipeline")
    print("\nExample usage:")
    print("""
    from integration import quick_analysis_and_report
    
    analysis, reports = quick_analysis_and_report(
        sequence_images=my_images,
        patient_history=my_patient_data,
        wound_vision=wound_vision,
        output_dir='reports'
    )
    """)
