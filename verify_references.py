import os
import sys
import django
from PIL import Image

# Setup Django environment
sys.path.append('/home/reid/projects/homescreen')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homescreen_project.settings')
django.setup()

from api.ai_services.screen_visualizer import ScreenVisualizer

def verify_references():
    print("Verifying ScreenVisualizer reference loading...")
    
    # Create dummy files for testing
    base_path = "/home/reid/projects/homescreen/media/screen_references/lifestyle_environmental"
    os.makedirs(os.path.join(base_path, "80", "master"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "95", "master"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "99", "master"), exist_ok=True)
    
    # Create dummy images
    Image.new('RGB', (100, 100), color='red').save(os.path.join(base_path, "80", "master", "ref_80.jpg"))
    Image.new('RGB', (100, 100), color='green').save(os.path.join(base_path, "95", "master", "ref_95.jpg"))
    Image.new('RGB', (100, 100), color='blue').save(os.path.join(base_path, "99", "master", "ref_99.jpg"))
    
    # Initialize visualizer (mocking API key to avoid error)
    os.environ["GOOGLE_API_KEY"] = "mock_key"
    visualizer = ScreenVisualizer()
    
    refs = visualizer.reference_images
    print(f"Loaded references keys: {list(refs.keys())}")
    
    if '80' in refs and '95' in refs and '99' in refs:
        print("SUCCESS: All opacity references loaded correctly.")
    else:
        print("FAILURE: Missing references.")
        
    # Clean up dummy files
    os.remove(os.path.join(base_path, "80", "master", "ref_80.jpg"))
    os.remove(os.path.join(base_path, "95", "master", "ref_95.jpg"))
    os.remove(os.path.join(base_path, "99", "master", "ref_99.jpg"))

if __name__ == "__main__":
    verify_references()
