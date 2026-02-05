# 001: Profile Dropdown Menu

**Priority:** High
**Complexity:** Small
**Status:** Ready

---

## What
Replace the credits button in the sidebar with a profile dropdown that shows user info, quick links, and usage stats.

## Why
Users need quick access to account functions without hunting through settings. The current credits-only widget feels incomplete.

## Acceptance Criteria
- [ ] Profile icon/avatar in sidebar (use initials if no avatar)
- [ ] Click opens dropdown with:
  - User email (truncated if long)
  - "Plans & Pricing" → `/app/settings` (pricing tab)
  - "Settings" → `/app/settings`
  - "Join Community" → Discord link (placeholder URL for now)
  - Divider
  - "Log out" → calls Supabase signOut
- [ ] Shows "X% daily compute used" or credit balance below menu items
- [ ] Dropdown closes when clicking outside
- [ ] Works on mobile (full-width sheet or similar)
- [ ] Tested on staging

## Technical Notes
- Existing: `CreditWidget.tsx` in sidebar - can evolve or replace
- Use shadcn `DropdownMenu` component
- Get user email from `AuthContext`
- Credits info already available from `CreditContext`

## Files Likely Touched
- `frontend/src/components/Layout.tsx` - sidebar structure
- `frontend/src/components/CreditWidget.tsx` - replace or enhance
- `frontend/src/components/ProfileDropdown.tsx` - new component
- `frontend/src/contexts/AuthContext.tsx` - might need user email exposed

## Out of Scope
- Avatar upload (future)
- Discord integration (just link for now)
- Notification badge (future)
