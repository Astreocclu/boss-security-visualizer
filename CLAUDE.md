# CLAUDE.md - Project Rules for Claude Code

## Working Style
- When I share a problem, analyze it first and wait for my reply before making changes
- Break large tasks into 3-5 subtasks and confirm the plan before starting
- Ask clarifying questions if requirements are ambiguous
- One feature at a time, fully complete before moving on

## Git Workflow
- Run `git status` and show me the output before any git operations
- Suggest commits but wait for my approval before running them
- Draft PR descriptions but I will create the PR
- Tell me when to commit, don't do it automatically
- Always work on feature branches, never commit directly to master
- One branch per feature (they already exist, use them)

### Branch Structure
```
master (stable)
├── screen-visualizer
├── feature/price-quote
├── feature/pdf-generator
├── feature/audit
├── feature/payments
└── feature/monday-integration
```

## Session Start
1. Read PLAN.md, TODO.md, and SESSION-NOTES.md
2. Check `git status` and `git branch`
3. Tell me where we left off (reference SESSION-NOTES.md)
4. Ask what I want to focus on today
5. Update SESSION-NOTES.md with today's date and branch

## During Session
**Log as you go** - Update SESSION-NOTES.md incrementally:
- After completing a significant task, add it to "What We Did"
- When something breaks, immediately note it in "What's Broken / Blocked"
- When you discover something important, document it
- Don't wait until end of session to update notes

## Session End
1. Remind me to commit if there are uncommitted changes
2. Update TODO.md with progress
3. Finalize SESSION-NOTES.md:
   - Complete "What We Did" list
   - Update "What's Working" / "What's Broken"
   - Fill in "Next Session Should"
   - Move to "Previous Sessions" if starting fresh next time
4. Tell me the next logical task

## Commands

### Backend (Django)
```bash
cd backend
python manage.py runserver        # dev server
python manage.py test             # run tests
python manage.py makemigrations   # create migrations
python manage.py migrate          # apply migrations
celery -A config worker -l info   # celery worker
```

### Frontend (React)
```bash
cd frontend
npm run dev      # dev server
npm run build    # production build
npm run test     # run tests
npx cypress open # E2E tests
```

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
- Use Lucide icons (already installed)

## Tech Stack Reference
- **Backend:** Django 4.0, DRF, PostgreSQL, Redis, Celery
- **Frontend:** React 19.1, React Router 7, Zustand
- **AI:** Google Gemini via google-generativeai
- **PDF:** ReportLab
- **Payments:** Stripe
- **Storage:** AWS S3

## Project-Specific Notes
- AI bounding boxes: AuditService should return [ymin, xmin, ymax, xmax] for overlay features
- Mock pricing currently hardcoded at $1350/window - needs real pricing engine
- Monday.com and Stripe integrations are stubs for now
