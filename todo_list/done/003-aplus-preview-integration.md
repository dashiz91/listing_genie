# 003: A+ Preview Integration

**Priority:** High
**Complexity:** Medium
**Status:** COMPLETE (tested on staging 2026-02-05)

---

## What
Integrate A+ Content modules into the main listing preview as a continuous, Amazon-like experience. Unify the Desktop/Mobile toggle to switch both listing images and A+ content together.

## Why
Current UX has A+ modules separate from listing preview with visible headers (hero, lifestyle, etc). Real Amazon pages show A+ as continuous content below the listing. Users need to see what their actual Amazon page will look like.

## Acceptance Criteria
- [x] Single Desktop/Mobile toggle switches BOTH listing images AND A+ content
- [x] A+ mobile view shows mobile-sized modules when in Mobile mode
- [x] Remove visible A+ module type headers (hero, full_image, etc.)
- [x] Module type/actions appear on hover only (via ImageActionOverlay with label prop)
- [x] Seamless visual transition - looks like real Amazon "From the manufacturer" section
- [x] A+ edit/regenerate panels match listing panel style (Sheet component, dark theme)
- [x] Tested on staging

## Technical Notes
- Lifted viewport state to `ShowroomPanel` as single source of truth (`unifiedViewportMode`)
- `AmazonListingPreview` now accepts controlled `deviceMode` + `onDeviceModeChange` props
- `AplusSection` toggle removed (shows indicator only when controlled externally)
- Added `label` prop to `ImageActionOverlay` for module labels on hover
- Replaced custom slide-up overlays with shadcn Sheet component for A+ edit/regen panels
- Matched dark theme styling (`bg-slate-900 border-slate-700`) across all panels

## Files Changed
- `frontend/src/components/split-layout/ShowroomPanel.tsx` - unified viewport state
- `frontend/src/components/amazon-preview/AmazonListingPreview.tsx` - controlled deviceMode
- `frontend/src/components/preview-slots/AplusSection.tsx` - removed headers/toggle, unified panel styling
- `frontend/src/components/shared/ImageActionOverlay.tsx` - added label prop

## Out of Scope
- A+ module reordering (future)
- A+ comparison table module type
- New A+ layout types
- Moving A+ inside AmazonListingPreview component (visual integration achieved)
