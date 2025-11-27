# Homescreen Project

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud API Key (for Gemini)

### Running the Application
The application is designed to be served via Django on port 8000.

1. **Build the Frontend**:
   ```bash
   cd frontend
   npm run build:prod
   cd ..
   ```

2. **Collect Static Files**:
   ```bash
   python3 manage.py collectstatic --noinput
   ```

3. **Start the Server**:
   ```bash
   python3 manage.py runserver
   ```

4. **Access the App**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.

> [!NOTE]
> **Current Workflow Status**:
> We are currently testing a single screen type: **Lifestyle/Environmental**.
> - **Supported Opacities**: 80%, 95%, 99%
> - **Future**: Colors, Internal/External, and additional screen types will be added in subsequent phases.

## Project Structure
- `api/`: Django backend
- `frontend/`: React frontend
- `media/`: User uploads and generated images
- `media/screen_references/`: Reference images for AI generation

## Development
To run tests:
```bash
make test
```
