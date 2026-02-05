# 002: Out of Credits Modal

**Priority:** High
**Complexity:** Small
**Status:** COMPLETE (tested on staging 2026-02-05)

---

## What
Show a modal/dialog when user tries to generate but doesn't have enough credits. Currently fails silently.

## Why
Users get confused when generation fails with no feedback. Need clear messaging and path to upgrade.

## Acceptance Criteria
- [x] Modal appears when generation fails due to insufficient credits
- [x] Shows: "You need X credits but have Y"
- [x] Primary CTA: "Upgrade Plan" → /app/settings?tab=billing
- [x] Secondary: "Maybe Later" to dismiss
- [x] Styled consistently with app (shadcn AlertDialog)
- [x] Tested on staging
- [x] Buttons NOT greyed out when out of credits (users can click → see modal)

## Technical Notes
- Backend returns 402 PAYMENT_REQUIRED with "Insufficient credits. Need X, have Y"
- Frontend catches 402 errors in all generation handlers
- OutOfCreditsModal component using shadcn AlertDialog
- Credit-based button disabling removed - let users click to see upgrade path

## Files Changed
- `frontend/src/components/OutOfCreditsModal.tsx` - new component
- `frontend/src/components/ui/alert-dialog.tsx` - shadcn component
- `frontend/src/pages/HomePage.tsx` - error handling in all generation functions
- `frontend/src/components/split-layout/WorkshopPanel.tsx` - removed credit-based disabled logic

## Out of Scope
- Stripe integration (future)
- Free credit offers
- Inline upgrade flow
