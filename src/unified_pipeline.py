"""
Enhanced WoundTrack Longitudinal Pipeline

Unified pipeline integrating all wound analysis components with comprehensive
longitudinal tracking and trend analysis.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class TimePointAnalysis:
    """Complete analysis results for a single timepoint."""
    day: int
    image_path: str
    processed_image_path: Optional[str] = None
    notes: str = ""
    timestamp: Optional[datetime] = None
    
    # Core analysis results
    vision_analysis: Optional[Dict] = None
    clinical_scores: Optional[Dict] = None
    risk_assessment: Optional[float] = None
    healing_forecast: Optional[int] = None
    care_recommendation: Optional[Dict] = None
    
    # Computed metrics
    wound_area: float = 0.0
    tissue_composition: Optional[Dict] = None
    
    def __post_init__(self):
        """Extract key metrics from analysis results."""
        if self.vision_analysis:
            dims = self.vision_analysis.get('dimensions', {})
            self.wound_area = dims.get('length_cm', 0) * dims.get('width_cm', 0)
            self.tissue_composition = self.vision_analysis.get('tissue_composition', {})


@dataclass
class LongitudinalMetrics:
    """Comprehensive longitudinal metrics across timepoints."""
    
    # Area metrics
    area_progression: List[float] = field(default_factory=list)
    area_changes: List[float] = field(default_factory=list)
    area_change_rate: List[float] = field(default_factory=list)
    total_area_change_pct: float = 0.0
    
    # Tissue evolution
    tissue_trends: Dict[str, List[float]] = field(default_factory=dict)
    tissue_shifts: List[Dict] = field(default_factory=list)
    
    # Clinical scores
    push_score_history: List[int] = field(default_factory=list)
    wagner_grade_history: List[int] = field(default_factory=list)
    score_improvements: List[int] = field(default_factory=list)
    
    # Risk trajectory
    risk_history: List[float] = field(default_factory=list)
    risk_trend: str = "stable"  # improving, stable, worsening
    avg_risk: float = 0.0
    
    # Healing metrics
    healing_velocity: List[float] = field(default_factory=list)
    avg_healing_velocity: float = 0.0
    forecast_accuracy: List[float] = field(default_factory=list)
    
    # Care evolution
    priority_history: List[str] = field(default_factory=list)
    escalations: int = 0


@dataclass
class TrendAnalysis:
    """Trend analysis results."""
    healing_trend: str = "unknown"  # improving, plateauing, worsening
    acceleration: str = "stable"  # accelerating, stable, decelerating
    anomalies_detected: List[Dict] = field(default_factory=list)
    statistical_significance: Dict[str, float] = field(default_factory=dict)
    
    # Specific trends
    area_trend: str = "stable"
    tissue_health_trend: str = "stable"
    risk_trend: str = "stable"


@dataclass  
class ClinicalAlert:
    """Clinical alert for concerning trends."""
    severity: str  # critical, warning, info
    category: str  # deterioration, stagnation, infection_risk, etc.
    message: str
    triggered_at_day: int
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class WoundSequenceAnalysis:
    """Complete analysis of a wound sequence over time."""
    
    def __init__(self, wound_id: str, patient_history: Dict):
        self.wound_id = wound_id
        self.patient_history = patient_history
        self.timepoints: List[TimePointAnalysis] = []
        self.longitudinal_metrics = LongitudinalMetrics()
        self.trends = TrendAnalysis()
        self.alerts: List[ClinicalAlert] = []
        self.overall_status: str = "unknown"
        self.created_at = datetime.now()
        
    def add_timepoint(self, analysis: TimePointAnalysis):
        """Add a new timepoint analysis."""
        self.timepoints.append(analysis)
        self._update_metrics()
        
    def _update_metrics(self):
        """Update longitudinal metrics after new timepoint."""
        # Always update area progression and risk — needed even for single visits
        self.longitudinal_metrics.area_progression = [
            tp.wound_area for tp in self.timepoints
        ]

        # Update risk trajectory — always
        self.longitudinal_metrics.risk_history = [
            tp.risk_assessment for tp in self.timepoints
            if tp.risk_assessment is not None
        ]
        if self.longitudinal_metrics.risk_history:
            self.longitudinal_metrics.avg_risk = np.mean(
                self.longitudinal_metrics.risk_history
            )

        # Update clinical scores — always
        self.longitudinal_metrics.push_score_history = [
            tp.clinical_scores.get('push', 0) for tp in self.timepoints
            if tp.clinical_scores
        ]
        self.longitudinal_metrics.wagner_grade_history = [
            tp.clinical_scores.get('wagner', 0) for tp in self.timepoints
            if tp.clinical_scores
        ]

        # Update tissue trends — always
        for tissue_type in ['granulation_percent', 'slough_percent', 'eschar_percent']:
            values = [
                tp.tissue_composition.get(tissue_type, 0)
                for tp in self.timepoints
                if tp.tissue_composition
            ]
            if values:
                self.longitudinal_metrics.tissue_trends[tissue_type] = values

        # Multi-timepoint-only metrics (velocity, area changes)
        if len(self.timepoints) >= 2:
            for i in range(1, len(self.timepoints)):
                prev_area = self.timepoints[i-1].wound_area
                curr_area = self.timepoints[i].wound_area
                if prev_area > 0:
                    change_pct = ((curr_area - prev_area) / prev_area) * 100
                    self.longitudinal_metrics.area_changes.append(change_pct)
                    days_diff = self.timepoints[i].day - self.timepoints[i-1].day
                    if days_diff > 0:
                        rate = (curr_area - prev_area) / days_diff * 7  # per week
                        self.longitudinal_metrics.healing_velocity.append(rate)

            # Total area change
            if self.timepoints[0].wound_area > 0:
                self.longitudinal_metrics.total_area_change_pct = (
                    (self.timepoints[-1].wound_area - self.timepoints[0].wound_area) /
                    self.timepoints[0].wound_area
                ) * 100


        # Update care priority history
        self.longitudinal_metrics.priority_history = [
            tp.care_recommendation.get('priority', 'Unknown')
            for tp in self.timepoints
            if tp.care_recommendation
        ]
        
    def analyze_trends(self):
        """Perform trend analysis - works with 1+ timepoints."""
        n = len(self.timepoints)
        areas = self.longitudinal_metrics.area_progression
        risks = self.longitudinal_metrics.risk_history

        if n == 1:
            # Single assessment: derive trend from risk score and care priority
            risk = risks[0] if risks else 0.5
            care = self.timepoints[0].care_recommendation or {}
            priority = care.get("priority", "Routine") if isinstance(care, dict) else "Routine"
            if priority == "Urgent" or risk > 0.7:
                self.trends.healing_trend = "worsening"
                self.trends.area_trend = "worsening"
                self.trends.risk_trend = "worsening"
            elif priority == "Escalate" or risk > 0.5:
                self.trends.healing_trend = "plateauing"
                self.trends.area_trend = "stable"
                self.trends.risk_trend = "stable"
            else:
                self.trends.healing_trend = "improving"
                self.trends.area_trend = "improving"
                self.trends.risk_trend = "improving"
            return

        if n >= 2:
            # Two or more points: simple before/after or slope comparison
            days = [tp.day for tp in self.timepoints]

            # Area trend (2 pts → direct diff; 3+ → linear regression)
            if len(areas) >= 3:
                slope = np.polyfit(days, areas, 1)[0]
            else:
                slope = (areas[-1] - areas[0]) / max((days[-1] - days[0]), 1)

            if slope < -0.1:
                self.trends.area_trend = "improving"
                self.trends.healing_trend = "improving"
            elif slope > 0.1:
                self.trends.area_trend = "worsening"
                self.trends.healing_trend = "worsening"
            else:
                self.trends.area_trend = "stable"
                self.trends.healing_trend = "plateauing"

            # Acceleration (needs 2 velocity readings)
            if len(self.longitudinal_metrics.healing_velocity) >= 2:
                velocities = self.longitudinal_metrics.healing_velocity
                if velocities[-1] < velocities[0]:
                    self.trends.acceleration = "decelerating"
                elif velocities[-1] > velocities[0]:
                    self.trends.acceleration = "accelerating"
                else:
                    self.trends.acceleration = "stable"

            # Risk trend
            if len(risks) >= 2:
                if risks[-1] < risks[0] - 0.05:
                    self.trends.risk_trend = "improving"
                    self.longitudinal_metrics.risk_trend = "improving"
                elif risks[-1] > risks[0] + 0.05:
                    self.trends.risk_trend = "worsening"
                    self.longitudinal_metrics.risk_trend = "worsening"
                else:
                    self.trends.risk_trend = "stable"
                    self.longitudinal_metrics.risk_trend = "stable"

        # Detect anomalies
        self._detect_anomalies()
        
    def _detect_anomalies(self):
        """Detect anomalous changes in wound progression."""
        # Sudden area increase
        for i, change in enumerate(self.longitudinal_metrics.area_changes):
            if change > 20:  # More than 20% increase
                self.trends.anomalies_detected.append({
                    'type': 'sudden_deterioration',
                    'timepoint': i + 1,
                    'value': change,
                    'metric': 'area_change'
                })
                
        # Prolonged stagnation
        if len(self.longitudinal_metrics.area_changes) >= 3:
            recent_changes = self.longitudinal_metrics.area_changes[-3:]
            if all(abs(c) < 5 for c in recent_changes):  # Less than 5% change
                self.trends.anomalies_detected.append({
                    'type': 'stagnation',
                    'timepoint': len(self.timepoints) - 1,
                    'value': np.mean(recent_changes),
                    'metric': 'area_change'
                })
                
    def generate_alerts(self):
        """Generate clinical alerts based on analysis."""
        # Deterioration alert
        if self.trends.area_trend == "worsening":
            self.alerts.append(ClinicalAlert(
                severity="critical",
                category="deterioration",
                message="Wound area increasing - intervention required",
                triggered_at_day=self.timepoints[-1].day,
                metrics={
                    'area_change': self.longitudinal_metrics.total_area_change_pct,
                    'current_area': self.timepoints[-1].wound_area
                },
                recommendations=[
                    "Review current treatment protocol",
                    "Consider wound culture",
                    "Evaluate for infection",
                    "Reassess offloading strategy"
                ]
            ))
            
        # Stagnation alert
        if self.trends.healing_trend == "plateauing":
            self.alerts.append(ClinicalAlert(
                severity="warning",
                category="stagnation",
                message="Wound healing has plateaued",
                triggered_at_day=self.timepoints[-1].day,
                metrics={
                    'recent_changes': self.longitudinal_metrics.area_changes[-3:]
                },
                recommendations=[
                    "Consider adjunctive therapies",
                    "Evaluate nutritional status",
                    "Review compliance with treatment"
                ]
            ))
            
        # High risk alert
        if self.longitudinal_metrics.avg_risk > 0.7:
            self.alerts.append(ClinicalAlert(
                severity="critical",
                category="high_risk",
                message="Elevated amputation risk sustained",
                triggered_at_day=self.timepoints[-1].day,
                metrics={
                    'avg_risk': self.longitudinal_metrics.avg_risk,
                    'current_risk': self.longitudinal_metrics.risk_history[-1]
                },
                recommendations=[
                    "Urgent vascular assessment",
                    "Consider specialist referral",
                    "Intensify monitoring frequency"
                ]
            ))
            
    def set_overall_status(self):
        """Determine overall wound status."""
        if not self.timepoints:
            self.overall_status = "unknown"
            return
            
        # Based on trend analysis and recent changes
        if self.trends.healing_trend == "improving":
            if self.longitudinal_metrics.avg_risk < 0.3:
                self.overall_status = "healing_well"
            else:
                self.overall_status = "improving_high_risk"
        elif self.trends.healing_trend == "worsening":
            self.overall_status = "deteriorating"
        else:  # plateauing
            if self.timepoints[-1].wound_area < 2.0:
                self.overall_status = "stable_small"
            else:
                self.overall_status = "stagnant_needs_intervention"
                
    def get_summary(self) -> Dict:
        """Get summary dictionary of analysis."""
        return {
            'wound_id': self.wound_id,
            'timepoints_analyzed': len(self.timepoints),
            'duration_days': self.timepoints[-1].day if self.timepoints else 0,
            'overall_status': self.overall_status,
            'total_area_change_pct': self.longitudinal_metrics.total_area_change_pct,
            'avg_healing_velocity': np.mean(self.longitudinal_metrics.healing_velocity) 
                                    if self.longitudinal_metrics.healing_velocity else 0,
            'healing_trend': self.trends.healing_trend,
            'risk_trend': self.trends.risk_trend,
            'critical_alerts': len([a for a in self.alerts if a.severity == 'critical']),
            'warnings': len([a for a in self.alerts if a.severity == 'warning'])
        }


def analyze_wound_progression(
    sequence_images: List[Dict],
    patient_history: Dict,
    wound_vision,
    wound_score,
    risk_fusion,
    heal_cast,
    care_guide,
    preprocessor=None,
    previous_sequences: Optional[List] = None
) -> WoundSequenceAnalysis:
    """
    Unified pipeline for comprehensive wound progression analysis.
    
    Args:
        sequence_images: List of dicts with keys:
            - 'image_path': str
            - 'day': int  
            - 'notes': str (optional)
        patient_history: Dict with patient clinical data
        wound_vision: WoundVision analyzer instance
        wound_score: WoundScore instance
        risk_fusion: RiskFusion instance
        heal_cast: HealCast instance
        care_guide: CareGuide instance
        preprocessor: Optional image preprocessor
        previous_sequences: Optional historical analysis data
        
    Returns:
        WoundSequenceAnalysis: Complete analysis object
    """
    # Initialize analysis
    wound_id = patient_history.get('patient_id', 'UNKNOWN')
    analysis = WoundSequenceAnalysis(wound_id, patient_history)
    
    # Build previous visit data for HealCast
    previous_visits = []
    
    # Process each timepoint
    for img_data in sequence_images:
        image_path = img_data['image_path']
        day = img_data['day']
        notes = img_data.get('notes', '')
        
        # Preprocess if needed
        processed_path = None
        if preprocessor:
            processed_img = preprocessor.preprocess(image_path)
            processed_path = image_path.replace('.jpg', '_processed.jpg')
            processed_img.save(processed_path)
            analysis_image = processed_path
        else:
            analysis_image = image_path
            
        # 1. WoundVision analysis
        vision_result = wound_vision.analyze(analysis_image)
        
        # Extract wound area
        dims = vision_result.get('dimensions', {})
        wound_area = dims.get('length_cm', 0) * dims.get('width_cm', 0)
        
        # Prepare features for scoring
        scoring_features = {
            'area_cm2': wound_area,
            'necrosis_pct': vision_result.get('tissue_composition', {}).get('eschar_percent', 0),
            'slough_pct': vision_result.get('tissue_composition', {}).get('slough_percent', 0),
            'granulation_pct': vision_result.get('tissue_composition', {}).get('granulation_percent', 0),
            'infection_signs': 'Purulence' if 'purulent' in vision_result.get('exudate', {}).get('type', '').lower() else 'None'
        }
        
        # 2. WoundScore analysis
        push_score = wound_score.calculate_push_score(scoring_features)
        wagner_grade = wound_score.calculate_wagner_grade(scoring_features)
        
        clinical_scores = {
            'push': push_score,
            'wagner': wagner_grade
        }
        
        # 3. RiskFusion analysis
        risk_prob = risk_fusion.assess_risk(patient_history, scoring_features)
        
        # 4. HealCast analysis
        history_areas = [v['area'] for v in previous_visits] + [wound_area]
        history_days = [v['day'] for v in previous_visits] + [day]
        
        days_to_close = heal_cast.predict_closure(history_days, history_areas)
        
        # 5. CareGuide analysis – pass wound-specific metrics for tailored recommendations
        tissue = vision_result.get('tissue_composition', {})
        exudate_info = vision_result.get('exudate', {})
        care_decision = care_guide.determine_action(
            risk_prob,
            push_score,
            days_to_close,
            granulation_pct=float(tissue.get('granulation_percent', tissue.get('granulation', 50))),
            slough_pct=float(tissue.get('slough_percent', tissue.get('slough', 30))),
            exudate=exudate_info.get('amount', 'moderate'),
            wound_area=wound_area,
        )
        
        # Create timepoint analysis
        tp_analysis = TimePointAnalysis(
            day=day,
            image_path=image_path,
            processed_image_path=processed_path,
            notes=notes,
            vision_analysis=vision_result,
            clinical_scores=clinical_scores,
            risk_assessment=risk_prob,
            healing_forecast=days_to_close,
            care_recommendation=care_decision
        )
        
        # Add to sequence
        analysis.add_timepoint(tp_analysis)
        
        # Update previous visits for next iteration
        previous_visits.append({
            'day': day,
            'area': wound_area
        })
    
    # Perform trend analysis
    analysis.analyze_trends()
    
    # Generate alerts
    analysis.generate_alerts()
    
    # Set overall status
    analysis.set_overall_status()
    
    return analysis


# Helper function for generating summary report
def generate_progression_summary(analysis: WoundSequenceAnalysis) -> str:
    """
    Generate human-readable summary of wound progression.
    
    Args:
        analysis: WoundSequenceAnalysis object
        
    Returns:
        str: Formatted summary report
    """
    summary = f"""
WOUND PROGRESSION SUMMARY
========================
Wound ID: {analysis.wound_id}
Patient: {analysis.patient_history.get('patient_id', 'N/A')}
Analysis Period: Day 0 to Day {analysis.timepoints[-1].day if analysis.timepoints else 0}
Timepoints Analyzed: {len(analysis.timepoints)}

OVERALL STATUS: {analysis.overall_status.upper()}

KEY METRICS
-----------
Initial Area: {analysis.timepoints[0].wound_area:.2f} cm²
Current Area: {analysis.timepoints[-1].wound_area:.2f} cm²
Total Change: {analysis.longitudinal_metrics.total_area_change_pct:+.1f}%
Avg Healing Velocity: {np.mean(analysis.longitudinal_metrics.healing_velocity):.2f} cm²/week

CLINICAL SCORES
--------------
PUSH Score: {analysis.timepoints[0].clinical_scores['push']} → {analysis.timepoints[-1].clinical_scores['push']}
Wagner Grade: {analysis.timepoints[0].clinical_scores['wagner']} → {analysis.timepoints[-1].clinical_scores['wagner']}

RISK ASSESSMENT
--------------
Initial Risk: {analysis.longitudinal_metrics.risk_history[0]:.1%}
Current Risk: {analysis.longitudinal_metrics.risk_history[-1]:.1%}
Risk Trend: {analysis.trends.risk_trend.upper()}

TRENDS
------
Healing Trend: {analysis.trends.healing_trend.upper()}
Area Trend: {analysis.trends.area_trend.upper()}
Acceleration: {analysis.trends.acceleration.upper()}

ALERTS ({len(analysis.alerts)})
-------
"""
    
    for i, alert in enumerate(analysis.alerts, 1):
        summary += f"\n{i}. [{alert.severity.upper()}] {alert.category}: {alert.message}"
        if alert.recommendations:
            summary += f"\n   Recommendations: {', '.join(alert.recommendations[:2])}"
    
    if not analysis.alerts:
        summary += "No alerts triggered.\n"
        
    return summary
