# White-Label Architecture Plan

## Status: Integration Phase
**Last Updated:** 2025-12-10

---

## Goal
Design a system to make verticals (boss-security-visualizer, pools-visualizer, etc.) easily copyable with client-configurable reference images and product names (white-label SaaS approach).

---

## Implementation Status

### Phase 0: Frontend Proof - COMPLETE
- [x] `DynamicForm.js` component created
- [x] Renders forms from `product_categories` JSON schema
- [x] Domain-agnostic (no hardcoded product references)

### Phase 1: YAML Config System - COMPLETE
- [x] YAML config format defined (`api/tenants/{tenant}/config.yaml`)
- [x] `sync_tenant_config` management command
- [x] `export_tenant_config` management command
- [x] Boss tenant YAML config created
- [x] Pools tenant YAML config created

### Phase 2: Prompt Override System - COMPLETE
- [x] `PromptOverride` model with version history
- [x] `prompt_service.py` - DB override → Code default priority
- [x] Rollback capability

### Phase 3: Pipeline Step Registry - COMPLETE
- [x] `pipeline_registry.py` - Step type → handler mapping
- [x] Handlers: cleanup, insertion, quality_check
- [x] Scope-based step skipping

### Phase 4: Reference Image System - PENDING
- [ ] `ReferenceImage` model with tenant FK
- [ ] Upload endpoint with processing
- [ ] Frontend gallery
- [ ] AI pipeline integration

---

## Remaining Work

### Testing (Priority: High)
- [ ] Tests for `pipeline_registry.py`
- [ ] Tests for `prompt_service.py`
- [ ] Integration test: YAML → API → DynamicForm

### API Integration (Priority: High)
- [ ] Verify `/api/config/` returns `product_categories` schema
- [ ] Update `useTenantConfig.js` if needed

### Documentation (Priority: Medium)
- [x] `docs/TENANT_ARCHITECTURE_V2.md` - New architecture docs
- [ ] Deprecation notices on old docs

### Tech Debt (Priority: Low)
- `frontend/src/store/visualizationStore.js` - screen refs
- `api/ai_services/utils/prompt_utils.py` - screen refs
- `frontend/src/components/Upload/MeshSelector.js` - should rename

---

## Architecture Decision: Hybrid Config Pattern

- **YAML files in Git** = Source of Truth
- **DB** = Read-only cache (except reference images)
- **Only reference images** are client-mutable in DB
- **Prompts** use "override" pattern: code default + optional DB override

See `docs/TENANT_ARCHITECTURE_V2.md` for full architecture documentation.
