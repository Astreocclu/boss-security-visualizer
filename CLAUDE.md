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

**Note:** Always use `python3` commands over `python` commands.

```bash
source venv/bin/activate
python3 manage.py runserver 8000
```

### Backend (Django)
```bash
python3 manage.py runserver        # dev server on port 8000
python3 manage.py test             # run tests
python3 manage.py makemigrations   # create migrations
python3 manage.py migrate          # apply migrations
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
1. **Use Gemini** to read PLAN.md, TODO.md, and SESSION-NOTES.md (3+ files = delegate to Gemini)
   ```bash
   gemini -p "Read PLAN.md, TODO.md, and SESSION-NOTES.md. Summarize: current status, what's broken, and next steps."
   ```
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

---

## GEMINI CLI DELEGATION

**Pattern:** Claude asks Gemini for advice/commands → Gemini returns text → Claude executes with its own tools.

Gemini is a **consultant**, not an executor. It has 5x context but limited tool access.

### USE GEMINI FOR (text-in, text-out):
- **Session startup** - Reading project docs (PLAN.md, TODO.md, SESSION-NOTES.md)
- **Reading 3+ files** - Always delegate to Gemini when needing to read more than 3 files
- "What files should I look at for X?"
- "What command would do Y?"
- "Analyze this code structure and suggest approach"
- "Critique my plan - what breaks?"

### CLAUDE ALWAYS EXECUTES:
- **Web research** - Claude's WebSearch/WebFetch (Gemini can't do web)
- **Playwright/browser tasks** - Claude runs the actual scraping
- **File operations** - Claude reads/writes/edits
- **Shell commands** - Claude executes what Gemini suggests
- **Code writing** - Claude does the implementation

---

## ITERATIVE BRAINSTORMING

For architecture decisions or complex problem-solving:

1. Claude drafts initial approach
2. Claude pipes to Gemini: `echo "[draft]" | gemini -p "Critique this. What breaks?"`
3. Claude reads critique, revises
4. Repeat until solid

This is NOT for code writing. This is for THINKING through hard problems with a second brain that has 5x context.
