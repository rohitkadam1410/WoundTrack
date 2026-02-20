"""
WoundTrack Enhanced Longitudinal Pipeline - Standalone Demonstration

This script demonstrates the complete enhanced longitudinal pipeline with
mock data, showing integration of all components and report generation.

Usage:
    python woundtrack_enhanced_demo.py
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unified_pipeline import (
    analyze_wound_progression,
    WoundSequenceAnalysis,
    TimePointAnalysis,
    generate_progression_summary
)
from report_generator import (
    WoundProgressionReport,
    generate_comprehensive_report
)


# ============================================================================
# MOCK COMPONENTS (Replace with actual implementations)
# ============================================================================

class MockWoundVision:
    """Mock WoundVision for demonstration."""
    
    def __init__(self):
        self.call_count = 0
        
    def analyze(self, image_path):
        """Simulate wound vision analysis with realistic progression."""
        self.call_count += 1
        
        # Simulate healing progression
        base_length = 5.0 - (self.call_count * 0.3)  # Decreasing
        base_width = 3.0 - (self.call_count * 0.2)
        
        # Tissue improves over time
        granulation = min(20 + (self.call_count * 12), 80)
        slough = max(50 - (self.call_count * 10), 10)
        eschar = max(30 - (self.call_count * 5), 5)
        
        return {
            'dimensions': {
                'length_cm': max(base_length, 1.0),
                'width_cm': max(base_width, 0.8)
            },
            'tissue_composition': {
                'granulation_percent': granulation,
                'slough_percent': slough,
                'eschar_percent': eschar
            },
            'exudate': {
                'amount': 'moderate' if self.call_count < 3 else 'minimal',
                'type': 'serous'
            },
            'surrounding_skin': 'erythematous' if self.call_count < 2 else 'intact',
            'wound_bed_color': 'red-pink'
        }


class MockWoundScore:
    """Mock WoundScore for demonstration."""
    
    def calculate_push_score(self, features):
        """Calculate PUSH score based on features."""
        area = features.get('area_cm2', 0)
        
        # Area score (0-10)
        if area == 0:
            area_score = 0
        elif area < 0.3:
            area_score = 1
        elif area < 0.7:
            area_score = 2
        elif area < 1.0:
            area_score = 3
        elif area < 3.0:
            area_score = 4
        elif area < 6.0:
            area_score = 5
        elif area < 12.0:
            area_score = 6
        elif area < 24.0:
            area_score = 8
        else:
            area_score = 10
        
        # Exudate (mock: decreases over time)
        exudate_score = max(3 - int(area / 5), 0)
        
        # Tissue type (mock: based on necrosis)
        necrosis = features.get('necrosis_pct', 0)
        if necrosis > 50:
            tissue_score = 4
        elif necrosis > 25:
            tissue_score = 3
        elif features.get('slough_pct', 0) > 50:
            tissue_score = 2
        elif features.get('granulation_pct', 0) > 75:
            tissue_score = 0
        else:
            tissue_score = 1
            
        return area_score + exudate_score + tissue_score
    
    def calculate_wagner_grade(self, features):
        """Calculate Wagner grade."""
        area = features.get('area_cm2', 0)
        necrosis = features.get('necrosis_pct', 0)
        
        if area == 0:
            return 0
        elif necrosis > 30:
            return 3
        elif area > 10:
            return 2
        else:
            return 1


class MockRiskFusion:
    """Mock RiskFusion for demonstration."""
    
    def assess_risk(self, patient_history, wound_features):
        """Assess amputation risk."""
        base_risk = 0.4
        
        # Add risk factors
        if patient_history.get('HbA1c', 0) > 8.0:
            base_risk += 0.15
        if patient_history.get('Smoker', False):
            base_risk += 0.10
        if patient_history.get('age', 0) > 70:
            base_risk += 0.05
            
        # Reduce risk based on wound improvement
        area = wound_features.get('area_cm2', 10)
        if area < 5:
            base_risk -= 0.15
        if area < 2:
            base_risk -= 0.10
            
        return max(0.1, min(0.9, base_risk))


class MockHealCast:
    """Mock HealCast for demonstration."""
    
    def predict_closure(self, days_history, area_history):
        """Predict days to closure."""
        if len(area_history) < 2:
            return 60
        
        # Calculate healing rate
        area_change = area_history[-1] - area_history[0]
        days_elapsed = days_history[-1] - days_history[0]
        
        if days_elapsed == 0 or area_change >= 0:
            return 90  # Not healing or worsening
        
        rate_per_day = abs(area_change) / days_elapsed
        current_area = area_history[-1]
        
        if rate_per_day == 0:
            return 120
        
        days_to_close = int(current_area / rate_per_day)
        return min(days_to_close, 120)


class MockCareGuide:
    """Mock CareGuide for demonstration."""
    
    def determine_action(self, risk_prob, push_score, days_to_close):
        """Determine care action."""
        if risk_prob > 0.7 or push_score > 12:
            priority = 'Urgent'
            rationale = 'High risk or severe wound'
        elif risk_prob > 0.5 or push_score > 8:
            priority = 'Escalate'
            rationale = 'Moderate risk requiring enhanced monitoring'
        else:
            priority = 'Routine'
            rationale = 'Low risk, continue current treatment'
        
        return {
            'priority': priority,
            'rationale': rationale,
            'actions': [
                'Continue current dressing protocol',
                'Monitor for signs of infection',
                'Ensure patient compliance'
            ]
        }


# ============================================================================
# DEMO DATA GENERATION
# ============================================================================

def create_mock_images(output_dir='data/demo_wounds'):
    """Create mock wound images for demonstration."""
    os.makedirs(output_dir, exist_ok=True)
    
    image_paths = []
    
    for day in [0, 7, 14, 21, 28]:
        # Create simple colored image representing wound
        img = Image.new('RGB', (512, 512), color=(180, 100, 100))
        
        # Add some variation to show "healing"
        size = int(300 - day * 5)  # Wound getting smaller
        color_val = min(180 + day * 2, 220)  # Wound bed improving
        
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse(
            [(256-size//2, 256-size//2), (256+size//2, 256+size//2)],
            fill=(color_val, 80+day, 80+day)
        )
        
        filename = f'PT_DEMO_day{day:03d}.jpg'
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        image_paths.append(filepath)
        
    return image_paths


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def run_enhanced_pipeline_demo():
    """Run complete demonstration of enhanced pipeline."""
    
    print("="*80)
    print("WOUNDTRACK ENHANCED LONGITUDINAL PIPELINE DEMONSTRATION")
    print("="*80)
    print()
    
    # Step 1: Create mock data
    print("[Step 1/6] Creating mock wound images...")
    image_paths = create_mock_images()
    print(f"  ✓ Created {len(image_paths)} mock wound images")
    print()
    
    # Step 2: Prepare sequence data
    print("[Step 2/6] Preparing wound sequence data...")
    sequence = []
    for i, (day, path) in enumerate(zip([0, 7, 14, 21, 28], image_paths)):
        sequence.append({
            'image_path': path,
            'day': day,
            'notes': f'Assessment {i+1} - Day {day}'
        })
    print(f"  ✓ Sequence prepared: {len(sequence)} timepoints")
    print()
    
    # Step 3: Patient data
    print("[Step 3/6] Preparing patient clinical data...")
    patient_history = {
        'patient_id': 'PT-DEMO-001',
        'HbA1c': 8.2,
        'Smoker': False,
        'age': 65,
        'diabetes_duration_years': 15
    }
    print(f"  ✓ Patient ID: {patient_history['patient_id']}")
    print(f"  ✓ HbA1c: {patient_history['HbA1c']}")
    print(f"  ✓ Age: {patient_history['age']}")
    print()
    
    # Step 4: Initialize components
    print("[Step 4/6] Initializing analysis components...")
    wound_vision = MockWoundVision()
    wound_score = MockWoundScore()
    risk_fusion = MockRiskFusion()
    heal_cast = MockHealCast()
    care_guide = MockCareGuide()
    print("  ✓ WoundVision initialized")
    print("  ✓ WoundScore initialized")
    print("  ✓ RiskFusion initialized")
    print("  ✓ HealCast initialized")
    print("  ✓ CareGuide initialized")
    print()
    
    # Step 5: Run unified pipeline
    print("[Step 5/6] Running unified wound progression analysis...")
    print("  This integrates all 5 components with longitudinal tracking...")
    print()
    
    analysis = analyze_wound_progression(
        sequence_images=sequence,
        patient_history=patient_history,
        wound_vision=wound_vision,
        wound_score=wound_score,
        risk_fusion=risk_fusion,
        heal_cast=heal_cast,
        care_guide=care_guide
    )
    
    print("  ✓ Analysis complete!")
    print(f"  ✓ Processed {len(analysis.timepoints)} timepoints")
    print(f"  ✓ Overall Status: {analysis.overall_status}")
    print(f"  ✓ Alerts Generated: {len(analysis.alerts)}")
    print()
    
    # Step 6: Generate reports
    print("[Step 6/6] Generating comprehensive reports...")
    
    # Create output directory
    output_dir = 'reports/demo'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all reports
    report_files = generate_comprehensive_report(
        analysis,
        output_dir=output_dir,
        include_detailed=True
    )
    
    print(f"  ✓ Text report: {report_files['text_report']}")
    print(f"  ✓ Visual dashboard: {report_files['visual_dashboard']}")
    print(f"  ✓ Summary card: {report_files['summary_card']}")
    print()
    
    # Display summary
    print("="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    summary = analysis.get_summary()
    print(f"\nWound ID: {summary['wound_id']}")
    print(f"Duration: {summary['duration_days']} days")
    print(f"Timepoints: {summary['timepoints_analyzed']}")
    print(f"\nOverall Status: {summary['overall_status'].upper()}")
    print(f"\nArea Change: {summary['total_area_change_pct']:+.1f}%")
    print(f"Avg Healing Velocity: {summary['avg_healing_velocity']:.2f} cm²/week")
    print(f"\nHealing Trend: {summary['healing_trend'].upper()}")
    print(f"Risk Trend: {summary['risk_trend'].upper()}")
    print(f"\nCritical Alerts: {summary['critical_alerts']}")
    print(f"Warnings: {summary['warnings']}")
    
    # Display alerts
    if analysis.alerts:
        print("\n" + "="*80)
        print("CLINICAL ALERTS")
        print("="*80)
        for i, alert in enumerate(analysis.alerts, 1):
            print(f"\n{i}. [{alert.severity.upper()}] {alert.category}")
            print(f"   {alert.message}")
            print(f"   Day: {alert.triggered_at_day}")
            if alert.recommendations:
                print(f"   Recommendations: {', '.join(alert.recommendations[:2])}")
    
    # Display progression summary
    print("\n" + "="*80)
    print("PROGRESSION SUMMARY")
    print("="*80)
    print(generate_progression_summary(analysis))
    
    # Show where to find reports
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print(f"\n📄 Open the text report in: {report_files['text_report']}")
    print(f"📊 Open the visual dashboard in browser: {report_files['visual_dashboard']}")
    print(f"📈 Open the summary card in browser: {report_files['summary_card']}")
    print()
    print("All reports have been generated successfully!")
    print("="*80)
    
    return analysis, report_files


def display_detailed_metrics(analysis):
    """Display detailed metrics from analysis."""
    
    print("\n" + "="*80)
    print("DETAILED LONGITUDINAL METRICS")
    print("="*80)
    
    metrics = analysis.longitudinal_metrics
    
    print("\n📏 Area Progression:")
    for i, (tp, area) in enumerate(zip(analysis.timepoints, metrics.area_progression)):
        print(f"  Day {tp.day:3d}: {area:6.2f} cm²")
    
    if metrics.area_changes:
        print("\n📈 Area Changes:")
        for i, change in enumerate(metrics.area_changes):
            if i + 1 < len(analysis.timepoints):
                print(f"  Day {analysis.timepoints[i].day} → Day {analysis.timepoints[i+1].day}: {change:+.1f}%")
    
    print("\n🏥 Clinical Scores:")
    if metrics.push_score_history:
        print("  PUSH Scores:", " → ".join(map(str, metrics.push_score_history)))
    if metrics.wagner_grade_history:
        print("  Wagner Grades:", " → ".join(map(str, metrics.wagner_grade_history)))
    
    print("\n⚠️  Risk Trajectory:")
    for i, (tp, risk) in enumerate(zip(analysis.timepoints, metrics.risk_history)):
        print(f"  Day {tp.day:3d}: {risk:5.1%}")
    
    if metrics.healing_velocity:
        print("\n⚡ Healing Velocity (cm²/week):")
        for i, vel in enumerate(metrics.healing_velocity):
            if i + 1 < len(analysis.timepoints):
                print(f"  Day {analysis.timepoints[i].day} → Day {analysis.timepoints[i+1].day}: {vel:+.2f}")
    
    print("\n🎯 Care Priority:")
    for i, (tp, priority) in enumerate(zip(analysis.timepoints, metrics.priority_history)):
        print(f"  Day {tp.day:3d}: {priority}")


if __name__ == "__main__":
    print("\n" + "🏥 "*20)
    print("Starting WoundTrack Enhanced Pipeline Demonstration")
    print("🏥 "*20 + "\n")
    
    try:
        # Run main demo
        analysis, report_files = run_enhanced_pipeline_demo()
        
        # Show detailed metrics
        display_detailed_metrics(analysis)
        
        print("\n✅ Demonstration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
