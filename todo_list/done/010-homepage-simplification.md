# 010: Homepage Simplification

**Priority:** High
**Complexity:** Large

## What
Redesign the /app generator page from a busy split-screen layout to a clean, minimal KREA.ai-inspired interface. The current page shows all form fields + preview simultaneously. The new design centers on a simple entry point with complexity hidden behind an "Advanced" button.

## Why
Current UI is overwhelming - too many visible fields scares users away. A minimal interface (like KREA.ai reference) feels more approachable and professional. Users should be able to start generating with minimal friction, only expanding advanced options when needed.

## Reference
- Screenshot: `C:\Users\Rober\Downloads\Screenshot 2026-02-04 194511.jpg`
- KREA.ai style: centered prompt area, minimal controls, dark theme, content sections below
- Key principle: hide complexity, show results

## Acceptance Criteria
- [ ] Clean centered entry point (upload photos + title = minimum to start)
- [ ] Advanced settings hidden behind a sleek button/drawer
- [ ] Preview/showroom only appears after first generation (not always visible)
- [ ] All existing functionality preserved (just reorganized)
- [ ] Responsive (mobile-friendly)
- [ ] Uses shadcn components
- [ ] Tested on staging

## Files Likely Touched
- `frontend/src/pages/HomePage.tsx` - Main orchestration (major rework)
- `frontend/src/components/split-layout/WorkshopPanel.tsx` - Form sections
- `frontend/src/components/split-layout/SplitScreenLayout.tsx` - Layout container
- `frontend/src/components/split-layout/ShowroomPanel.tsx` - Preview wrapper
- `frontend/src/components/live-preview/LivePreview.tsx` - Preview states

## Out of Scope
- Landing page changes (only /app route)
- Backend changes
- New features (this is purely a UI reorganization)
