# REDDAI.CO Design System

> **MUST READ** — This document defines the visual identity for the entire REDDAI.CO platform.
> All new UI components must follow these guidelines.

---

## Brand Identity

### The Logo

A geometric fox — clever, sharp, trustworthy. The duality of warm orange and cool slate creates visual tension that draws the eye.

**Logo Files:**
- `public/logo/fox-icon.png` — Transparent fox icon (1024x1024)

### Brand Voice

- Professional but approachable
- Confident, not arrogant
- Clear and direct
- Tech-forward without being cold

---

## Color System

```
┌─────────────────────────────────────────────────────────┐
│  REDDAI.CO COLOR TOKENS                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Primary (Fox Orange)                                   │
│  ┌──────┐                                               │
│  │██████│  redd-500   #C85A35  ← Primary action color   │
│  └──────┘                                               │
│  ┌──────┐                                               │
│  │██████│  redd-600   #A04830  ← Hover state            │
│  └──────┘                                               │
│  ┌──────┐                                               │
│  │██████│  redd-400   #D4795A  ← Lighter accent         │
│  └──────┘                                               │
│                                                         │
│  Neutrals (Slate)                                       │
│  ┌──────┐                                               │
│  │██████│  slate-900  #1A1D21  ← Deep background        │
│  └──────┘                                               │
│  ┌──────┐                                               │
│  │██████│  slate-800  #252A31  ← Card backgrounds       │
│  └──────┘                                               │
│  ┌──────┐                                               │
│  │██████│  slate-600  #4A5568  ← Secondary text         │
│  └──────┘                                               │
│  ┌──────┐                                               │
│  │██████│  slate-100  #F1F5F9  ← Light mode bg          │
│  └──────┘                                               │
│                                                         │
│  Semantic                                               │
│  ┌──────┐                                               │
│  │██████│  white      #FFFFFF  ← Primary text on dark   │
│  └──────┘                                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Tailwind Config

These colors are defined in `frontend/tailwind.config.js`:

```js
colors: {
  redd: {
    400: '#D4795A',  // Lighter accent
    500: '#C85A35',  // Primary (CTAs, highlights)
    600: '#A04830',  // Hover states
  },
  slate: {
    100: '#F1F5F9',  // Light mode background
    600: '#4A5568',  // Secondary/muted text
    800: '#252A31',  // Card backgrounds
    900: '#1A1D21',  // Page background (dark mode)
  },
}
```

### Color Usage Rules

| Element | Color | Tailwind Class |
|---------|-------|----------------|
| Page background | slate-900 | `bg-slate-900` |
| Card background | slate-800 | `bg-slate-800` |
| Primary text | white | `text-white` |
| Secondary text | slate-400 | `text-slate-400` |
| Muted text | slate-500 | `text-slate-500` |
| Primary button | redd-500 | `bg-redd-500 hover:bg-redd-600` |
| Secondary button | slate-800 | `bg-slate-800 hover:bg-slate-700` |
| Borders | slate-700 | `border-slate-700` |
| Focus rings | redd-500 | `ring-redd-500` |
| Links | redd-400 | `text-redd-400 hover:text-redd-500` |
| Accents/badges | redd-500/10 | `bg-redd-500/10 text-redd-400` |

---

## Typography

### Font Family

**Inter** — Clean, modern, highly legible at all sizes.

Loaded via Google Fonts in `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Configured in Tailwind:
```js
fontFamily: {
  sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
}
```

### Type Scale

| Element | Class | Usage |
|---------|-------|-------|
| H1 (Hero) | `text-5xl font-bold tracking-tight` | Landing hero only |
| H2 (Section) | `text-3xl font-semibold` | Section titles |
| H3 (Card) | `text-xl font-medium` | Card titles, subsections |
| Body | `text-base` | Default paragraph text |
| Small | `text-sm` | Captions, helper text |
| Tiny | `text-xs` | Badges, labels |

### Text Colors by Context

```
Dark backgrounds (slate-900, slate-800):
  - Primary text: text-white
  - Secondary text: text-slate-400
  - Muted text: text-slate-500

Light backgrounds (slate-100, white):
  - Primary text: text-slate-900
  - Secondary text: text-slate-600
  - Muted text: text-slate-500
```

---

## Spacing System

Use Tailwind's default spacing scale consistently:

| Use Case | Value | Class |
|----------|-------|-------|
| Section padding (vertical) | 96px | `py-24` |
| Container max width | 1152px | `max-w-6xl` |
| Card padding | 24-32px | `p-6` or `p-8` |
| Grid gaps | 24-32px | `gap-6` or `gap-8` |
| Component spacing | 16px | `space-y-4` or `gap-4` |
| Tight spacing | 8px | `space-y-2` or `gap-2` |

---

## Component Patterns

### Buttons

```tsx
// Primary CTA
<button className="px-6 py-3 bg-redd-500 hover:bg-redd-600 text-white font-medium rounded-lg transition-colors">
  Get Started
</button>

// Secondary
<button className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg border border-slate-700 transition-colors">
  Learn More
</button>

// Ghost
<button className="px-4 py-2 text-slate-300 hover:text-white transition-colors">
  Cancel
</button>
```

### Cards

```tsx
<div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-redd-500/40 transition-colors">
  {/* Card content */}
</div>
```

### Badges

```tsx
<span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-redd-500/10 border border-redd-500/20">
  <span className="w-2 h-2 rounded-full bg-redd-500 animate-pulse"></span>
  <span className="text-redd-400 text-sm font-medium">AI-Powered</span>
</span>
```

### Input Fields

```tsx
<input
  type="text"
  className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-redd-500 focus:border-transparent"
  placeholder="Enter value..."
/>
```

### Icons in Containers

```tsx
<div className="w-10 h-10 rounded-lg bg-redd-500/10 flex items-center justify-center text-redd-500">
  <svg className="w-6 h-6">...</svg>
</div>
```

---

## Layout Patterns

### Container

```tsx
<div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
  {/* Content */}
</div>
```

### Section

```tsx
<section className="py-24 px-4 sm:px-6 lg:px-8">
  <div className="max-w-6xl mx-auto">
    {/* Section content */}
  </div>
</section>
```

### Navbar

```tsx
<nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
  <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex items-center justify-between h-16">
      {/* Nav content */}
    </div>
  </div>
</nav>
```

---

## Effects & Transitions

### Hover States

All interactive elements should have smooth transitions:
```tsx
className="transition-colors"  // For color changes
className="transition-all"     // For multiple properties
```

### Shadows

```tsx
// Card shadow
className="shadow-lg shadow-redd-500/10"

// Elevated card
className="shadow-2xl shadow-redd-500/10"
```

### Gradients

```tsx
// Fade to background (for hero images)
className="bg-gradient-to-t from-slate-900 via-transparent to-transparent"

// Section divider
className="bg-gradient-to-r from-slate-700 via-redd-500/50 to-slate-700"
```

### Glass Effect (Navbar)

```tsx
className="bg-slate-900/80 backdrop-blur-md"
```

---

## Responsive Breakpoints

Follow Tailwind's default breakpoints:

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| (default) | 0px | Mobile-first base styles |
| `sm:` | 640px | Small tablets |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |

### Mobile-First Examples

```tsx
// Stack on mobile, row on tablet+
className="flex flex-col sm:flex-row"

// 1 col on mobile, 2 on tablet, 3 on desktop
className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"

// Hide on mobile, show on desktop
className="hidden md:block"
```

---

## File Structure

```
frontend/
├── public/
│   ├── logo/
│   │   └── fox-icon.png        # Transparent logo
│   └── images/
│       └── hero-mockup.png     # Landing page hero image
│
├── src/
│   ├── components/
│   │   ├── landing/            # Landing page sections
│   │   │   ├── navbar.tsx
│   │   │   ├── hero.tsx
│   │   │   ├── social-proof.tsx
│   │   │   ├── features.tsx
│   │   │   ├── how-it-works.tsx
│   │   │   ├── pricing.tsx
│   │   │   ├── cta-footer.tsx
│   │   │   └── index.ts
│   │   └── ui/                 # Shared UI components (future)
│   │
│   ├── pages/
│   │   ├── LandingPage.tsx     # Marketing landing page
│   │   └── HomePage.tsx        # App dashboard (to be restyled)
│   │
│   └── styles/
│       └── index.css           # Global styles + Tailwind
│
└── tailwind.config.js          # Color tokens, fonts
```

---

## Design Principles

### Do

- Use the redd color sparingly — it's an accent, not a background
- Maintain generous whitespace (padding, margins)
- Keep text readable with proper contrast
- Use transitions on all interactive elements
- Test on mobile widths (375px minimum)

### Don't

- Use more than 2-3 colors per component
- Add decorative elements that don't serve a purpose
- Use light text on light backgrounds
- Skip hover/focus states on buttons and links
- Forget about dark mode — the app IS dark mode

---

## Migration Plan (App Restyling)

When restyling the main app (`/app` route) to match the landing page:

1. **Update Layout.tsx** — Apply dark background, proper container widths
2. **Update forms** — Use new input styles, button styles
3. **Update cards** — Apply glass effect, proper borders
4. **Update colors** — Replace `primary-*` with `redd-*` where appropriate
5. **Add Inter font** — Already loaded, just apply via Tailwind

---

## Quick Reference

```
Background:     bg-slate-900
Cards:          bg-slate-800/50 border border-slate-700 rounded-xl
Text:           text-white (primary), text-slate-400 (secondary)
CTA Button:     bg-redd-500 hover:bg-redd-600 text-white rounded-lg
Accent:         text-redd-500, bg-redd-500/10
Transitions:    transition-colors (always add to interactive elements)
Container:      max-w-6xl mx-auto px-4 sm:px-6 lg:px-8
Section:        py-24
```

---

*Last updated: January 21, 2026*
