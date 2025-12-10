# Boss Security Visualizer - Project Plan

## Overview
All-in-one security screen sales tool: visualize screens on customer homes, generate security audits, create quotes, and accept payments.

## Tech Stack
- **Backend:** Django 4.0, DRF, PostgreSQL, Redis, Celery
- **Frontend:** React 19.1, React Router 7, Zustand, Cypress
- **AI:** Google Gemini (image processing)
- **Services:** Stripe (payments), Monday.com (CRM), AWS S3 (storage), ReportLab (PDFs)

---

## Features & Status

### ✅ Done
- Showroom Visualizer (Before/After toggle, "Magic Flip")
- AI pipeline (cleanse, build, install screens)
- Security Audit (Gemini vulnerability detection)
- PDF generator (5-page structure, mock pricing)

### 🔨 In Progress
- screen-visualizer branch: perfecting visualizer

### 📋 Planned (by branch)
| Branch | Feature | Priority |
|--------|---------|----------|
| feature/price-quote | Real pricing engine | High |
| feature/pdf-generator | Dynamic pricing in PDFs, vulnerability overlay | High |
| feature/audit | Visual vulnerability map on images | Medium |
| feature/payments | Stripe integration | Medium |
| feature/monday-integration | CRM lead push | Low |

---

## Implementation Phases

### Phase 1: Visualizer Enhancements
- [ ] Slider mode (react-compare-image or custom)
- [ ] Heat map simulation (SVG overlay, gradient)
- [ ] Intruder view (shield icons, lock points)
- [ ] Zoom lock (2x max)

### Phase 2: AI Consultant
- [ ] Recommendation engine (consultant.py)
- [ ] Color match from trim analysis
- [ ] Mounting type recommendation
- [ ] Screen density from sun-angle analysis
- [ ] /recommend endpoint
- [ ] "Recommended by AI" badges in wizard

### Phase 3: Commerce
- [ ] Stripe payment intent backend
- [ ] PaymentElement frontend
- [ ] Monday.com service
- [ ] Webhook -> CRM push
- [ ] Real pricing engine (replace $1350 mock)

### Phase 4: Polish
- [ ] Bounding box overlays (heat map, vulnerability map)
- [ ] Zoom lock implementation

---

## Architecture Notes
- AI bounding boxes: Update AuditService prompt to return [ymin, xmin, ymax, xmax] for overlays
- State: React Query + Zustand for async consultant analysis
