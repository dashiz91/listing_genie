# REDDSTUDIO Backlog

Raw ideas and feature requests. Pick one → refine into `ready/` → implement.

---

## UI/UX

### Homepage Simplification
Make home page look like reference: `C:\Users\Rober\Downloads\Screenshot 2026-02-04 194511.jpg`
Minimal settings visible, advanced sleek button to open all forms. Only show preview after first generation so it looks sleek. Use shadcn components.

### Loading Animation Improvement
Improve the loading of generations. Research unique loading bars from genius brands/products for inspiration.

---

## Auth/Onboarding

### Supabase Email Branding
Email registration looks bad - sends to random localhost URL. Make it come from our domain, not theirs. Currently looks generic.

---

## New Features

### ASIN Import (One-Click Generation)
Streamline form generation with ASIN input option. Our AI scrapes Amazon for title, description, target audience, and other requirements + 2 images. Then regenerate in 1 click.

### Monetary Tiers Revision
Change free tier: only 10 credits per email ever (no daily reset). Concern about exploiters making multiple emails - consider phone verification requirement?

---

## AI/Prompts

### Editorial Reference Strategy Rework
Current problem: AI takes editorial references too literally and shows them as actual text in images instead of using them for style/quality guidance.

**Fix needed:** Rework prompt strategy to use editorial references as quality cues:
- Brand names (for quality association)
- Technical photography terms (expensive cameras, studio lighting)
- High-end production keywords
- Style direction without literal text

The reference should inform visual quality, not become visible copy. Keep actual copywriting separate from quality/style modifiers.

---

## Completed (reference)

- Profile Dropdown (001) - profile icon with menu, credit usage display
- Out of Credits Modal (002) - modal popup when insufficient credits, upgrade path
- A+ Preview Integration (003) - unified Desktop/Mobile toggle, module labels on hover, unified panel styling
