import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homescreen_project.settings')
django.setup()

from api.models import VisualizationRequest, ScreenType
from api.serializers import VisualizationRequestCreateSerializer
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

def verify_changes():
    print("Verifying changes...")

    # 1. Check Model Fields
    print("\n1. Checking Model Fields...")
    fields = [f.name for f in VisualizationRequest._meta.get_fields()]
    if 'opacity' in fields and 'color' in fields and 'clean_image' in fields:
        print("✅ 'opacity', 'color', and 'clean_image' fields found in VisualizationRequest model.")
    else:
        print(f"❌ Missing fields in VisualizationRequest model. Found: {fields}")
        return

    # 2. Check Serializer Validation
    print("\n2. Checking Serializer Validation...")
    
    # Create dummy user and screen type
    user, _ = User.objects.get_or_create(username='test_verifier')
    screen_type, _ = ScreenType.objects.update_or_create(
        name='Lifestyle',
        defaults={'is_active': True}
    )
    
    # Create dummy image
    from PIL import Image
    import io
    
    img_io = io.BytesIO()
    Image.new('RGB', (100, 100), color='red').save(img_io, format='JPEG')
    img_io.seek(0)
    
    image = SimpleUploadedFile("test.jpg", img_io.getvalue(), content_type="image/jpeg")
    
    data = {
        'original_image': image,
        'screen_type': screen_type.id,
        'opacity': '95',
        'color': 'Dark Bronze'
    }
    
    serializer = VisualizationRequestCreateSerializer(data=data)
    if serializer.is_valid():
        print("✅ Serializer valid with new fields.")
        # Note: We can't easily save here without mocking the view context or manually handling creation, 
        # but validation passing is the key check for the serializer update.
        print(f"Validated Data: {serializer.validated_data.keys()}")
        if 'opacity' in serializer.validated_data and 'color' in serializer.validated_data:
             print("✅ 'opacity' and 'color' present in validated data.")
        else:
             print("❌ 'opacity' or 'color' missing from validated data.")

    else:
        print(f"❌ Serializer invalid: {serializer.errors}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    verify_changes()
