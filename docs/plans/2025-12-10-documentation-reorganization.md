# Documentation Reorganization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update and reorganize all documentation to reflect current codebase state after major refactoring.

**Architecture:** Fix inaccurate CLAUDE.md entries, archive stale docs while preserving SESSION-NOTES.md as active, create documentation index for discoverability.

**Tech Stack:** Markdown, Git, Bash (file operations only - no code changes)

---

## Task 1: Create Archive Directory Structure

**Files:**
- Create: `docs/archive/`
- Create: `docs/archive/logs/`
- Create: `docs/archive/investigations/`

**Step 1: Create archive directories**

```bash
mkdir -p docs/archive/logs docs/archive/investigations
```

**Step 2: Verify directories exist**

Run: `ls -la docs/archive/`
Expected: `logs` and `investigations` subdirectories listed

**Step 3: Commit**

```bash
git add docs/archive/
git commit -m "chore: create docs/archive structure for stale documentation"
```

---

## Task 2: Archive Debug Logs

**Files:**
- Move: `chat-export-2025-12-02.md` → `docs/archive/logs/`
- Move: `DEBUG-ResultDetailPage-BlankScreen.md` → `docs/archive/logs/`
- Move: `DEBUG-SESSION-2025-12-02-FULL.md` → `docs/archive/logs/`
- Move: `DEBUG-SESSION-2025-12-02.md` → `docs/archive/logs/`

**Step 1: Move debug/chat files to archive**

```bash
mv chat-export-2025-12-02.md docs/archive/logs/
mv DEBUG-ResultDetailPage-BlankScreen.md docs/archive/logs/
mv DEBUG-SESSION-2025-12-02-FULL.md docs/archive/logs/
mv DEBUG-SESSION-2025-12-02.md docs/archive/logs/
```

**Step 2: Verify files moved**

Run: `ls docs/archive/logs/`
Expected: All 4 files listed

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: archive debug logs and chat exports"
```

---

## Task 3: Archive Investigation Files

**Files:**
- Move: `feature_analysis.md` → `docs/archive/investigations/`
- Move: `potential_bugs.md` → `docs/archive/investigations/`
- Move: `docs/investigations/ANALYSIS-WEATHER-VISUAL.md` → `docs/archive/investigations/`
- Move: `docs/investigations/DIAGNOSTIC-SCOPE-MISMATCH.md` → `docs/archive/investigations/`
- Move: `docs/investigations/DIAGNOSTIC-WEATHER-CHANGE.md` → `docs/archive/investigations/`

**Step 1: Check which files exist**

```bash
ls -la feature_analysis.md potential_bugs.md docs/investigations/*.md 2>/dev/null || echo "Some files may not exist"
```

**Step 2: Move existing investigation files**

```bash
# Move root-level analysis files (if they exist)
[ -f feature_analysis.md ] && mv feature_analysis.md docs/archive/investigations/
[ -f potential_bugs.md ] && mv potential_bugs.md docs/archive/investigations/

# Move investigation directory files (if they exist)
[ -f docs/investigations/ANALYSIS-WEATHER-VISUAL.md ] && mv docs/investigations/ANALYSIS-WEATHER-VISUAL.md docs/archive/investigations/
[ -f docs/investigations/DIAGNOSTIC-SCOPE-MISMATCH.md ] && mv docs/investigations/DIAGNOSTIC-SCOPE-MISMATCH.md docs/archive/investigations/
[ -f docs/investigations/DIAGNOSTIC-WEATHER-CHANGE.md ] && mv docs/investigations/DIAGNOSTIC-WEATHER-CHANGE.md docs/archive/investigations/
```

**Step 3: Verify files moved**

Run: `ls docs/archive/investigations/`
Expected: Moved investigation files listed

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: archive completed investigation files"
```

---

## Task 4: Archive Old Planning Docs (NOT SESSION-NOTES.md)

**Files:**
- Move: `PLAN.md` → `docs/plans/PLAN-archived-20251210.md`
- Move: `TODO.md` → `docs/plans/TODO-archived-20251210.md`
- **KEEP IN PLACE:** `SESSION-NOTES.md` (active - used by /save command)

**Step 1: Move PLAN.md with archived prefix**

```bash
[ -f PLAN.md ] && mv PLAN.md docs/plans/PLAN-archived-20251210.md
```

**Step 2: Move TODO.md with archived prefix**

```bash
[ -f TODO.md ] && mv TODO.md docs/plans/TODO-archived-20251210.md
```

**Step 3: Verify SESSION-NOTES.md still in root**

Run: `ls -la SESSION-NOTES.md`
Expected: File exists in project root (NOT moved)

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: archive PLAN.md and TODO.md, keep SESSION-NOTES.md active"
```

---

## Task 5: Fix CLAUDE.md - Django Version

**Files:**
- Modify: `CLAUDE.md:77`

**Step 1: Identify the incorrect line**

Current (line 77):
```markdown
- **Backend:** Django 5.2, DRF, SQLite (dev), PostgreSQL (prod)
```

**Step 2: Replace with correct version**

Replace with:
```markdown
- **Backend:** Django >= 4.0, DRF, SQLite (dev), PostgreSQL (prod)
```

**Step 3: Verify change**

Run: `grep "Backend:" CLAUDE.md`
Expected: `- **Backend:** Django >= 4.0, DRF, SQLite (dev), PostgreSQL (prod)`

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "fix(docs): correct Django version in CLAUDE.md (5.2 -> >= 4.0)"
```

---

## Task 6: Fix CLAUDE.md - Frontend Command

**Files:**
- Modify: `CLAUDE.md:35`

**Step 1: Identify the incorrect line**

Current (line 35):
```markdown
npm run dev      # dev server
```

**Step 2: Replace with correct command**

Replace with:
```markdown
npm start        # dev server
```

**Step 3: Verify change**

Run: `grep "npm start" CLAUDE.md`
Expected: `npm start        # dev server`

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "fix(docs): correct frontend dev command (npm run dev -> npm start)"
```

---

## Task 7: Fix CLAUDE.md - Session Start Instructions

**Files:**
- Modify: `CLAUDE.md:55-58`

**Step 1: Identify the outdated section**

Current (lines 55-58):
```markdown
1. **Use Gemini** to read PLAN.md, TODO.md, and SESSION-NOTES.md (3+ files = delegate to Gemini)
   ```bash
   gemini -p "Read PLAN.md, TODO.md, and SESSION-NOTES.md. Summarize: current status, what's broken, and next steps."
   ```
```

**Step 2: Replace with updated docs**

Replace with:
```markdown
1. **Use Gemini** to read FEATURE-STATUS.md and WHITE-LABEL-PLAN.md (active project docs)
   ```bash
   gemini -p "Read FEATURE-STATUS.md and WHITE-LABEL-PLAN.md. Summarize: current status, what's broken, and next steps."
   ```
```

**Step 3: Verify change**

Run: `grep "FEATURE-STATUS" CLAUDE.md`
Expected: References to FEATURE-STATUS.md appear

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "fix(docs): update Session Start to reference current docs"
```

---

## Task 8: Fix CLAUDE.md - Gemini Delegation Section

**Files:**
- Modify: `CLAUDE.md:98`

**Step 1: Identify the outdated line**

Current (line 98):
```markdown
- **Session startup** - Reading project docs (PLAN.md, TODO.md, SESSION-NOTES.md)
```

**Step 2: Replace with updated docs**

Replace with:
```markdown
- **Session startup** - Reading project docs (FEATURE-STATUS.md, WHITE-LABEL-PLAN.md)
```

**Step 3: Verify change**

Run: `grep "Session startup" CLAUDE.md`
Expected: References FEATURE-STATUS.md and WHITE-LABEL-PLAN.md

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "fix(docs): update Gemini delegation docs reference"
```

---

## Task 9: Create Documentation Index

**Files:**
- Create: `docs/README.md`

**Step 1: Create the index file**

```markdown
# Documentation Index

## Active Documentation

| Document | Purpose |
|----------|---------|
| [FEATURE-STATUS.md](../FEATURE-STATUS.md) | Current feature status and roadmap |
| [WHITE-LABEL-PLAN.md](../WHITE-LABEL-PLAN.md) | White-label/multi-tenant implementation plan |
| [SESSION-NOTES.md](../SESSION-NOTES.md) | Living session handoff notes (updated by /save) |
| [TENANT_ARCHITECTURE_V2.md](./TENANT_ARCHITECTURE_V2.md) | Current tenant/white-label architecture |

## Implementation Plans

| Plan | Status |
|------|--------|
| [2025-12-10-white-label-docs-tests.md](./plans/2025-12-10-white-label-docs-tests.md) | Active |
| [2025-12-10-documentation-reorganization.md](./plans/2025-12-10-documentation-reorganization.md) | Active |

## Archived Documentation

Old/completed documentation moved to `docs/archive/`:
- `archive/logs/` - Debug sessions and chat exports
- `archive/investigations/` - Completed investigations
- `plans/PLAN-archived-*.md` - Superseded planning docs
- `plans/TODO-archived-*.md` - Superseded todo lists

## Technical Reference

| Document | Purpose |
|----------|---------|
| [TECHNICAL-DOCUMENTATION.md](./TECHNICAL-DOCUMENTATION.md) | API and technical reference |
| [AI_SERVICES_*.md](.) | AI service documentation |
```

**Step 2: Write the file**

Save to: `docs/README.md`

**Step 3: Verify file created**

Run: `head -20 docs/README.md`
Expected: Documentation index header visible

**Step 4: Commit**

```bash
git add docs/README.md
git commit -m "docs: create documentation index"
```

---

## Task 10: Create Archive README

**Files:**
- Create: `docs/archive/README.md`

**Step 1: Create archive context file**

```markdown
# Archived Documentation

This directory contains documentation that is no longer actively maintained but preserved for historical reference.

## Contents

- `logs/` - Debug session logs, chat exports
- `investigations/` - Completed bug investigations and analyses

## Why Archived?

These files were archived during the December 2025 documentation reorganization because:
1. They reference outdated file structures (homescreen_project → visualizer_project)
2. Issues they investigate have been resolved
3. They've been superseded by newer documentation

## Still Need Something?

Check the active docs in the parent `docs/` directory or `docs/README.md` for the current documentation index.
```

**Step 2: Write the file**

Save to: `docs/archive/README.md`

**Step 3: Verify file created**

Run: `cat docs/archive/README.md`
Expected: Archive context content visible

**Step 4: Commit**

```bash
git add docs/archive/README.md
git commit -m "docs: add archive README with context"
```

---

## Task 11: Final Verification

**Step 1: Verify CLAUDE.md has all fixes**

```bash
grep -E "(Django >= 4.0|npm start|FEATURE-STATUS)" CLAUDE.md
```

Expected: All 3 patterns found

**Step 2: Verify SESSION-NOTES.md still in root**

```bash
ls -la SESSION-NOTES.md
```

Expected: File exists in project root

**Step 3: Verify archive structure**

```bash
find docs/archive -type f -name "*.md" | head -10
```

Expected: Archived files listed

**Step 4: Verify docs index exists**

```bash
ls -la docs/README.md
```

Expected: File exists

**Step 5: Run git status**

```bash
git status
```

Expected: Clean working tree (all changes committed)

---

## Summary

After completing all tasks:

- **CLAUDE.md** updated with correct Django version, npm command, and doc references
- **SESSION-NOTES.md** preserved in root (active for /save command)
- **docs/archive/** contains all stale logs and investigations
- **docs/plans/** contains archived PLAN.md and TODO.md
- **docs/README.md** provides documentation index
- All changes committed in logical, atomic commits
