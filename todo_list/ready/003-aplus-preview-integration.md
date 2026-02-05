# 003: A+ Preview Integration

**Priority:** High
**Complexity:** Medium
**Status:** Ready

---

## What
Integrate A+ Content modules into the main listing preview as a continuous, Amazon-like experience. Unify the Desktop/Mobile toggle to switch both listing images and A+ content together.

## Why
Current UX has A+ modules separate from listing preview with visible headers (hero, lifestyle, etc). Real Amazon pages show A+ as continuous content below the listing. Users need to see what their actual Amazon page will look like.

## Acceptance Criteria
- [ ] A+ modules render inside same preview wrapper as listing images (continuous scroll)
- [ ] Remove visible A+ module type headers (hero, full_image, etc.)
- [ ] Module type/actions appear on hover only (like listing image slots)
- [ ] Single Desktop/Mobile toggle switches BOTH listing images AND A+ content
- [ ] A+ mobile view shows mobile-sized modules when in Mobile mode
- [ ] Seamless visual transition - looks like real Amazon "From the manufacturer" section
- [ ] Tested on staging

## Technical Notes
- Currently: `ShowroomPanel` has `AmazonListingPreview` + separate `AplusSection`
- Need to merge or nest A+ inside the Amazon preview wrapper
- Viewport state (`desktop`/`mobile`) should be shared, not separate
- A+ already has `viewportMode` prop - wire it to same toggle as listing
- Module hover overlay similar to `ImageActionOverlay` used for listing slots

## Files Likely Touched
- `frontend/src/components/split-layout/ShowroomPanel.tsx` - layout restructure
- `frontend/src/components/amazon-preview/AmazonListingPreview.tsx` - include A+ section
- `frontend/src/components/preview-slots/AplusSection.tsx` - remove headers, add hover overlay
- `frontend/src/pages/HomePage.tsx` - unify viewport state

## Out of Scope
- A+ module reordering (future)
- A+ comparison table module type
- New A+ layout types
