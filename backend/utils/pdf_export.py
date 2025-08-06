#!/usr/bin/env python3
"""
PDF Export Utility for Poker Strategy Development System
Generates comprehensive strategy reports in PDF format.
"""

import os
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from gui_models import StrategyData


class StrategyPDFExporter:
    """Exports poker strategy data to comprehensive PDF reports."""
    
    def __init__(self, strategy_data: StrategyData):
        self.strategy_data = strategy_data
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkred
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14
        )
        
        # Code/monospace style
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            spaceAfter=4
        )
    
    def export_strategy_report(self, output_path: str) -> bool:
        """Export a comprehensive strategy report to PDF."""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Title page
            story.extend(self._create_title_page())
            
            # Strategy overview
            story.extend(self._create_strategy_overview())
            
            # Hand strength tiers
            story.extend(self._create_hand_strength_section())
            
            # Postflop strategy
            story.extend(self._create_postflop_strategy_section())
            
            # Decision tables
            story.extend(self._create_decision_tables_section())
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            return False
    
    def _create_title_page(self) -> List[Paragraph]:
        """Create the title page."""
        story = []
        
        # Main title
        title = Paragraph("POKER STRATEGY DEVELOPMENT SYSTEM", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle = Paragraph("Comprehensive Strategy Report", self.section_style)
        story.append(subtitle)
        story.append(Spacer(1, 0.3*inch))
        
        # Generation info
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        strategy_file = self.strategy_data.current_strategy_file or "New Strategy"
        
        info_text = f"""
        <b>Generated:</b> {current_time}<br/>
        <b>Strategy File:</b> {strategy_file}<br/>
        <b>Total Hands:</b> {sum(len(tier.hands) for tier in self.strategy_data.tiers)}<br/>
        <b>Total Tiers:</b> {len(self.strategy_data.tiers)}
        """
        
        info_para = Paragraph(info_text, self.body_style)
        story.append(info_para)
        story.append(Spacer(1, 0.5*inch))
        
        # Description
        desc_text = """
        This report contains a comprehensive analysis of your poker strategy,
        including hand strength tiers, postflop decision tables, and strategic
        recommendations based on modern poker theory.
        """
        
        desc_para = Paragraph(desc_text, self.body_style)
        story.append(desc_para)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _create_strategy_overview(self) -> List[Paragraph]:
        """Create the strategy overview section."""
        story = []
        
        # Section header
        header = Paragraph("STRATEGY OVERVIEW", self.section_style)
        story.append(header)
        
        # Overview text
        overview_text = f"""
        <b>Strategy Type:</b> Modern PFA/Caller Theory<br/>
        <b>Positions Supported:</b> UTG, MP, CO, BTN<br/>
        <b>Streets Supported:</b> Flop, Turn, River<br/>
        <b>Hand Strength System:</b> 0-100 scale<br/>
        <b>Decision Parameters:</b> Value Threshold, Check Threshold, Bet Sizing
        """
        
        overview_para = Paragraph(overview_text, self.body_style)
        story.append(overview_para)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_hand_strength_section(self) -> List[Paragraph]:
        """Create the hand strength tiers section."""
        story = []
        
        # Section header
        header = Paragraph("HAND STRENGTH TIERS", self.section_style)
        story.append(header)
        
        # Tier information
        for tier in self.strategy_data.tiers:
            # Tier header
            tier_header = Paragraph(f"{tier.name} (HS {tier.min_hs}-{tier.max_hs})", self.subsection_style)
            story.append(tier_header)
            
            # Tier details
            tier_text = f"""
            <b>Hands:</b> {len(tier.hands)} total<br/>
            <b>Range:</b> {', '.join(tier.hands)}<br/>
            <b>Strategy:</b> Standard play for {tier.name} tier
            """
            
            tier_para = Paragraph(tier_text, self.body_style)
            story.append(tier_para)
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_postflop_strategy_section(self) -> List[Paragraph]:
        """Create the postflop strategy section."""
        story = []
        
        # Section header
        header = Paragraph("POSTFLOP STRATEGY", self.section_style)
        story.append(header)
        
        # PFA Strategy
        pfa_header = Paragraph("PFA (Position of Final Action - Aggressor)", self.subsection_style)
        story.append(pfa_header)
        
        pfa_text = """
        • More aggressive betting patterns<br/>
        • Lower thresholds for value betting<br/>
        • Smaller sizing for pot control<br/>
        • Designed for players who initiated the action
        """
        
        pfa_para = Paragraph(pfa_text, self.body_style)
        story.append(pfa_para)
        story.append(Spacer(1, 0.1*inch))
        
        # Caller Strategy
        caller_header = Paragraph("Caller (Passive Player)", self.subsection_style)
        story.append(caller_header)
        
        caller_text = """
        • More defensive play patterns<br/>
        • Higher thresholds for value betting<br/>
        • Larger sizing for value extraction<br/>
        • Designed for players who called preflop
        """
        
        caller_para = Paragraph(caller_text, self.body_style)
        story.append(caller_para)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_decision_tables_section(self) -> List[Paragraph]:
        """Create the decision tables section."""
        story = []
        
        # Section header
        header = Paragraph("DECISION TABLES", self.section_style)
        story.append(header)
        
        postflop_data = self.strategy_data.strategy_dict.get("postflop", {})
        
        for street in ["flop", "turn", "river"]:
            # Street header
            street_header = Paragraph(f"{street.upper()} STRATEGY", self.subsection_style)
            story.append(street_header)
            
            # Create table for this street
            table_data = self._create_decision_table_data(street, postflop_data)
            if table_data:
                # Improved column widths for better fit
                table = Table(table_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Left align first column
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center other columns
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_decision_table_data(self, street: str, postflop_data: Dict) -> List[List[str]]:
        """Create table data for decision tables."""
        table_data = []
        
        # Header row
        header = ["Action/Parameter", "UTG", "MP", "CO", "BTN"]
        table_data.append(header)
        
        # PFA section
        pfa_data = postflop_data.get("pfa", {}).get(street, {})
        if pfa_data:
            # Value Threshold row
            pfa_val_row = ["PFA - Value Thresh"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = pfa_data.get(pos, {}).get("val_thresh", "")
                pfa_val_row.append(str(val))
            table_data.append(pfa_val_row)
            
            # Check Threshold row
            pfa_check_row = ["PFA - Check Thresh"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = pfa_data.get(pos, {}).get("check_thresh", "")
                pfa_check_row.append(str(val))
            table_data.append(pfa_check_row)
            
            # Bet Sizing row
            pfa_sizing_row = ["PFA - Bet Sizing"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = pfa_data.get(pos, {}).get("sizing", "")
                pfa_sizing_row.append(str(val))
            table_data.append(pfa_sizing_row)
        
        # Caller section
        caller_data = postflop_data.get("caller", {}).get(street, {})
        if caller_data:
            # Value Threshold row
            caller_val_row = ["Caller - Value Thresh"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = caller_data.get(pos, {}).get("val_thresh", "")
                caller_val_row.append(str(val))
            table_data.append(caller_val_row)
            
            # Check Threshold row
            caller_check_row = ["Caller - Check Thresh"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = caller_data.get(pos, {}).get("check_thresh", "")
                caller_check_row.append(str(val))
            table_data.append(caller_check_row)
            
            # Bet Sizing row
            caller_sizing_row = ["Caller - Bet Sizing"]
            for pos in ["UTG", "MP", "CO", "BTN"]:
                val = caller_data.get(pos, {}).get("sizing", "")
                caller_sizing_row.append(str(val))
            table_data.append(caller_sizing_row)
        
        return table_data


def export_strategy_to_pdf(strategy_data: StrategyData, output_path: str) -> bool:
    """Convenience function to export strategy to PDF."""
    exporter = StrategyPDFExporter(strategy_data)
    return exporter.export_strategy_report(output_path) 