# Product Specification: Homescreen Visualizer

## 1. Product Overview
The Homescreen Visualizer is an AI-powered application that allows users to upload a photo of their home and realistically visualize different types of motorized screens (Solar, Insect, Security) installed on their windows and patios.

## 2. Core User Workflow
1.  **Upload**: User uploads a high-quality photo of their home (exterior view).
2.  **Configuration**:
    *   **Screen Type**: User selects the screen mesh type (e.g., "Lifestyle/Environmental").
    *   **Opacity**: User selects opacity level (80%, 95%, 99%).
    *   **Color**: User selects screen color (or system matches reference).
3.  **Processing**: The system processes the image through a multi-stage AI pipeline.
4.  **Result**: User views the "Before" and "After" comparison, along with a quality score.

## 3. "Under the Hood" AI Pipeline
The core value proposition is the high-fidelity AI processing pipeline, which follows a strict 4-step sequence to ensure realism and structural integrity.

### Step 1: The Cleanse (Image Restoration)
*   **Goal**: Prepare the canvas.
*   **Action**: Remove visual clutter (hoses, trash, debris). **Remove people and furniture.** Fix lighting/shadows.
*   **Constraint**: Do NOT change the house structure, camera angle, or canvas size.

### Step 2: Frame the Image (Structural Build-Out)
*   **Goal**: Ensure there is a physical structure to hold the screens.
*   **Action**: The AI analyzes the patio or window openings. If structural elements (like pillars, headers, or beams) are missing or insufficient to support a motorized screen, the AI generates them.
*   **Detail**: New structural elements must match the existing house texture and architecture perfectly.

### Step 3: Install Screens (The "Money Shot")
*   **Goal**: Apply the screen material realistically.
*   **Action**: Apply screen material using reference textures.
*   **Constraint**: **Frame ONLY the outer edges.** Do NOT add internal beams, bars, or dividers.
*   **Details**: Consider physics (screens down, lighting, shadows, transparency), opacity, and color.
*   **Inputs**:
    *   **Reference Texture**: Uses real-world photos of screen mesh (e.g., "Lifestyle/Environmental" at 95% opacity) to ensure texture accuracy.
    *   **Physics**: Screens are rendered "down" (closed), with correct lighting, shadows, and transparency based on the selected opacity.
    *   **Color**: Matches the specified color or reference image.

### Step 4: Quality Check & Rating
*   **Goal**: Verify the output before showing it to the user.
*   **Action**: A separate AI vision pass inspects the image for:
    *   All openings screened?
    *   No hallucinations (floating pillars, unnecessary beams)?
    *   Consistent opacity?
    *   Clean image?
*   **Rating**: The system assigns a **Quality Score (0-100)** based on these criteria.
*   **Retry**: If the score is below a threshold or critical issues are found, the system automatically retries Step 3 with adjusted parameters.

## 4. Technical Requirements
*   **AI Provider**: Google Gemini (Pro Vision / Image models).
*   **Backend**: Django (Python).
*   **Frontend**: React.
*   **Infrastructure**: Dockerized deployment.

## 5. Success Metrics
*   **Realism**: The "After" image should be indistinguishable from a real photo of an installed screen.
*   **Accuracy**: The screen texture and opacity must match the physical product samples.
*   **Speed**: Total pipeline processing time should be optimized for user experience (target < 30s).
