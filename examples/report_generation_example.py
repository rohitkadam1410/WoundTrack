"""
Example: Complete Workflow with Report Generation

This example demonstrates the full workflow from wound sequence analysis
to comprehensive report generation.
"""

from src.unified_pipeline import analyze_wound_progression
from src.report_generator import (
    WoundProgressionReport,
    generate_comprehensive_report
)

# Assuming these are imported from your notebook or modules:
# from wound_vision import WoundVision
# from wound_score import WoundScore
# from risk_fusion import RiskFusion
# from heal_cast import HealCast
# from care_guide import CareGuide
# from preprocessing import WoundImagePreprocessor


def complete_workflow_example():
    """
    Complete workflow: Analysis + Report Generation
    """
    
    print("="*80)
    print("WOUNDTRACK COMPLETE WORKFLOW EXAMPLE")
    print("="*80)
    
    # Step 1: Define wound sequence
    print("\n[1/5] Preparing wound sequence data...")
    sequence = [
        {
            'image_path': 'data/wounds/patient_001/day_000.jpg',
            'day': 0,
            'notes': 'Initial presentation - diabetic foot ulcer'
        },
        {
            'image_path': 'data/wounds/patient_001/day_007.jpg',
            'day': 7,
            'notes': 'First follow-up - treatment initiated'
        },
        {
            'image_path': 'data/wounds/patient_001/day_014.jpg',
            'day': 14,
            'notes': 'Second follow-up - patient compliance good'
        },
        {
            'image_path': 'data/wounds/patient_001/day_021.jpg',
            'day': 21,
            'notes': 'Third follow-up - wound appears to be improving'
        },
        {
            'image_path': 'data/wounds/patient_001/day_028.jpg',
            'day': 28,
            'notes': 'One month assessment'
        }
    ]
    
    # Step 2: Patient clinical data
    patient_history = {
        'patient_id': 'PT-001',
        'HbA1c': 8.2,
        'Smoker': False,
        'age': 65,
        'diabetes_duration_years': 15,
        'comorbidities': ['hypertension', 'peripheral_neuropathy']
    }
    
    # Step 3: Run unified analysis
    print("[2/5] Running wound progression analysis...")
    print(f"      Processing {len(sequence)} timepoints...")
    
    """
    # Initialize components (uncomment when running with actual components)
    preprocessor = WoundImagePreprocessor()
    wound_vision = WoundVision(pipe=pipe, core_instruction=CORE_INSTRUCTION)
    wound_score = WoundScore()
    risk_fusion = RiskFusion()
    heal_cast = HealCast()
    care_guide = CareGuide()
    
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
    """
    
    # For demonstration, we'll show what the output would be
    print("      ✓ WoundVision analysis completed")
    print("      ✓ Clinical scoring completed")
    print("      ✓ Risk assessment completed")
    print("      ✓ Healing forecast completed")
    print("      ✓ Care recommendations generated")
    print("      ✓ Longitudinal metrics calculated")
    print("      ✓ Trend analysis performed")
    print("      ✓ Alerts generated")
    
    # Step 4: Generate comprehensive reports
    print("\n[3/5] Generating comprehensive reports...")
    
    """
    # Generate all reports (uncomment when analysis is available)
    report_files = generate_comprehensive_report(
        analysis,
        output_dir='reports',
        include_detailed=True
    )
    
    print(f"      ✓ Text report saved: {report_files['text_report']}")
    print(f"      ✓ Visual dashboard saved: {report_files['visual_dashboard']}")
    print(f"      ✓ Summary card saved: {report_files['summary_card']}")
    """
    
    # Step 5: Show what reports contain
    print("\n[4/5] Report Contents:")
    print("\n📄 TEXT REPORT includes:")
    print("   • Executive Summary with overall status")
    print("   • Key Metrics (area, velocity, tissue composition)")
    print("   • Clinical Scores (PUSH, Wagner) progression")
    print("   • Risk Assessment trajectory")
    print("   • Trend Analysis (improvement/plateau/worsening)")
    print("   • Clinical Alerts with severity levels")
    print("   • Detailed per-timepoint analysis")
    print("   • Clinical Recommendations")
    
    print("\n📊 VISUAL DASHBOARD includes 6 charts:")
    print("   1. Wound Area Progression (line chart)")
    print("   2. Tissue Composition Evolution (multi-line)")
    print("   3. Clinical Scores Trend (PUSH & Wagner)")
    print("   4. Risk Assessment Trajectory (with thresholds)")
    print("   5. Healing Velocity (bar chart)")
    print("   6. Care Priority Timeline")
    
    print("\n📈 SUMMARY CARD includes 6 indicators:")
    print("   1. Total Area Change (with delta)")
    print("   2. Average Healing Velocity")
    print("   3. Current Risk (gauge)")
    print("   4. PUSH Score Change")
    print("   5. Critical Alerts Count")
    print("   6. Analysis Duration")
    
    # Step 6: Example of custom report usage
    print("\n[5/5] Additional Report Options:")
    print("\n💡 Custom Report Generation:")
    
    print("""
    # Generate only text report
    report_gen = WoundProgressionReport(analysis)
    report_text = report_gen.generate_text_report(detailed=True)
    print(report_text)
    
    # Generate only visual dashboard
    fig = report_gen.generate_visual_report()
    fig.show()  # Display in browser
    
    # Generate only summary card
    summary_fig = report_gen.generate_summary_card()
    summary_fig.show()
    
    # Save reports with custom naming
    report_gen.save_text_report('custom_report.txt', detailed=False)
    """)
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)


def quick_report_example():
    """
    Quick example showing minimal code for report generation.
    """
    
    print("\n" + "="*80)
    print("QUICK REPORT GENERATION EXAMPLE")
    print("="*80)
    
    print("""
# Minimal code for complete analysis + reports:

from src.unified_pipeline import analyze_wound_progression
from src.report_generator import generate_comprehensive_report

# 1. Run analysis
analysis = analyze_wound_progression(
    sequence_images=my_sequence,
    patient_history=my_patient_data,
    wound_vision=wound_vision,
    wound_score=WoundScore(),
    risk_fusion=RiskFusion(),
    heal_cast=HealCast(),
    care_guide=CareGuide()
)

# 2. Generate all reports
reports = generate_comprehensive_report(
    analysis,
    output_dir='patient_reports',
    include_detailed=True
)

# That's it! You now have:
# - Text report with full analysis
# - Interactive visual dashboard
# - Summary card with key metrics
    """)
    
    print("Output files:")
    print("  • patient_reports/PT001_20260208_report.txt")
    print("  • patient_reports/PT001_20260208_dashboard.html")
    print("  • patient_reports/PT001_20260208_summary.html")


def sample_text_report_output():
    """
    Show sample text report output.
    """
    
    sample_report = """
================================================================================
WOUNDTRACK LONGITUDINAL ANALYSIS REPORT
================================================================================
Wound ID: WOUND-001
Patient ID: PT-001
Report Generated: 2026-02-08 22:30:00
Analysis Period: Day 0 to Day 28
Number of Assessments: 5

================================================================================
EXECUTIVE SUMMARY
================================================================================
Overall Status: HEALING WELL

The wound is showing positive healing progress with decreasing area and 
favorable risk profile.

================================================================================
KEY METRICS
================================================================================
Wound Area:
  Initial:  12.50 cm²
  Current:  6.80 cm²
  Change:   -45.6%

Healing Velocity:
  Average:  -1.46 cm²/week
  Current:  -1.20 cm²/week

Tissue Composition (Current):
  Granulation:           65%
  Slough:                25%
  Eschar:                10%

================================================================================
CLINICAL ASSESSMENT
================================================================================
PUSH Score Progression:
  Initial:  10
  Current:  6
  Trend:    10 → 9 → 8 → 7 → 6

Wagner Grade Progression:
  Initial:  2
  Current:  1
  Trend:    2 → 2 → 1 → 1 → 1

================================================================================
RISK ASSESSMENT
================================================================================
Amputation Risk Profile:
  Initial Risk:  45.0%
  Current Risk:  22.0%
  Average Risk:  32.4%
  Risk Trend:    IMPROVING

Risk Level Interpretation:
  Low risk - Continue standard monitoring

================================================================================
TREND ANALYSIS
================================================================================
Healing Trend:        IMPROVING
Area Trend:           IMPROVING
Risk Trend:           IMPROVING
Healing Acceleration: STABLE

================================================================================
CLINICAL RECOMMENDATIONS
================================================================================
CONTINUE CURRENT APPROACH:
  • Maintain current treatment protocol
  • Continue scheduled monitoring
  • Reinforce patient education
  • Monitor for any changes in trajectory

================================================================================
Report generated by WoundTrack AI System
This report is for clinical decision support. All recommendations should be
reviewed by qualified healthcare professionals in context of complete patient care.
================================================================================
    """
    
    print("\n" + "="*80)
    print("SAMPLE TEXT REPORT OUTPUT")
    print("="*80)
    print(sample_report)


if __name__ == "__main__":
    # Run examples
    complete_workflow_example()
    print("\n\n")
    quick_report_example()
    print("\n\n")
    sample_text_report_output()
