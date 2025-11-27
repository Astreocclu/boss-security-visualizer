"""
Refine Assets Script (Phase 0)
------------------------------
This script processes raw product images from `media/raw_assets/` and creates high-fidelity
"Digital Twins" in `media/screen_references/master/`.

Workflow:
1. Ingest: Read from media/raw_assets/
2. Upscale/Sharpen: Use Gemini Vision to remove artifacts and sharpen.
3. Normalize: Resize to 2048px height.
4. Save: Write to media/screen_references/master/{filename}.png
"""

import os
import sys
import logging
from PIL import Image
from google import genai
from google.genai import types

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RAW_ASSETS_DIR = "media/raw_assets"
MASTER_REF_DIR = "media/screen_references/master"

def refine_assets():
    """
    Main function to refine assets.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found.")
        return

    client = genai.Client(api_key=api_key)
    model_name = "gemini-3-pro-image-preview" # Using the same model for consistency

    # Ensure directories exist
    os.makedirs(RAW_ASSETS_DIR, exist_ok=True)
    os.makedirs(MASTER_REF_DIR, exist_ok=True)

    # Process each file in raw_assets
    for filename in os.listdir(RAW_ASSETS_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            process_file(client, model_name, filename)

def process_file(client, model_name, filename):
    """
    Process a single file: Upscale -> Resize -> Save.
    """
    try:
        input_path = os.path.join(RAW_ASSETS_DIR, filename)
        logger.info(f"Processing {filename}...")
        
        image = Image.open(input_path)
        
        # Step A: Upscale / Sharpen using Gemini Vision
        # Note: Gemini generates a NEW image based on the prompt. 
        # Ideally we'd use a dedicated upscaler API, but per instructions we use Gemini Vision.
        prompt = "Sharpen this image. Remove JPEG artifacts. Do NOT add new details. Do NOT change the shape of the handle or tracks. Output a high-resolution version."
        
        response = client.models.generate_content(
            model=model_name,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_generation_config=types.ImageGenerationConfig(
                    guidance_scale=60, # Lower guidance to stick closer to source? Or higher? 
                                       # Actually for "restoration" via generation, it's tricky.
                                       # We'll try a balanced approach.
                    person_generation="dont_generate_people"
                )
            )
        )
        
        refined_image = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    from io import BytesIO
                    refined_image = Image.open(BytesIO(part.inline_data.data))
                    break
        
        if not refined_image:
            logger.warning(f"Failed to generate refined image for {filename}. Using original.")
            refined_image = image

        # Step C: Normalize (Resize to 2048px height)
        target_height = 2048
        aspect_ratio = refined_image.width / refined_image.height
        target_width = int(target_height * aspect_ratio)
        
        final_image = refined_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Save as PNG
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(MASTER_REF_DIR, output_filename)
        final_image.save(output_path, "PNG")
        
        logger.info(f"Saved refined asset to {output_path}")

    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    refine_assets()
