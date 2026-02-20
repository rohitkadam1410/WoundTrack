"""
Usage Examples for Enhanced WoundTrack Longitudinal Pipeline

This file demonstrates how to use the unified pipeline for comprehensive
wound progression analysis.
"""

from src.unified_pipeline import (
    analyze_wound_progression,
    generate_progression_summary,
    WoundSequenceAnalysis
)
from src.preprocessing import WoundImagePreprocessor
# Assume these are already imported from your notebook or existing modules
# from wound_vision import WoundVision
# from wound_score import WoundScore
# from risk_fusion import RiskFusion
# from heal_cast import HealCast
# from care_guide import CareGuide


def example_1_simple_analysis():
    """Example 1: Basic wound progression analysis."""
    
    # Define wound image sequence
    sequence = [
        {'image_path': 'data/wounds/PT1001_day0.jpg', 'day': 0, 'notes': 'Initial presentation'},
        {'image_path': 'data/wounds/PT1001_day7.jpg', 'day': 7, 'notes': 'First follow-up'},
        {'image_path': 'data/wounds/PT1001_day14.jpg', 'day': 14, 'notes': 'Second follow-up'},
        {'image_path': 'data/wounds/PT1001_day21.jpg', 'day': 21, 'notes': 'Third follow-up'}
    ]
    
    # Patient clinical history
    patient_history = {
        'patient_id': 'PT-1001',
        'HbA1c': 8.2,
        'Smoker': False,
        'age': 65,
        'diabetes_duration_years': 15
    }
    
    # Initialize components (using your existing instances)
    # preprocessor = WoundImagePreprocessor()
    # wound_vision = WoundVision(pipe=pipe, core_instruction=CORE_INSTRUCTION)
    # wound_score = WoundScore()
    # risk_fusion = RiskFusion()
    # heal_cast = HealCast()
    # care_guide = CareGuide()
    
    # Run unified analysis
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide,
        preprocessor=preprocessor
    )
    
    # Print summary
    print(generate_progression_summary(analysis))
    
    # Access specific metrics
    print(f"\nArea progression: {analysis.longitudinal_metrics.area_progression}")
    print(f"Healing velocity: {analysis.longitudinal_metrics.healing_velocity}")
    print(f"Overall status: {analysis.overall_status}")
    
    # Check alerts
    for alert in analysis.alerts:
        print(f"\n[{alert.severity}] {alert.message}")
        print(f"Recommendations: {alert.recommendations}")
        
    return analysis


def example_2_detailed_timepoint_analysis():
    """Example 2: Detailed per-timepoint analysis."""
    
    sequence = [
        {'image_path': 'data/wounds/PT2001_day0.jpg', 'day': 0},
        {'image_path': 'data/wounds/PT2001_day7.jpg', 'day': 7},
        {'image_path': 'data/wounds/PT2001_day14.jpg', 'day': 14}
    ]
    
    patient_history = {
        'patient_id': 'PT-2001',
        'HbA1c': 7.5,
        'Smoker': True,
        'age': 58
    }
    
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide
    )
    
    # Detailed per-timepoint analysis
    for i, tp in enumerate(analysis.timepoints):
        print(f"\n=== Timepoint {i+1} (Day {tp.day}) ===")
        print(f"Wound Area: {tp.wound_area:.2f} cm²")
        print(f"PUSH Score: {tp.clinical_scores['push']}")
        print(f"Wagner Grade: {tp.clinical_scores['wagner']}")
        print(f"Risk: {tp.risk_assessment:.1%}")
        print(f"Forecast: {tp.healing_forecast} days to closure")
        print(f"Priority: {tp.care_recommendation['priority']}")
        print(f"Tissue Composition:")
        for tissue, pct in tp.tissue_composition.items():
            print(f"  {tissue}: {pct}%")
            
    return analysis


def example_3_trend_monitoring():
    """Example 3: Focus on trend analysis and monitoring."""
    
    sequence = [
        {'image_path': f'data/wounds/PT3001_day{day}.jpg', 'day': day}
        for day in [0, 7, 14, 21, 28]  # 5 timepoints
    ]
    
    patient_history = {
        'patient_id': 'PT-3001',
        'HbA1c': 9.1,
        'Smoker': False,
        'age': 72
    }
    
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide
    )
    
    # Trend analysis
    print("=== TREND ANALYSIS ===")
    print(f"Healing Trend: {analysis.trends.healing_trend}")
    print(f"Area Trend: {analysis.trends.area_trend}")
    print(f"Risk Trend: {analysis.trends.risk_trend}")
    print(f"Acceleration: {analysis.trends.acceleration}")
    
    # Check for anomalies
    if analysis.trends.anomalies_detected:
        print("\n=== ANOMALIES DETECTED ===")
        for anomaly in analysis.trends.anomalies_detected:
            print(f"Type: {anomaly['type']}")
            print(f"Timepoint: {anomaly['timepoint']}")
            print(f"Metric: {anomaly['metric']}")
            print(f"Value: {anomaly['value']:.2f}")
            
    # Longitudinal metrics evolution
    print("\n=== METRIC EVOLUTION ===")
    print(f"Area changes: {[f'{x:+.1f}%' for x in analysis.longitudinal_metrics.area_changes]}")
    print(f"PUSH scores: {analysis.longitudinal_metrics.push_score_history}")
    print(f"Risk levels: {[f'{x:.1%}' for x in analysis.longitudinal_metrics.risk_history]}")
    
    return analysis


def example_4_batch_processing():
    """Example 4: Process multiple patients in batch."""
    
    patients_data = [
        {
            'patient_id': 'PT-4001',
            'sequence': [
                {'image_path': f'data/wounds/PT4001_day{d}.jpg', 'day': d}
                for d in [0, 7, 14]
            ],
            'history': {'HbA1c': 7.8, 'Smoker': False, 'age': 60}
        },
        {
            'patient_id': 'PT-4002',
            'sequence': [
                {'image_path': f'data/wounds/PT4002_day{d}.jpg', 'day': d}
                for d in [0, 7, 14, 21]
            ],
            'history': {'HbA1c': 8.5, 'Smoker': True, 'age': 55}
        },
        {
            'patient_id': 'PT-4003',
            'sequence': [
                {'image_path': f'data/wounds/PT4003_day{d}.jpg', 'day': d}
                for d in [0, 7]
            ],
            'history': {'HbA1c': 6.9, 'Smoker': False, 'age': 68}
        }
    ]
    
    results = []
    
    for patient_data in patients_data:
        print(f"\nProcessing {patient_data['patient_id']}...")
        
        analysis = analyze_wound_progression(
            sequence_images=patient_data['sequence'],
            patient_history=patient_data['history'],
            wound_vision=wound_vision,
            wound_score=wound_score,
            risk_fusion=risk_fusion,
            heal_cast=heal_cast,
            care_guide=care_guide
        )
        
        results.append(analysis)
        
        # Quick summary
        summary = analysis.get_summary()
        print(f"  Status: {summary['overall_status']}")
        print(f"  Area change: {summary['total_area_change_pct']:+.1f}%")
        print(f"  Alerts: {summary['critical_alerts']} critical, {summary['warnings']} warnings")
        
    # Compare patients
    print("\n=== COHORT SUMMARY ===")
    for analysis in results:
        summary = analysis.get_summary()
        print(f"{summary['wound_id']}: {summary['overall_status']} "
              f"({summary['total_area_change_pct']:+.1f}% change)")
        
    return results


def example_5_integration_with_reporting():
    """Example 5: Integration with reporting and visualization."""
    
    sequence = [
        {'image_path': f'data/wounds/PT5001_day{d}.jpg', 'day': d}
        for d in [0, 7, 14, 21, 28, 35]
    ]
    
    patient_history = {
        'patient_id': 'PT-5001',
        'HbA1c': 7.2,
        'Smoker': False,
        'age': 63
    }
    
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide
    )
    
    # Generate text report
    report_text = generate_progression_summary(analysis)
    
    # Save report
    with open(f'{patient_history["patient_id"]}_report.txt', 'w') as f:
        f.write(report_text)
        
    # Create visualization data
    import plotly.graph_objects as go
    
    days = [tp.day for tp in analysis.timepoints]
    areas = analysis.longitudinal_metrics.area_progression
    
    fig = go.Figure()
    
    # Area progression
    fig.add_trace(go.Scatter(
        x=days,
        y=areas,
        mode='lines+markers',
        name='Wound Area',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title=f'Wound Progression - {patient_history["patient_id"]}',
        xaxis_title='Days',
        yaxis_title='Area (cm²)',
        template='plotly_white'
    )
    
    fig.write_html(f'{patient_history["patient_id"]}_progression.html')
    
    print(f"Report saved to {patient_history['patient_id']}_report.txt")
    print(f"Chart saved to {patient_history['patient_id']}_progression.html")
    
    return analysis


def example_6_real_time_monitoring():
    """Example 6: Simulating real-time monitoring with incremental updates."""
    
    patient_history = {
        'patient_id': 'PT-6001',
        'HbA1c': 8.0,
        'Smoker': False,
        'age': 70
    }
    
    # Initialize with baseline
    initial_sequence = [
        {'image_path': 'data/wounds/PT6001_day0.jpg', 'day': 0, 
         'notes': 'Baseline assessment'}
    ]
    
    analysis = analyze_wound_progression(
        sequence_images=initial_sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide
    )
    
    print("=== BASELINE ===")
    print(f"Initial area: {analysis.timepoints[0].wound_area:.2f} cm²")
    print(f"Initial risk: {analysis.timepoints[0].risk_assessment:.1%}")
    
    # Simulate adding new timepoints incrementally
    new_timepoints = [
        {'image_path': 'data/wounds/PT6001_day7.jpg', 'day': 7},
        {'image_path': 'data/wounds/PT6001_day14.jpg', 'day': 14},
        {'image_path': 'data/wounds/PT6001_day21.jpg', 'day': 21}
    ]
    
    for new_tp in new_timepoints:
        print(f"\n=== Adding Day {new_tp['day']} ===")
        
        # Re-run analysis with updated sequence
        updated_sequence = initial_sequence + new_timepoints[:new_timepoints.index(new_tp)+1]
        
        analysis = analyze_wound_progression(
            sequence_images=updated_sequence,
            patient_history=patient_history,
            wound_vision=wound_vision,
            wound_score=wound_score,
            risk_fusion=risk_fusion,
            heal_cast=heal_cast,
            care_guide=care_guide
        )
        
        # Show updated metrics
        latest = analysis.timepoints[-1]
        print(f"Current area: {latest.wound_area:.2f} cm²")
        print(f"Change from baseline: {analysis.longitudinal_metrics.area_changes[-1]:+.1f}%")
        print(f"Healing trend: {analysis.trends.healing_trend}")
        
        # Check for new alerts
        new_alerts = [a for a in analysis.alerts if a.triggered_at_day == new_tp['day']]
        if new_alerts:
            print(f"NEW ALERT: {new_alerts[0].message}")
            
    return analysis


if __name__ == "__main__":
    # Run examples
    print("Example 1: Simple Analysis")
    print("="*50)
    # example_1_simple_analysis()
    
    print("\n\nExample 2: Detailed Timepoint Analysis")
    print("="*50)
    # example_2_detailed_timepoint_analysis()
    
    print("\n\nExample 3: Trend Monitoring")
    print("="*50)
    # example_3_trend_monitoring()
    
    print("\n\nExample 4: Batch Processing")
    print("="*50)
    # example_4_batch_processing()
    
    print("\n\nExample 5: Integration with Reporting")
    print("="*50)
    # example_5_integration_with_reporting()
    
    print("\n\nExample 6: Real-time Monitoring")
    print("="*50)
    # example_6_real_time_monitoring()
