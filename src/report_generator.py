"""
WoundTrack Report Generation Module

Generates comprehensive textual and visual reports for wound progression analysis.
"""

from typing import Dict, List, Optional
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


class WoundProgressionReport:
    """Generate comprehensive reports for wound progression analysis."""
    
    def __init__(self, analysis):
        """
        Initialize report generator.
        
        Args:
            analysis: WoundSequenceAnalysis object
        """
        self.analysis = analysis
        self.generated_at = datetime.now()
        
    def generate_text_report(self, detailed: bool = True) -> str:
        """
        Generate comprehensive text report.
        
        Args:
            detailed: If True, include detailed per-timepoint analysis
            
        Returns:
            str: Formatted text report
        """
        report_lines = []
        
        # Header
        report_lines.extend(self._generate_header())
        
        # Executive Summary
        report_lines.append("\n" + "="*80)
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("="*80)
        report_lines.extend(self._generate_executive_summary())
        
        # Key Metrics
        report_lines.append("\n" + "="*80)
        report_lines.append("KEY METRICS")
        report_lines.append("="*80)
        report_lines.extend(self._generate_key_metrics())
        
        # Clinical Scores
        report_lines.append("\n" + "="*80)
        report_lines.append("CLINICAL ASSESSMENT")
        report_lines.append("="*80)
        report_lines.extend(self._generate_clinical_scores())
        
        # Risk Assessment
        report_lines.append("\n" + "="*80)
        report_lines.append("RISK ASSESSMENT")
        report_lines.append("="*80)
        report_lines.extend(self._generate_risk_assessment())
        
        # Trend Analysis
        report_lines.append("\n" + "="*80)
        report_lines.append("TREND ANALYSIS")
        report_lines.append("="*80)
        report_lines.extend(self._generate_trend_analysis())
        
        # Alerts
        if self.analysis.alerts:
            report_lines.append("\n" + "="*80)
            report_lines.append("CLINICAL ALERTS")
            report_lines.append("="*80)
            report_lines.extend(self._generate_alerts())
        
        # Detailed Timepoint Analysis
        if detailed:
            report_lines.append("\n" + "="*80)
            report_lines.append("DETAILED TIMEPOINT ANALYSIS")
            report_lines.append("="*80)
            report_lines.extend(self._generate_detailed_timepoints())
        
        # Recommendations
        report_lines.append("\n" + "="*80)
        report_lines.append("CLINICAL RECOMMENDATIONS")
        report_lines.append("="*80)
        report_lines.extend(self._generate_recommendations())
        
        # Footer
        report_lines.append("\n" + "="*80)
        report_lines.extend(self._generate_footer())
        
        return "\n".join(report_lines)
    
    def _generate_header(self) -> List[str]:
        """Generate report header."""
        lines = [
            "="*80,
            "WOUNDTRACK LONGITUDINAL ANALYSIS REPORT",
            "="*80,
            f"Wound ID: {self.analysis.wound_id}",
            f"Patient ID: {self.analysis.patient_history.get('patient_id', 'N/A')}",
            f"Report Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Analysis Period: Day 0 to Day {self.analysis.timepoints[-1].day if self.analysis.timepoints else 0}",
            f"Number of Assessments: {len(self.analysis.timepoints)}",
            ""
        ]
        return lines
    
    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary."""
        lines = [
            f"Overall Status: {self.analysis.overall_status.upper().replace('_', ' ')}",
            "",
            self._get_status_interpretation()
        ]
        return lines
    
    def _get_status_interpretation(self) -> str:
        """Get interpretation of overall status."""
        interpretations = {
            'healing_well': "The wound is showing positive healing progress with decreasing area and favorable risk profile.",
            'improving_high_risk': "The wound is improving but the patient maintains elevated amputation risk requiring close monitoring.",
            'deteriorating': "The wound is worsening with increasing area and/or unfavorable tissue changes. Immediate intervention required.",
            'stable_small': "The wound is small and stable. Continue current treatment and monitoring.",
            'stagnant_needs_intervention': "The wound has plateaued without significant improvement. Consider treatment modification."
        }
        return interpretations.get(self.analysis.overall_status, 
                                  "Status assessment requires clinical judgment.")
    
    def _generate_key_metrics(self) -> List[str]:
        """Generate key metrics section."""
        initial_tp = self.analysis.timepoints[0]
        current_tp = self.analysis.timepoints[-1]
        metrics = self.analysis.longitudinal_metrics
        
        lines = [
            "Wound Area:",
            f"  Initial:  {initial_tp.wound_area:.2f} cm²",
            f"  Current:  {current_tp.wound_area:.2f} cm²",
            f"  Change:   {metrics.total_area_change_pct:+.1f}%",
            "",
            "Healing Velocity:",
            f"  Average:  {np.mean(metrics.healing_velocity) if metrics.healing_velocity else 0:.2f} cm²/week",
            f"  Current:  {metrics.healing_velocity[-1] if metrics.healing_velocity else 0:.2f} cm²/week",
            "",
            "Tissue Composition (Current):",
        ]
        
        if current_tp.tissue_composition:
            for tissue, value in current_tp.tissue_composition.items():
                tissue_name = tissue.replace('_percent', '').replace('_', ' ').title()
                lines.append(f"  {tissue_name + ':':20} {value:>3}%")
        
        return lines
    
    def _generate_clinical_scores(self) -> List[str]:
        """Generate clinical scores section."""
        initial_tp = self.analysis.timepoints[0]
        current_tp = self.analysis.timepoints[-1]
        metrics = self.analysis.longitudinal_metrics
        
        lines = [
            "PUSH Score Progression:",
            f"  Initial:  {initial_tp.clinical_scores['push']}",
            f"  Current:  {current_tp.clinical_scores['push']}",
            f"  Trend:    {' → '.join(map(str, metrics.push_score_history))}",
            "",
            "Wagner Grade Progression:",
            f"  Initial:  {initial_tp.clinical_scores['wagner']}",
            f"  Current:  {current_tp.clinical_scores['wagner']}",
            f"  Trend:    {' → '.join(map(str, metrics.wagner_grade_history))}",
        ]
        
        return lines
    
    def _generate_risk_assessment(self) -> List[str]:
        """Generate risk assessment section."""
        metrics = self.analysis.longitudinal_metrics
        
        lines = [
            "Amputation Risk Profile:",
            f"  Initial Risk:  {metrics.risk_history[0]:.1%}",
            f"  Current Risk:  {metrics.risk_history[-1]:.1%}",
            f"  Average Risk:  {metrics.avg_risk:.1%}",
            f"  Risk Trend:    {metrics.risk_trend.upper()}",
            "",
            "Risk Level Interpretation:",
        ]
        
        current_risk = metrics.risk_history[-1]
        if current_risk < 0.3:
            lines.append("  Low risk - Continue standard monitoring")
        elif current_risk < 0.5:
            lines.append("  Moderate risk - Enhanced monitoring recommended")
        elif current_risk < 0.7:
            lines.append("  High risk - Intensive monitoring and intervention required")
        else:
            lines.append("  CRITICAL RISK - Urgent specialist referral indicated")
        
        return lines
    
    def _generate_trend_analysis(self) -> List[str]:
        """Generate trend analysis section."""
        trends = self.analysis.trends
        
        lines = [
            f"Healing Trend:        {trends.healing_trend.upper()}",
            f"Area Trend:           {trends.area_trend.upper()}",
            f"Risk Trend:           {trends.risk_trend.upper()}",
            f"Healing Acceleration: {trends.acceleration.upper()}",
        ]
        
        if trends.anomalies_detected:
            lines.append("")
            lines.append(f"Anomalies Detected: {len(trends.anomalies_detected)}")
            for i, anomaly in enumerate(trends.anomalies_detected, 1):
                lines.append(f"  {i}. {anomaly['type'].replace('_', ' ').title()} "
                           f"at Day {self.analysis.timepoints[anomaly['timepoint']].day}")
        
        return lines
    
    def _generate_alerts(self) -> List[str]:
        """Generate alerts section."""
        lines = []
        
        critical_alerts = [a for a in self.analysis.alerts if a.severity == 'critical']
        warning_alerts = [a for a in self.analysis.alerts if a.severity == 'warning']
        
        if critical_alerts:
            lines.append("CRITICAL ALERTS:")
            for i, alert in enumerate(critical_alerts, 1):
                lines.append(f"\n  {i}. [{alert.category.upper()}]")
                lines.append(f"     {alert.message}")
                lines.append(f"     Triggered: Day {alert.triggered_at_day}")
                if alert.recommendations:
                    lines.append("     Recommendations:")
                    for rec in alert.recommendations[:3]:
                        lines.append(f"       • {rec}")
        
        if warning_alerts:
            lines.append("\nWARNINGS:")
            for i, alert in enumerate(warning_alerts, 1):
                lines.append(f"\n  {i}. [{alert.category.upper()}]")
                lines.append(f"     {alert.message}")
                lines.append(f"     Triggered: Day {alert.triggered_at_day}")
        
        return lines
    
    def _generate_detailed_timepoints(self) -> List[str]:
        """Generate detailed timepoint analysis."""
        lines = []
        
        for i, tp in enumerate(self.analysis.timepoints):
            lines.append(f"\nTimepoint {i+1} - Day {tp.day}")
            lines.append("-" * 40)
            lines.append(f"Image: {tp.image_path}")
            if tp.notes:
                lines.append(f"Notes: {tp.notes}")
            lines.append(f"Wound Area: {tp.wound_area:.2f} cm²")
            
            if i > 0:
                change = self.analysis.longitudinal_metrics.area_changes[i-1]
                lines.append(f"Change from previous: {change:+.1f}%")
            
            lines.append(f"\nClinical Scores:")
            lines.append(f"  PUSH:   {tp.clinical_scores['push']}")
            lines.append(f"  Wagner: {tp.clinical_scores['wagner']}")
            
            lines.append(f"\nRisk Assessment:")
            lines.append(f"  Amputation Risk: {tp.risk_assessment:.1%}")
            
            if tp.healing_forecast:
                lines.append(f"\nHealing Forecast:")
                lines.append(f"  Estimated days to closure: {tp.healing_forecast}")
            
            lines.append(f"\nCare Recommendation:")
            lines.append(f"  Priority: {tp.care_recommendation['priority']}")
            lines.append(f"  Rationale: {tp.care_recommendation['rationale']}")
            
            if tp.tissue_composition:
                lines.append(f"\nTissue Composition:")
                for tissue, value in tp.tissue_composition.items():
                    tissue_name = tissue.replace('_percent', '').replace('_', ' ').title()
                    lines.append(f"  {tissue_name}: {value}%")
        
        return lines
    
    def _generate_recommendations(self) -> List[str]:
        """Generate clinical recommendations."""
        lines = []
        
        # Based on overall status
        if self.analysis.overall_status == 'deteriorating':
            lines.extend([
                "URGENT ACTIONS REQUIRED:",
                "  • Immediate clinical review",
                "  • Wound culture if not recently performed",
                "  • Review and optimize offloading",
                "  • Consider vascular assessment",
                "  • Increase monitoring frequency to weekly or more"
            ])
        elif self.analysis.overall_status == 'stagnant_needs_intervention':
            lines.extend([
                "TREATMENT MODIFICATION RECOMMENDED:",
                "  • Review current treatment protocol effectiveness",
                "  • Consider adjunctive therapies (e.g., NPWT, biologics)",
                "  • Nutritional assessment",
                "  • Patient compliance evaluation",
                "  • Consider multidisciplinary team review"
            ])
        elif self.analysis.overall_status == 'healing_well':
            lines.extend([
                "CONTINUE CURRENT APPROACH:",
                "  • Maintain current treatment protocol",
                "  • Continue scheduled monitoring",
                "  • Reinforce patient education",
                "  • Monitor for any changes in trajectory"
            ])
        
        # Based on alerts
        if any(a.severity == 'critical' for a in self.analysis.alerts):
            lines.append("\n⚠ CRITICAL ALERTS PRESENT - REFER TO ALERTS SECTION")
        
        return lines
    
    def _generate_footer(self) -> List[str]:
        """Generate report footer."""
        lines = [
            "",
            "Report generated by WoundTrack AI System",
            "This report is for clinical decision support. All recommendations should be",
            "reviewed by qualified healthcare professionals in context of complete patient care.",
            "="*80
        ]
        return lines
    
    def save_text_report(self, filename: str, detailed: bool = True):
        """
        Save text report to file.
        
        Args:
            filename: Output filename
            detailed: Include detailed timepoint analysis
        """
        report = self.generate_text_report(detailed=detailed)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def generate_visual_report(self, filename: str = None) -> go.Figure:
        """
        Generate comprehensive visual dashboard.
        
        Args:
            filename: Optional filename to save HTML report
            
        Returns:
            plotly Figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Wound Area Progression',
                'Tissue Composition Evolution',
                'Clinical Scores Trend',
                'Risk Assessment Trajectory',
                'Healing Velocity',
                'Care Priority Timeline'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.12
        )
        
        days = [tp.day for tp in self.analysis.timepoints]
        
        # 1. Wound Area Progression
        areas = self.analysis.longitudinal_metrics.area_progression
        fig.add_trace(
            go.Scatter(
                x=days, y=areas,
                mode='lines+markers',
                name='Wound Area',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=10)
            ),
            row=1, col=1
        )
        
        # 2. Tissue Composition Evolution
        for tissue_type, color in [
            ('granulation_percent', '#2ecc71'),
            ('slough_percent', '#f39c12'),
            ('eschar_percent', '#34495e')
        ]:
            if tissue_type in self.analysis.longitudinal_metrics.tissue_trends:
                values = self.analysis.longitudinal_metrics.tissue_trends[tissue_type]
                tissue_name = tissue_type.replace('_percent', '').title()
                fig.add_trace(
                    go.Scatter(
                        x=days, y=values,
                        mode='lines+markers',
                        name=tissue_name,
                        line=dict(color=color, width=2)
                    ),
                    row=1, col=2
                )
        
        # 3. Clinical Scores Trend
        push_scores = self.analysis.longitudinal_metrics.push_score_history
        wagner_grades = self.analysis.longitudinal_metrics.wagner_grade_history
        
        fig.add_trace(
            go.Scatter(
                x=days, y=push_scores,
                mode='lines+markers',
                name='PUSH Score',
                line=dict(color='#3498db', width=2),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=days, y=wagner_grades,
                mode='lines+markers',
                name='Wagner Grade',
                line=dict(color='#9b59b6', width=2),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        # 4. Risk Assessment Trajectory
        risks = [r * 100 for r in self.analysis.longitudinal_metrics.risk_history]
        risk_colors = ['#2ecc71' if r < 30 else '#f39c12' if r < 70 else '#e74c3c' 
                      for r in risks]
        
        fig.add_trace(
            go.Scatter(
                x=days, y=risks,
                mode='lines+markers',
                name='Amputation Risk',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=12, color=risk_colors),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)'
            ),
            row=2, col=2
        )
        
        # Add risk threshold lines
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Low Risk", row=2, col=2)
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     annotation_text="High Risk", row=2, col=2)
        
        # 5. Healing Velocity
        if self.analysis.longitudinal_metrics.healing_velocity:
            velocity_days = days[1:]  # Velocity calculated from 2nd timepoint
            velocities = self.analysis.longitudinal_metrics.healing_velocity
            
            colors = ['#2ecc71' if v < 0 else '#e74c3c' for v in velocities]
            
            fig.add_trace(
                go.Bar(
                    x=velocity_days,
                    y=velocities,
                    name='Healing Rate',
                    marker_color=colors
                ),
                row=3, col=1
            )
        
        # 6. Care Priority Timeline
        priority_map = {'Routine': 1, 'Escalate': 2, 'Urgent': 3}
        priorities = [
            priority_map.get(tp.care_recommendation.get('priority', 'Routine'), 1)
            for tp in self.analysis.timepoints
        ]
        
        priority_colors = ['#2ecc71' if p == 1 else '#f39c12' if p == 2 else '#e74c3c' 
                          for p in priorities]
        
        fig.add_trace(
            go.Scatter(
                x=days, y=priorities,
                mode='lines+markers',
                name='Care Priority',
                line=dict(color='#95a5a6', width=2),
                marker=dict(size=15, color=priority_colors)
            ),
            row=3, col=2
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Days", row=3, col=1)
        fig.update_xaxes(title_text="Days", row=3, col=2)
        fig.update_yaxes(title_text="Area (cm²)", row=1, col=1)
        fig.update_yaxes(title_text="Percentage (%)", row=1, col=2)
        fig.update_yaxes(title_text="Score", row=2, col=1)
        fig.update_yaxes(title_text="Risk (%)", row=2, col=2)
        fig.update_yaxes(title_text="cm²/week", row=3, col=1)
        fig.update_yaxes(title_text="Priority Level", row=3, col=2,
                        ticktext=['Routine', 'Escalate', 'Urgent'],
                        tickvals=[1, 2, 3])
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"WoundTrack Longitudinal Analysis - {self.analysis.wound_id}<br>" +
                     f"<sub>Overall Status: {self.analysis.overall_status.replace('_', ' ').title()}</sub>",
                x=0.5,
                xanchor='center'
            ),
            showlegend=True,
            height=1200,
            template='plotly_white',
            font=dict(size=10)
        )
        
        if filename:
            fig.write_html(filename)
        
        return fig
    
    def generate_summary_card(self) -> go.Figure:
        """
        Generate a summary card visual.
        
        Returns:
            plotly Figure object
        """
        summary = self.analysis.get_summary()
        
        # Create indicator figures
        fig = make_subplots(
            rows=2, cols=3,
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]
            ],
            subplot_titles=(
                'Total Area Change',
                'Avg Healing Velocity',
                'Current Risk',
                'PUSH Score Change',
                'Critical Alerts',
                'Analysis Duration'
            )
        )
        
        # Area change indicator
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=self.analysis.timepoints[-1].wound_area,
                delta={'reference': self.analysis.timepoints[0].wound_area,
                      'relative': True, 'valueformat': '.1%'},
                number={'suffix': " cm²"},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=1
        )
        
        # Healing velocity
        avg_velocity = summary['avg_healing_velocity']
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=avg_velocity,
                number={'suffix': " cm²/wk", 'valueformat': '.2f'},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=2
        )
        
        # Current risk
        current_risk = self.analysis.longitudinal_metrics.risk_history[-1] * 100
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=current_risk,
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                },
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=3
        )
        
        # PUSH score change
        push_change = (self.analysis.timepoints[-1].clinical_scores['push'] - 
                      self.analysis.timepoints[0].clinical_scores['push'])
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=self.analysis.timepoints[-1].clinical_scores['push'],
                delta={'reference': self.analysis.timepoints[0].clinical_scores['push']},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=1
        )
        
        # Critical alerts
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=summary['critical_alerts'],
                number={'font': {'color': 'red' if summary['critical_alerts'] > 0 else 'green'}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=2
        )
        
        # Duration
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=summary['duration_days'],
                number={'suffix': " days"},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=2, col=3
        )
        
        fig.update_layout(
            title=f"WoundTrack Summary - {self.analysis.wound_id}",
            height=600,
            template='plotly_white'
        )
        
        return fig


def generate_comprehensive_report(
    analysis,
    output_dir: str = ".",
    include_detailed: bool = True
) -> Dict[str, str]:
    """
    Generate both textual and visual reports.
    
    Args:
        analysis: WoundSequenceAnalysis object
        output_dir: Output directory for reports
        include_detailed: Include detailed timepoint analysis in text report
        
    Returns:
        dict: Paths to generated files
    """
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    report_generator = WoundProgressionReport(analysis)
    
    # Generate filenames
    base_name = f"{analysis.wound_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    text_file = os.path.join(output_dir, f"{base_name}_report.txt")
    visual_file = os.path.join(output_dir, f"{base_name}_dashboard.html")
    summary_file = os.path.join(output_dir, f"{base_name}_summary.html")
    
    # Generate reports
    report_generator.save_text_report(text_file, detailed=include_detailed)
    report_generator.generate_visual_report(visual_file)
    
    summary_fig = report_generator.generate_summary_card()
    summary_fig.write_html(summary_file)
    
    return {
        'text_report': text_file,
        'visual_dashboard': visual_file,
        'summary_card': summary_file
    }
