import os
import sys
import django
from django.core.files import File

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homescreen_project.settings')
django.setup()

from api.models import VisualizationRequest, GeneratedImage
from django.contrib.auth.models import User
from api.utils.pdf_generator import generate_visualization_pdf

def verify_pdf_generation():
    # Get or create a user
    user, created = User.objects.get_or_create(username='testuser')
    if created:
        user.set_password('testpass')
        user.save()
        print("Created test user.")

    # Get the most recent request or create one
    request = VisualizationRequest.objects.filter(user=user).last()
    
    if not request:
        print("No VisualizationRequest found. Creating a dummy one...")
        # Use logo as dummy image
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'logo512.png')
        
        if not os.path.exists(logo_path):
            print(f"Error: Dummy image not found at {logo_path}")
            return

        request = VisualizationRequest(
            user=user,
            status='complete',
            screen_categories=['Window', 'Door'],
            mesh_choice='12x12',
            frame_color='Black'
        )
        
        with open(logo_path, 'rb') as f:
            request.original_image.save('dummy_original.png', File(f), save=True)
            
        # Create a dummy result
        result = GeneratedImage(request=request)
        with open(logo_path, 'rb') as f:
            result.generated_image.save('dummy_generated.png', File(f), save=True)
        
        print(f"Created dummy request ID: {request.id}")
    
    print(f"Testing PDF generation for Request ID: {request.id}")
    
    try:
        pdf_buffer = generate_visualization_pdf(request)
        
        output_filename = f"test_quote_{request.id}.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
            
        print(f"Successfully generated PDF: {output_filename}")
        print(f"PDF Size: {len(pdf_buffer.getvalue())} bytes")
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_pdf_generation()
