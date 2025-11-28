import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
from PIL import Image as PILImage

def generate_visualization_pdf(visualization_request):
    """
    Generate a 5-page PDF Quote & Audit Report.
    
    Pages:
    1. The Assessment (Hero)
    2. The Vulnerability Map (Risks)
    3. The Solution (After + Heat Map)
    4. The Investment (Quote)
    5. The Guarantee
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1, # Center
        spaceAfter=20,
        textColor=colors.HexColor('#002147') # Deep Navy
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        alignment=1,
        spaceAfter=10,
        textColor=colors.HexColor('#C04000') # Burnt Orange
    )
    
    body_style = styles['Normal']
    body_style.fontSize = 12
    
    # --- Helper: Logo ---
    def get_logo():
        logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
        if os.path.exists(logo_path):
            return RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        return Paragraph("BOSS SECURITY SCREENS", title_style)

    # --- Page 1: The Assessment ---
    elements.append(get_logo())
    elements.append(Spacer(1, 0.5*inch))
    
    address = "Your Home" # Placeholder, could be from user profile if available
    elements.append(Paragraph(f"Home Security Audit for {address}", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Hero Image (Clean Original)
    if visualization_request.original_image:
        img_path = visualization_request.original_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=6*inch, height=4*inch)
            elements.append(img)
            
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Prepared by Boss Security Screens", subtitle_style))
    elements.append(PageBreak())
    
    # --- Page 2: The Vulnerability Map ---
    elements.append(Paragraph("Security Vulnerability Assessment", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Audit Data
    audit_report = getattr(visualization_request, 'audit_report', None)
    
    if audit_report:
        # Summary
        elements.append(Paragraph("AI Security Analysis:", subtitle_style))
        elements.append(Paragraph(audit_report.analysis_summary, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk List
        risks = []
        if audit_report.has_ground_level_access:
            risks.append("• HIGH RISK: Ground Level Windows Detected")
        if audit_report.has_concealment:
            risks.append("• HIGH RISK: Concealed Entry Points (Landscaping)")
        if audit_report.has_glass_proximity:
            risks.append("• MEDIUM RISK: Glass near Door Locks")
        if audit_report.has_hardware_weakness:
            risks.append("• CRITICAL: Standard Fly Screens Detected (No Protection)")
            
        if risks:
            for risk in risks:
                elements.append(Paragraph(risk, ParagraphStyle('Risk', parent=body_style, textColor=colors.red)))
        else:
            elements.append(Paragraph("No specific high-risk vulnerabilities detected by AI.", body_style))
            
    else:
        elements.append(Paragraph("Audit pending or not available.", body_style))

    # Re-show image with "Red Warning" overlay concept (Textual for now in PDF)
    elements.append(Spacer(1, 0.2*inch))
    if visualization_request.original_image:
        img_path = visualization_request.original_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=5*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Paragraph("Fig 1. Vulnerability Map", ParagraphStyle('Caption', parent=body_style, alignment=1)))

    elements.append(PageBreak())
    
    # --- Page 3: The Solution ---
    elements.append(Paragraph("The Boss Solution", title_style))
    
    # After Image
    generated_result = visualization_request.results.first()
    if generated_result and generated_result.generated_image:
        img_path = generated_result.generated_image.path
        if os.path.exists(img_path):
            img = _get_resized_image(img_path, width=6*inch, height=4*inch)
            elements.append(img)
            elements.append(Paragraph("Protected with Boss Security Screens", subtitle_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Features
    features = [
        ["Feature", "Benefit"],
        ["12x12 Stainless Steel Mesh", "No-Cut, No-Break Protection"],
        ["3-Point Locking System", "Burglar-Proof Security"],
        ["66% Heat Block", "Significant Energy Savings"],
        ["No Exterior Screws", "Tamper-Proof Aesthetics"]
    ]
    
    t = Table(features, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002147')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    
    # --- Page 4: The Investment ---
    elements.append(Paragraph("Your Investment", title_style))
    
    # Itemized List (Mockup logic based on scope)
    scope = visualization_request.scope or {}
    items = [["Item", "Quantity", "Unit Price", "Total"]]
    
    total = 0
    if scope.get('hasWindows'):
        items.append(["Standard Security Window", "3", "$450", "$1,350"])
        total += 1350
    if scope.get('hasDoors'):
        items.append(["Security Door", "1", "$1,200", "$1,200"])
        total += 1200
    if scope.get('hasPatio'):
        items.append(["Patio Enclosure", "1", "$2,500", "$2,500"])
        total += 2500
        
    if total == 0:
        # Default if no scope
        items.append(["Security Screen Package", "1", "TBD", "TBD"])
        
    items.append(["", "", "TOTAL", f"${total:,}"])
    
    t_quote = Table(items, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    t_quote.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(t_quote)
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Financing Available: 0% APR for 12 Months", subtitle_style))
    
    # Buy Now CTA (Visual representation for PDF)
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("To proceed, click 'Buy Now' in the app to place your $500 refundable deposit.", body_style))
    
    elements.append(PageBreak())
    
    # --- Page 5: The Guarantee ---
    elements.append(Paragraph("Our Promise", title_style))
    
    elements.append(Paragraph("The Boss 'No Break-In' Guarantee", subtitle_style))
    elements.append(Paragraph("""
    We are so confident in our product that if a burglar manages to break through our screen, 
    we will replace the screen and pay your insurance deductible up to $3,000.
    """, body_style))
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Next Steps", subtitle_style))
    elements.append(Paragraph("1. Place Deposit", body_style))
    elements.append(Paragraph("2. Schedule Precision Measurement", body_style))
    elements.append(Paragraph("3. Custom Fabrication (2-3 Weeks)", body_style))
    elements.append(Paragraph("4. Professional Installation", body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def _get_resized_image(path, width, height):
    """Helper to load and resize image for ReportLab."""
    try:
        img = RLImage(path, width=width, height=height)
        img.hAlign = 'CENTER'
        return img
    except Exception:
        return Paragraph("[Image Missing]", ParagraphStyle('Error'))
