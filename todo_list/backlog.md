# REDDSTUDIO Backlog

Raw ideas and feature requests. Pick one → refine into `ready/` → implement.

---

## UI/UX

(No pending items)

---

## Auth/Onboarding

(No pending items)

---

## New Features

- **Push to Amazon Seller Central (011)** — SP-API integration to push listing images (7) and A+ Content modules (6) directly to live Amazon listings. OAuth seller auth, S3 temporary hosting, Listings Items API + A+ Content API. Phase 1 = listing images, Phase 2 = A+ Content. **Blocked by:** SP-API app approval (prod_nebula submitted with "Product Listing" role). Story in `ready/011-seller-central-push.md`
  - **Frontend UI complete**: Settings page Amazon Connection card (connect/disconnect via OAuth), ResultsView "Push to Amazon" button with ASIN/SKU form + job status polling, API client types + methods for 5 endpoints
  - **Backend in progress**: Amazon auth service, push service, SP-API client (parallel reviewer)
  - **Pending**: End-to-end test once backend endpoints are deployed to staging

---

## AI/Prompts

(No pending items)

---

## Completed (reference)

- A+ Prompt System Rebuild - rewrote VISUAL_SCRIPT_PROMPT with detailed archetype guidance matching listing quality, replaced per-module and hero pair prompt delivery with single comprehensive prompt, updated TypeScript types for new script structure with role/layout/text fields
- Profile Dropdown (001) - profile icon with menu, credit usage display
- Out of Credits Modal (002) - modal popup when insufficient credits, upgrade path
- A+ Preview Integration (003) - unified Desktop/Mobile toggle, module labels on hover, unified panel styling
- Loading Animation Improvement - enhanced visual effects during generation
- Pre-generated Style Library - 11 styles in 6 categories, vertical strip previews, auto-fills form
- Supabase Email Branding - Resend SMTP, branded templates, noreply@reddstudio.ai on staging+prod
- Monetary Tiers Revision - Free = 10 credits lifetime
- Alt text generation for images - backend API
- ASIN Import - auto-fill form from Amazon product page
- Homepage Simplification (010) - KREA.ai-inspired clean interface replacing split-screen layout
- Generation Loading UX overhaul: polling bug fix, progress bar, batched generation (2 at a time), celebration overlay, upload PIL fallback
- Bug fixes: Feature field VARCHAR(100→500), mobile responsive sidebar, PIL upload fix
- Premium A+ Content Quality Overhaul - text rendering enabled, module design archetypes (hero_brand, exploded_detail, trust_authority, lifestyle_action, dramatic_mono), cinematic hero lighting, brand logo included in A+ refs, safe zone rules
- 3-color maximum enforcement - framework JSON schemas from 5→3, frontend brand color limits, number-of-colors buttons [2,3] only, truncation safety nets in all code paths
- A+ module aspect ratio fix - 16:9→21:9 to match 1464x600 target (2.44:1), eliminated edge cropping of text/content
- Premium Loading System - unified Spinner component (4 sizes), WorkflowStepper horizontal pipeline indicator, narrative GenerationLoader (image-type-specific labels), per-image named pipeline in progress bar, amber→slate/redd theme in AplusSection, gradient shimmer skeletons, CSS keyframe cleanup, ~35 files touched
