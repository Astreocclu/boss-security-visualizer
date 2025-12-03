# Boss Security Visualizer

## What This Is
A Django + React application for visualizing security window screens with AI-powered analysis.

## THIS IS A STANDALONE PROJECT
- Has its own database: db.sqlite3 (local SQLite)
- Has its own venv: ./venv
- Runs on port: 8000
- Does NOT import from other projects

## Location
/home/reid/testhome/boss-security-visualizer/

## Commands
```bash
source venv/bin/activate
python manage.py runserver 8000
```

### Backend (Django)
```bash
python manage.py runserver        # dev server on port 8000
python manage.py test             # run tests
python manage.py makemigrations   # create migrations
python manage.py migrate          # apply migrations
```

### Frontend (React)
```bash
cd frontend
npm run dev      # dev server
npm run build    # production build
npm run test     # run tests
```

---

## Working Style
- When I share a problem, analyze it first and wait for my reply before making changes
- Break large tasks into 3-5 subtasks and confirm the plan before starting
- Ask clarifying questions if requirements are ambiguous
- One feature at a time, fully complete before moving on

## Git Workflow
- Run `git status` and show me the output before any git operations
- Suggest commits but wait for my approval before running them
- Tell me when to commit, don't do it automatically
- Always work on feature branches, never commit directly to master

## Session Start
1. Read PLAN.md, TODO.md, and SESSION-NOTES.md
2. Check `git status` and `git branch`
3. Tell me where we left off
4. Ask what I want to focus on today

## Code Style

### Python/Django
- Use type hints
- Docstrings for public functions
- Keep views thin, logic in services
- Use Django REST Framework serializers

### React
- Functional components with hooks
- Zustand for global state
- Keep components small and focused

## Tech Stack
- **Backend:** Django 5.2, DRF, SQLite (dev), PostgreSQL (prod)
- **Frontend:** React 19.1, React Router 7, Zustand
- **AI:** Google Gemini via google-generativeai
- **PDF:** ReportLab
- **Payments:** Stripe
- **Storage:** AWS S3

## Project-Specific Notes
- AI bounding boxes: AuditService returns [ymin, xmin, ymax, xmax] for overlay features
- Mock pricing currently hardcoded at $1350/window
- ACTIVE_TENANT env var controls tenant (defaults to 'boss')
