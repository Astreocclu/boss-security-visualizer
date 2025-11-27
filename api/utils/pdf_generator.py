import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
from PIL import Image as PILImage

def generate_visualization_pdf(visualization_request):
    """
    Generate a PDF quote for a visualization request.
    
    Args:
        visualization_request: VisualizationRequest instance
        
    Returns:
        io.BytesIO: Buffer containing the PDF
    """
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center
    
    normal_style = styles['Normal']
    
    # --- Page 1: Visuals ---
    
    # 1. Header (Logo)
    # Try to find the logo
    logo_path = os.path.join(settings.BASE_DIR, 'frontend', 'public', 'logo512.png')
    if os.path.exists(logo_path):
        # Resize logo to be smaller, e.g., 2 inches wide
        im = RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        im.hAlign = 'CENTER'
        elements.append(im)
    else:
        elements.append(Paragraph("Boss Security Screens", title_style))
        
    elements.append(Spacer(1, 0.25*inch))
    
    # 2. Before / After Images
    # We want them side by side or top/bottom depending on aspect ratio.
    # Let's do top/bottom for larger view, or side-by-side if they fit.
    # Given requirements say "Large 'Before' vs 'After' comparison images", let's try to make them big.
    
    original_img_path = visualization_request.original_image.path if visualization_request.original_image else None
    
    # Get the latest generated image
    generated_result = visualization_request.results.first()
    generated_img_path = generated_result.generated_image.path if generated_result and generated_result.generated_image else None
    
    if original_img_path and os.path.exists(original_img_path):
        elements.append(Paragraph("Before", title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Resize image to fit page width (approx 7 inches available width)
        # We need to calculate aspect ratio
        try:
            with PILImage.open(original_img_path) as pil_img:
                width, height = pil_img.size
                aspect = height / float(width)
                
            display_width = 6 * inch
            display_height = display_width * aspect
            
            # Cap height if it's too tall
            if display_height > 4 * inch:
                display_height = 4 * inch
                display_width = display_height / aspect
                
            img_before = RLImage(original_img_path, width=display_width, height=display_height)
            img_before.hAlign = 'CENTER'
            elements.append(img_before)
        except Exception as e:
            elements.append(Paragraph(f"Error loading image: {e}", normal_style))
            
    elements.append(Spacer(1, 0.25*inch))

    if generated_img_path and os.path.exists(generated_img_path):
        elements.append(Paragraph("After", title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        try:
            with PILImage.open(generated_img_path) as pil_img:
                width, height = pil_img.size
                aspect = height / float(width)
                
            display_width = 6 * inch
            display_height = display_width * aspect
            
            # Cap height
            if display_height > 4 * inch:
                display_height = 4 * inch
                display_width = display_height / aspect
                
            img_after = RLImage(generated_img_path, width=display_width, height=display_height)
            img_after.hAlign = 'CENTER'
            elements.append(img_after)
        except Exception as e:
            elements.append(Paragraph(f"Error loading image: {e}", normal_style))
            
    elements.append(PageBreak())
    
    # --- Page 2: Specifications & Price ---
    
    # Header again? Or just title
    elements.append(Paragraph("Project Specifications", title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Specifications Table
    # Row 1: System Type
    # Row 2: Mesh Selection
    # Row 3: Frame Color
    
    # Determine System Type label
    system_type = "Unknown"
    if visualization_request.screen_categories:
        # It's a list, join them
        if isinstance(visualization_request.screen_categories, list):
            system_type = ", ".join(visualization_request.screen_categories)
        else:
            system_type = str(visualization_request.screen_categories)
    elif visualization_request.screen_type:
        # Fallback to legacy
        system_type = visualization_request.get_screen_type_display()
        
    # Mesh Selection
    mesh_selection = visualization_request.get_mesh_choice_display()
    
    # Frame Color
    frame_color = visualization_request.get_frame_color_display()
    
    data = [
        ["System Type", system_type],
        ["Mesh Selection", mesh_selection],
        ["Frame Color", frame_color],
    ]
    
    # Table Style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    t = Table(data, colWidths=[2.5*inch, 4.5*inch])
    t.setStyle(table_style)
    elements.append(t)
    
    elements.append(Spacer(1, 1.0*inch))
    
    # Price Section
    # Large Bold Text: "Estimate: Quote Pending"
    price_style = ParagraphStyle(
        'PriceStyle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=1, # Center
        spaceAfter=20,
        textColor=colors.darkblue
    )
    
    elements.append(Paragraph("Estimate: Quote Pending", price_style))
    
    # Subtext: "A Boss Security representative will contact you shortly."
    subtext_style = ParagraphStyle(
        'SubtextStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1, # Center
        textColor=colors.grey
    )
    elements.append(Paragraph("A Boss Security representative will contact you shortly.", subtext_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
