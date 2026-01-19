# Listing Genie - Front-End Specification

**Document Version:** 1.0
**Date:** December 20, 2024
**Status:** Draft
**Author:** Sally (UX Expert)
**Reference:** [Project Brief v1.0](./brief.md), [PRD v1.0](./prd.md), [Creative Blueprint v1.0](./creative-blueprint.md)

---

## 1. Design Principles

### 1.1 Core Design Philosophy

Listing Genie is designed for **speed, trust, and simplicity**. Every design decision must serve one of these pillars:

| Principle | Implementation | Why It Matters |
|-----------|---------------|----------------|
| **Mobile-First** | All layouts designed for 375px first, then scaled up | 60%+ of Amazon sellers manage businesses from mobile |
| **Progress Transparency** | Always show users where they are in the process | Reduces anxiety, builds trust during payment |
| **Minimal Friction** | Maximum 3 clicks from landing to payment | Competing against "hire a designer" - must be faster |
| **Professional Trust** | Clean, modern aesthetic with subtle premium touches | Users are paying money - must feel legitimate |
| **Instant Feedback** | Every action has immediate visual response | Reinforces system is working, reduces abandonment |

### 1.2 Design Values

1. **Clarity Over Cleverness** - Use plain language, not marketing speak
2. **Speed Over Features** - Show only what's needed at each step
3. **Trust Over Flash** - Professional and reliable, not trendy
4. **Guidance Over Freedom** - One clear path, minimal decisions
5. **Results Over Process** - Focus on outcome (great images), not how it works

---

## 2. User Flow Overview

### 2.1 Complete User Journey

```
┌──────────────────┐
│  Landing Page    │ <-- Entry point
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  Upload Step     │ <-- Drag-drop or click to upload
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  Form Step       │ <-- Title + 3 features + audience
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  Payment Step    │ <-- Review & Stripe checkout
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  Progress Step   │ <-- Live generation status
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  Gallery View    │ <-- Preview & download
└──────────────────┘
         │
         ├──> Image Preview Modal
         ├──> Individual Downloads
         └──> Bulk ZIP Download
```

### 2.2 Step Progress Indicator

**Visual Design:**
```
[●]────[○]────[○]────[○]────[○]
Upload  Form  Pay  Generate View
```

**States:**
- **Current Step:** Filled circle (●) with bold label
- **Future Steps:** Empty circle (○) with grey label
- **Completed Steps:** Filled circle (●) with checkmark, green accent

**Mobile Behavior:** Condense to icons only on screens <480px

---

## 3. Screen-by-Screen Specifications

### 3.1 Landing Page

**Purpose:** Quickly communicate value and drive users to start generating

**Layout Structure:**

```
┌─────────────────────────────────────┐
│        [Logo]    [How It Works]     │ <-- Header
├─────────────────────────────────────┤
│                                     │
│        Transform Your Product       │ <-- Hero
│       Into 5 Pro Amazon Images      │
│              in Minutes             │
│                                     │
│         [Start Generating →]        │ <-- Primary CTA
│                                     │
│     3-5 days → 5 minutes            │ <-- Value Props
│    $50-200 → $9.99                  │
│     Amazon-Optimized                │
│                                     │
├─────────────────────────────────────┤
│                                     │
│    [Sample Before/After Gallery]    │ <-- Social Proof
│                                     │
├─────────────────────────────────────┤
│                                     │
│   Simple 3-Step Process:            │ <-- Process
│   1. Upload Product Photo           │
│   2. Add Product Details            │
│   3. Get 5 Pro Images               │
│                                     │
└─────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Hero Section** | H1 headline, 2-line subheader, primary CTA button |
| **CTA Button** | Large (min 48px height), high-contrast, sticky on scroll (mobile) |
| **Value Props** | 3 columns on desktop, stacked on mobile, icons + numbers |
| **Before/After** | Image carousel showing transformation (3-5 examples) |
| **Process Steps** | Numbered cards with icons |

**Mobile Adaptations:**
- Hero headline: 32px → 24px
- Stack value props vertically
- Sticky CTA at bottom of screen

**Key States:**
- **Default:** Full hero visible
- **Scroll:** Sticky header with CTA button
- **Mobile:** Bottom sticky CTA bar

---

### 3.2 Upload Step

**Purpose:** Get product photo with clear validation and preview

**Layout:**

```
┌─────────────────────────────────────┐
│  [●]────[○]────[○]────[○]────[○]    │ <-- Progress
│  Upload Product Photo (Step 1 of 5) │
├─────────────────────────────────────┤
│                                     │
│   ┌───────────────────────────┐     │
│   │                           │     │
│   │     📷                    │     │ <-- Upload Zone
│   │                           │     │
│   │  Drag photo here or       │     │
│   │  [Choose File]            │     │
│   │                           │     │
│   │  JPEG or PNG • Max 10MB   │     │
│   │  Min 1000x1000 pixels     │     │
│   └───────────────────────────┘     │
│                                     │
│   OR preview if uploaded:           │
│                                     │
│   ┌───────────────────────────┐     │
│   │  [Uploaded Image Preview] │     │ <-- Preview State
│   │        ✓ Looks good!      │     │
│   │     [Remove] [Continue →] │     │
│   └───────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Upload Zone** | Dashed border, min 300px height, drag-over state, click-to-upload |
| **File Input** | Hidden native input, triggered by zone click or button |
| **Preview** | Max 400px width, centered, with checkmark and actions |
| **Validation Messages** | Inline under upload zone, red for errors, green for success |

**States:**

1. **Empty State**
   - Dashed border upload zone
   - Icon and instructions visible
   - "Choose File" button secondary style

2. **Drag-Over State**
   - Solid border (primary color)
   - Background tint
   - "Drop to upload" message

3. **Uploading State**
   - Progress bar
   - "Uploading... X%" text
   - Disable zone interaction

4. **Preview State**
   - Image displayed
   - Green checkmark
   - Remove and Continue buttons

5. **Error State**
   - Red border on upload zone
   - Clear error message (file too large, wrong format, too small)
   - Retry/clear option

**Validation Rules:**
- File type: JPEG or PNG only
- File size: Max 10MB
- Dimensions: Minimum 1000x1000px
- On failure: Show specific error, allow retry

**Mobile Adaptations:**
- Upload zone: 280px height (smaller)
- Preview: Full width with padding
- Camera access option (use device camera)

---

### 3.3 Form Step

**Purpose:** Collect product information for AI generation

**Layout:**

```
┌─────────────────────────────────────┐
│  [●]────[●]────[○]────[○]────[○]    │ <-- Progress
│  Product Details (Step 2 of 5)      │
├─────────────────────────────────────┤
│                                     │
│  Tell us about your product         │
│                                     │
│  Product Title *                    │
│  ┌─────────────────────────────┐   │
│  │ [                     ]     │   │
│  └─────────────────────────────┘   │
│  0/200 characters                   │
│                                     │
│  Key Feature #1 *                   │
│  ┌─────────────────────────────┐   │
│  │ [                     ]     │   │
│  └─────────────────────────────┘   │
│  0/100 characters                   │
│                                     │
│  Key Feature #2 *                   │
│  ┌─────────────────────────────┐   │
│  │ [                     ]     │   │
│  └─────────────────────────────┘   │
│  0/100 characters                   │
│                                     │
│  Key Feature #3 *                   │
│  ┌─────────────────────────────┐   │
│  │ [                     ]     │   │
│  └─────────────────────────────┘   │
│  0/100 characters                   │
│                                     │
│  Target Audience *                  │
│  ┌─────────────────────────────┐   │
│  │ [                     ]     │   │
│  └─────────────────────────────┘   │
│  0/150 characters                   │
│  Example: "Busy moms seeking..."   │
│                                     │
│         [← Back]  [Continue →]      │
│                                     │
└─────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Form Container** | Max 600px width, centered, white background, subtle shadow |
| **Input Fields** | Full width, 48px height (mobile-friendly), 16px font size |
| **Labels** | Bold, 14px, with asterisk for required |
| **Character Counter** | Right-aligned below input, updates live, turns red near limit |
| **Helper Text** | Grey, italic, below counter (for Target Audience only) |
| **Validation** | On blur and submit, inline error messages |

**States:**

1. **Empty State**
   - Placeholder text in each field
   - Character counter shows 0/limit
   - Continue button disabled

2. **Typing State**
   - Character counter updates live
   - Input border highlights on focus (primary color)

3. **Valid Field**
   - Green checkmark icon appears on right
   - Field border subtle green tint

4. **Invalid Field**
   - Red border
   - Error message below (e.g., "This field is required")
   - No checkmark

5. **Form Complete**
   - All fields have green checkmarks
   - Continue button enabled (primary color)

**Validation Rules:**
- All fields required
- Character limits enforced
- No special validation beyond length
- Validate on blur and before submit

**Mobile Adaptations:**
- Stack all fields vertically (already mobile-first)
- Input fields: 52px height for easier tapping
- Action buttons: Full width on mobile

---

### 3.4 Payment Step

**Purpose:** Review information and complete Stripe checkout

**Layout:**

```
┌─────────────────────────────────────┐
│  [●]────[●]────[●]────[○]────[○]    │ <-- Progress
│  Review & Pay (Step 3 of 5)         │
├─────────────────────────────────────┤
│                                     │
│  Order Summary                      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ [Product Thumbnail]         │   │
│  │                             │   │
│  │ Your Product:               │   │
│  │ "Organic Sleep Gummies..."  │   │
│  │                             │   │
│  │ What You'll Get:            │   │
│  │ ✓ 1 Main Product Image      │   │
│  │ ✓ 2 Infographic Images      │   │
│  │ ✓ 1 Lifestyle Image         │   │
│  │ ✓ 1 Comparison Chart        │   │
│  │ ✓ All Amazon-optimized      │   │
│  │ ✓ High-res (2000x2000px)    │   │
│  │                             │   │
│  │ Total: $9.99                │   │
│  └─────────────────────────────┘   │
│                                     │
│  🔒 Secure payment via Stripe       │
│                                     │
│       [← Edit Details]              │
│       [Pay $9.99 & Generate →]      │
│                                     │
│  💡 Money-back guarantee if         │
│     generation fails                │
│                                     │
└─────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Order Card** | White background, subtle shadow, padding, max 500px width |
| **Product Thumbnail** | Uploaded image, 100px x 100px, rounded corners |
| **Checklist Items** | Green checkmarks, clear list of deliverables |
| **Total Price** | Large, bold font (24px), highlighted |
| **Security Badge** | Lock icon + "Secure payment via Stripe" |
| **Primary CTA** | Full width, green/primary color, min 56px height |
| **Trust Badge** | Money-back guarantee message, subtle, bottom |

**States:**

1. **Review State**
   - All information visible
   - Edit button available
   - Pay button enabled

2. **Processing Payment**
   - Pay button shows spinner
   - "Processing..." text
   - Disable all interactions
   - Redirect to Stripe Checkout

3. **Payment Redirect**
   - Full-screen message "Redirecting to secure checkout..."
   - Spinner animation

**Mobile Adaptations:**
- Product thumbnail: 80px x 80px
- Stack all content vertically
- CTA button sticky at bottom
- Checklist items: Smaller font (14px)

**Security Elements:**
- Lock icon next to "Secure payment"
- Stripe logo/badge
- HTTPS indicator reinforcement
- Clear refund policy

---

### 3.5 Generation Progress Step

**Purpose:** Show live progress while images generate, reduce anxiety

**Layout:**

```
┌─────────────────────────────────────┐
│  [●]────[●]────[●]────[●]────[○]    │ <-- Progress
│  Generating Your Images (Step 4/5)  │
├─────────────────────────────────────┤
│                                     │
│  Creating your listing images...    │
│  This takes 2-3 minutes             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ✓ Main Image                │   │ <-- Completed
│  │   [████████████████]        │   │
│  │                             │   │
│  │ ⏳ Infographic 1             │   │ <-- In Progress
│  │   [████████░░░░░░░░]  60%   │   │
│  │                             │   │
│  │ ○ Infographic 2             │   │ <-- Pending
│  │   [░░░░░░░░░░░░░░░░]        │   │
│  │                             │   │
│  │ ○ Lifestyle Image           │   │ <-- Pending
│  │   [░░░░░░░░░░░░░░░░]        │   │
│  │                             │   │
│  │ ○ Comparison Chart          │   │ <-- Pending
│  │   [░░░░░░░░░░░░░░░░]        │   │
│  └─────────────────────────────┘   │
│                                     │
│  💡 Your images will be ready       │
│     shortly. Don't close this page. │
│                                     │
│  [View Sample Images]               │ <-- Optional distraction
│                                     │
└─────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Progress Container** | White card, centered, max 600px width |
| **Image Item** | Individual row per image type |
| **Status Icon** | Checkmark (✓), spinner (⏳), or empty circle (○) |
| **Progress Bar** | Animated, fills from left to right |
| **Percentage** | Optional, shown only for current image |
| **Time Estimate** | "This takes 2-3 minutes" - set expectations |
| **Warning Message** | "Don't close this page" - prevent abandonment |

**States:**

1. **Pending (○)**
   - Grey text
   - Empty progress bar (light grey background)
   - Empty circle icon

2. **In Progress (⏳)**
   - Bold text
   - Animated progress bar
   - Spinner icon
   - Optional percentage

3. **Complete (✓)**
   - Green checkmark
   - Full progress bar (green)
   - Regular text weight

4. **Error (✗)**
   - Red X icon
   - Error message below
   - Retry option

5. **All Complete**
   - Auto-redirect to gallery view
   - Or "View Images" button appears

**Mobile Adaptations:**
- Progress items: Slightly smaller
- Icons: 20px instead of 24px
- Time estimate: Prominent display

**Error Handling:**
- If single image fails: Show retry button for that image
- If all fail: Show refund message and support contact
- Network error: "Connection lost, retrying..." message

---

### 3.6 Gallery View

**Purpose:** Display all generated images with preview and download options

**Layout:**

```
┌─────────────────────────────────────┐
│  [●]────[●]────[●]────[●]────[●]    │ <-- All Complete!
│  Your Images Are Ready! (Step 5/5)  │
├─────────────────────────────────────┤
│                                     │
│  [Download All as ZIP ↓]            │ <-- Primary Action
│                                     │
│  ┌─────┬─────┬─────┬─────┬─────┐   │
│  │ [1] │ [2] │ [3] │ [4] │ [5] │   │ <-- Image Grid
│  │Main │Info1│Info2│Life │Comp │   │
│  │     │     │     │     │     │   │
│  │ [↓] │ [↓] │ [↓] │ [↓] │ [↓] │   │ <-- Individual Downloads
│  └─────┴─────┴─────┴─────┴─────┘   │
│                                     │
│  💡 These images are optimized      │
│     for Amazon. Upload directly     │
│     to Seller Central.              │
│                                     │
│  [← Generate Another Listing]       │
│                                     │
└─────────────────────────────────────┘
```

**Desktop Layout (>1024px):**
```
┌─────────────────────────────────────────────────────┐
│  Your Images Are Ready!        [Download All ↓]     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Image 1 │  │  Image 2 │  │  Image 3 │          │
│  │   Main   │  │  Info 1  │  │  Info 2  │          │
│  │          │  │          │  │          │          │
│  │   [↓]    │  │   [↓]    │  │   [↓]    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                     │
│  ┌──────────┐  ┌──────────┐                        │
│  │  Image 4 │  │  Image 5 │                        │
│  │Lifestyle │  │Comparison│                        │
│  │          │  │          │                        │
│  │   [↓]    │  │   [↓]    │                        │
│  └──────────┘  └──────────┘                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Success Message** | Large, celebratory heading with success icon |
| **Download All Button** | Primary CTA, top position, green with download icon |
| **Image Grid** | Responsive grid, equal-sized cards |
| **Image Card** | Thumbnail, label, download button, hover effect |
| **Individual Download** | Icon button or text link below each image |
| **Helper Text** | Amazon-specific usage tips |
| **Secondary CTA** | "Generate Another" button, less prominent |

**Image Card States:**

1. **Default**
   - Thumbnail displayed
   - Label below (e.g., "Main Image")
   - Download button visible
   - Subtle border

2. **Hover (Desktop)**
   - Slight scale up (1.02x)
   - Shadow deepens
   - "Click to preview" hint appears
   - Download button highlights

3. **Loading**
   - Skeleton loader
   - Spinner in center
   - Faded background

4. **Click/Tap**
   - Opens preview modal (see 3.7)

**Grid Responsive Behavior:**

- **Mobile (<768px):** 1 column, full width cards
- **Tablet (768-1024px):** 2 columns
- **Desktop (>1024px):** 3 columns, then 2 for last row

**Mobile Adaptations:**
- Download All: Sticky button at top
- Image cards: Full width with horizontal layout (thumbnail + info side-by-side)
- Individual download: Right-aligned icon button

---

### 3.7 Image Preview Modal

**Purpose:** View full-size images before downloading

**Layout:**

```
┌─────────────────────────────────────┐
│  ┌─────────────────────────────┐   │
│  │              [×]             │   │ <-- Close Button
│  │                             │   │
│  │                             │   │
│  │      [Full-Size Image]      │   │ <-- Image Display
│  │                             │   │
│  │                             │   │
│  │                             │   │
│  │   Main Product Image        │   │ <-- Label
│  │                             │   │
│  │   [← Previous] [Next →]     │   │ <-- Navigation
│  │   [Download This Image ↓]   │   │ <-- Action
│  │                             │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
     ↑
  Dark overlay (backdrop)
```

**Component Specifications:**

| Component | Details |
|-----------|---------|
| **Modal Backdrop** | Semi-transparent dark overlay (rgba(0,0,0,0.8)) |
| **Modal Container** | Centered, max 90vw/90vh, white background |
| **Image Display** | Max width/height to fit screen, maintain aspect ratio |
| **Close Button** | Top-right, X icon, min 44x44px tap target |
| **Navigation** | Left/right arrows or buttons, cycle through images |
| **Image Label** | Below image, centered, describes image type |
| **Download Button** | Primary action, below label |

**Interaction Behaviors:**

- **Open:** Click any image in gallery
- **Close:** Click X, press ESC, click outside modal
- **Navigate:** Arrow keys (desktop), swipe (mobile), prev/next buttons
- **Download:** Click download button

**States:**

1. **Opening Animation**
   - Fade in backdrop
   - Scale up modal from 0.9 to 1.0
   - Duration: 200ms

2. **Active**
   - Image fully displayed
   - Navigation enabled
   - Download ready

3. **Loading Next Image**
   - Show spinner briefly
   - Fade transition between images

4. **Closing Animation**
   - Fade out backdrop
   - Scale down modal
   - Duration: 150ms

**Mobile Adaptations:**
- Modal: Full screen on mobile
- Swipe gestures: Left/right to navigate
- Pinch-to-zoom: Enable for detailed view
- Download: Bottom sticky button

**Accessibility:**
- Focus trap within modal
- ESC to close
- Tab navigation through controls
- Screen reader labels

---

## 4. UI Design System

### 4.1 Color Palette

**Primary Colors:**

| Color | Hex | Usage |
|-------|-----|-------|
| **Primary** | #10B981 | CTA buttons, success states, checkmarks |
| **Primary Dark** | #059669 | Button hover states |
| **Primary Light** | #D1FAE5 | Success backgrounds, highlights |

**Neutral Colors:**

| Color | Hex | Usage |
|-------|-----|-------|
| **Grey 900** | #111827 | Headings, primary text |
| **Grey 700** | #374151 | Body text |
| **Grey 500** | #6B7280 | Secondary text, placeholders |
| **Grey 300** | #D1D5DB | Borders, dividers |
| **Grey 100** | #F3F4F6 | Backgrounds, subtle fills |
| **White** | #FFFFFF | Surfaces, cards |

**Semantic Colors:**

| Color | Hex | Usage |
|-------|-----|-------|
| **Error** | #EF4444 | Error messages, invalid states |
| **Warning** | #F59E0B | Warnings, cautions |
| **Info** | #3B82F6 | Informational messages |
| **Success** | #10B981 | Success messages (matches primary) |

**Rationale:**
- Green primary = growth, money, success (appropriate for Amazon sellers)
- Professional grey scale maintains trust
- High contrast for readability
- WCAG AA compliant combinations

### 4.2 Typography

**Font Stack:**
```css
Primary: -apple-system, BlinkMacSystemFont, 'Segoe UI',
         'Roboto', 'Helvetica Neue', Arial, sans-serif
```

**Type Scale:**

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| **H1** | 36px / 2.25rem | Bold (700) | 1.2 | Landing hero |
| **H2** | 30px / 1.875rem | Bold (700) | 1.3 | Page titles |
| **H3** | 24px / 1.5rem | Semibold (600) | 1.4 | Section headers |
| **H4** | 20px / 1.25rem | Semibold (600) | 1.4 | Card titles |
| **Body Large** | 18px / 1.125rem | Regular (400) | 1.6 | Important body text |
| **Body** | 16px / 1rem | Regular (400) | 1.5 | Default body text |
| **Body Small** | 14px / 0.875rem | Regular (400) | 1.5 | Helper text, captions |
| **Button** | 16px / 1rem | Semibold (600) | 1 | Button text |

**Mobile Adjustments:**
- H1: 28px (from 36px)
- H2: 24px (from 30px)
- Body minimum: 16px (never smaller for readability)

### 4.3 Spacing System

**Base Unit:** 4px (0.25rem)

| Token | Value | Usage |
|-------|-------|-------|
| **xs** | 4px | Icon margins, tight spacing |
| **sm** | 8px | Small gaps between elements |
| **md** | 16px | Default spacing between components |
| **lg** | 24px | Section spacing |
| **xl** | 32px | Large section spacing |
| **2xl** | 48px | Major section breaks |
| **3xl** | 64px | Page-level spacing |

**Consistent Application:**
- Card padding: 24px (lg)
- Button padding: 12px vertical, 24px horizontal
- Form field spacing: 16px (md)
- Section spacing: 48px (2xl)

### 4.4 Component Styles

#### Buttons

**Primary Button:**
```
Background: Primary (#10B981)
Text: White
Border: None
Border Radius: 8px
Padding: 12px 24px
Font: 16px, Semibold
Min Height: 48px (mobile: 52px)
Shadow: 0 1px 3px rgba(0,0,0,0.1)

Hover: Background → Primary Dark (#059669)
       Shadow → 0 4px 6px rgba(0,0,0,0.1)

Active: Scale 0.98

Disabled: Background → Grey 300
          Text → Grey 500
          Cursor → not-allowed
```

**Secondary Button:**
```
Background: White
Text: Grey 700
Border: 1px solid Grey 300
Border Radius: 8px
Padding: 12px 24px
Font: 16px, Semibold
Min Height: 48px

Hover: Border → Grey 500
       Background → Grey 100

Active: Scale 0.98
```

**Icon Button:**
```
Background: Transparent
Border: None
Size: 44x44px (min tap target)
Icon: 20px

Hover: Background → Grey 100
```

#### Form Inputs

**Text Input:**
```
Background: White
Border: 1px solid Grey 300
Border Radius: 6px
Padding: 12px 16px
Font: 16px, Regular
Height: 48px (mobile: 52px)

Focus: Border → Primary
       Outline → 2px Primary Light
       Shadow → 0 0 0 3px Primary Light

Error: Border → Error
       Outline → Error Light

Success: Border → Success
         Icon → Checkmark (right side)
```

**Character Counter:**
```
Font: 14px, Regular
Color: Grey 500
Position: Right-aligned below input

Near Limit (>90%): Color → Warning
At Limit (100%): Color → Error
```

#### Cards

**Standard Card:**
```
Background: White
Border: 1px solid Grey 200
Border Radius: 12px
Padding: 24px
Shadow: 0 1px 3px rgba(0,0,0,0.1)

Hover: Shadow → 0 4px 6px rgba(0,0,0,0.1)
```

**Image Card (Gallery):**
```
Background: White
Border: 1px solid Grey 200
Border Radius: 8px
Padding: 12px
Overflow: Hidden

Image Area: Aspect ratio 1:1
Label: 14px, Semibold, centered below image

Hover: Transform scale(1.02)
       Shadow → 0 8px 12px rgba(0,0,0,0.15)
       Cursor → Pointer
```

#### Progress Bar

**Progress Bar:**
```
Container:
  Background: Grey 200
  Height: 8px
  Border Radius: 4px
  Overflow: Hidden

Fill:
  Background: Primary
  Height: 100%
  Transition: width 0.3s ease

  Animated State (indeterminate):
    Background: Linear gradient shimmer
    Animation: Slide left-to-right
```

#### Modal

**Modal Overlay:**
```
Background: rgba(0, 0, 0, 0.75)
Position: Fixed, full screen
Z-index: 1000

Animation In: Fade in 200ms
Animation Out: Fade out 150ms
```

**Modal Container:**
```
Background: White
Border Radius: 16px
Max Width: 90vw
Max Height: 90vh
Padding: 24px
Shadow: 0 20px 25px rgba(0,0,0,0.3)

Animation In: Scale 0.9 → 1.0, Fade in
Animation Out: Scale 1.0 → 0.95, Fade out
```

### 4.5 Icons

**Icon Library:** Use Heroicons (free, MIT license) or Lucide Icons

**Standard Sizes:**
- Small: 16px (inline with text)
- Medium: 20px (buttons, UI elements)
- Large: 24px (feature icons)
- XLarge: 32px (hero sections)

**Common Icons:**
- Upload: Cloud upload icon
- Success: Checkmark in circle
- Error: X in circle
- Progress: Spinner/loading animation
- Download: Download arrow
- Close: X
- Info: Information circle
- Lock: Padlock (security)

**Icon Colors:**
- Default: Inherit text color
- Success: Primary green
- Error: Error red
- Info: Info blue

---

## 5. Responsive Breakpoints

### 5.1 Breakpoint System

| Breakpoint | Width | Target Device | Layout Changes |
|------------|-------|---------------|----------------|
| **xs** | < 480px | Small phones | Single column, stacked elements |
| **sm** | 480px - 767px | Large phones | Single column, larger tap targets |
| **md** | 768px - 1023px | Tablets | 2-column grids, side-by-side elements |
| **lg** | 1024px - 1279px | Laptops | 3-column grids, desktop layout |
| **xl** | ≥ 1280px | Desktop | Max width containers, spacious layout |

### 5.2 Responsive Strategies

**Mobile-First Approach:**
1. Design for 375px width first
2. Progressively enhance for larger screens
3. Never rely on hover states for critical functions
4. Ensure all tap targets ≥ 44x44px

**Grid Behavior:**
- xs/sm: 1 column
- md: 2 columns
- lg/xl: 3 columns (where applicable)

**Typography:**
- xs: 16px body (never smaller)
- sm+: Scale up headings
- lg+: Full type scale

**Navigation:**
- xs/sm: Hamburger menu or minimal nav
- md+: Full horizontal navigation

**Forms:**
- xs/sm: Full-width inputs, stacked labels
- md+: Inline labels where appropriate

**Images:**
- xs/sm: Full-width thumbnails
- md: 2-up grid
- lg: 3-up grid

### 5.3 Platform-Specific Optimizations

**iOS:**
- Safe area insets for notched devices
- Disable bounce scroll where inappropriate
- Use -webkit-overflow-scrolling: touch

**Android:**
- Material Design principles for familiarity
- Ensure back button behavior
- Test on Chrome and Samsung Internet

**Desktop:**
- Hover states for all interactive elements
- Keyboard navigation support
- Max-width containers (1280px) for readability

---

## 6. Key Interaction States

### 6.1 Loading States

**Button Loading:**
```
Replace button text with:
[Spinner] Processing...

Disable button
Maintain button dimensions
Show spinner animation
```

**Page Loading:**
```
Skeleton screens for content
- Grey placeholder blocks
- Shimmer animation
- Maintain layout structure
```

**Image Loading:**
```
Progressive image loading
- Low-res placeholder first
- Blur-up effect
- Final high-res image
```

### 6.2 Error States

**Form Validation:**
```
Field-level:
- Red border on input
- Error icon (X)
- Error message below
- Clear, actionable message

Form-level:
- Summary of errors above form
- Scroll to first error
- Highlight all invalid fields
```

**System Errors:**
```
Toast notification (top-right):
- Red background
- Error icon
- Clear message
- Retry action if applicable
- Auto-dismiss after 5s (or manual close)
```

**Generation Failure:**
```
Full-screen error state:
- Large error icon
- "Something went wrong" heading
- Explanation of what happened
- "You will not be charged" reassurance
- Contact support button
- Try again button
```

### 6.3 Success States

**Form Submission:**
```
Green checkmarks on fields
Success message
Auto-advance to next step
```

**Payment Complete:**
```
Success icon animation
"Payment successful!" message
Redirect to generation progress
```

**Generation Complete:**
```
Celebration micro-animation
"Your images are ready!" message
Immediate display of gallery
```

### 6.4 Empty States

**No Results:**
```
Icon illustration
"No images yet" heading
Helpful message
Primary CTA to start generating
```

---

## 7. Accessibility Requirements

### 7.1 WCAG 2.1 AA Compliance Targets

**Color Contrast:**
- Normal text: Minimum 4.5:1 ratio
- Large text (18px+): Minimum 3:1 ratio
- UI components: Minimum 3:1 ratio

**Keyboard Navigation:**
- All interactive elements focusable via Tab
- Logical tab order (top to bottom, left to right)
- Visible focus indicators (outline)
- Skip to main content link
- Modal focus trapping

**Screen Reader Support:**
- Semantic HTML (heading hierarchy, landmarks)
- ARIA labels for icon buttons
- ARIA live regions for dynamic content
- Alt text for all images
- Form labels properly associated

**Interactive Elements:**
- Minimum tap target: 44x44px
- Adequate spacing between tappable elements (8px minimum)
- No reliance on color alone for information
- Clear error messages

**Forms:**
- Labels visible and associated with inputs
- Error messages announced to screen readers
- Required fields clearly marked
- Autocomplete attributes where appropriate

### 7.2 Accessibility Checklist

**Per Screen:**
- [ ] Heading hierarchy is logical (H1 → H2 → H3)
- [ ] All images have alt text
- [ ] Form inputs have associated labels
- [ ] Focus order makes sense
- [ ] Color contrast meets AA standards
- [ ] Interactive elements have focus styles
- [ ] Error messages are clear and associated with fields
- [ ] Dynamic content updates are announced

**Testing:**
- [ ] Keyboard-only navigation works
- [ ] Screen reader testing (NVDA/JAWS/VoiceOver)
- [ ] Zoom to 200% without horizontal scroll
- [ ] Color blindness simulation passes

---

## 8. Animation & Micro-interactions

### 8.1 Animation Principles

1. **Purpose:** Every animation serves a function (feedback, guidance, delight)
2. **Speed:** Fast enough to feel responsive (150-300ms)
3. **Easing:** Natural motion (ease-out for entrances, ease-in for exits)
4. **Subtlety:** Enhance, don't distract

### 8.2 Key Animations

**Button Press:**
```
Scale: 1.0 → 0.98
Duration: 100ms
Easing: ease-out
```

**Card Hover:**
```
Transform: translateY(0) → translateY(-4px)
Shadow: Subtle → Deeper
Duration: 200ms
Easing: ease-out
```

**Modal Open/Close:**
```
Open:
  Backdrop: opacity 0 → 1 (200ms)
  Container: scale 0.9 → 1.0 (200ms)

Close:
  Backdrop: opacity 1 → 0 (150ms)
  Container: scale 1.0 → 0.95 (150ms)
```

**Progress Bar Fill:**
```
Width: 0% → X%
Duration: 300ms
Easing: ease-out
```

**Success Checkmark:**
```
Scale: 0 → 1.2 → 1.0 (elastic bounce)
Duration: 400ms
Easing: ease-out
```

**Loading Spinner:**
```
Rotation: 0deg → 360deg
Duration: 1000ms
Easing: linear
Loop: Infinite
```

**Page Transitions:**
```
Fade in: opacity 0 → 1 (200ms)
Slide up: translateY(20px) → translateY(0) (300ms)
Stagger children by 50ms
```

### 8.3 Reduced Motion

**Respect `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Replace animations with:
- Instant state changes
- Fade transitions only (no movement)
- Static feedback

---

## 9. Performance Considerations

### 9.1 Image Optimization

**Upload Preview:**
- Resize to max 400px before displaying
- Use progressive JPEG or WebP if supported
- Compress for preview (quality 80)

**Gallery Thumbnails:**
- Generate thumbnails server-side (300x300px)
- Lazy load images below fold
- Use blur-up technique

**Download Images:**
- Full resolution (2000x2000px)
- Optimize file size without quality loss
- Provide both PNG and JPEG options

### 9.2 Loading Strategy

**Critical Path:**
1. HTML structure
2. Critical CSS (inline above-fold styles)
3. Above-fold content
4. JavaScript (defer non-critical)

**Code Splitting:**
- Load only code needed for current step
- Lazy load components for future steps
- Preload next likely step

**Asset Loading:**
- Preconnect to external domains (Stripe, cloud storage)
- Defer off-screen images
- Optimize font loading

### 9.3 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **First Contentful Paint** | < 1.5s | Lighthouse |
| **Largest Contentful Paint** | < 2.5s | Lighthouse |
| **Time to Interactive** | < 3.5s | Lighthouse |
| **Cumulative Layout Shift** | < 0.1 | Lighthouse |

---

## 10. Technical Implementation Notes

### 10.1 Frontend Framework

**Recommended:** React with Vite

**Reasoning:**
- Fast development experience
- Component-based architecture
- Large ecosystem
- Easy integration with FastAPI backend

**Alternative:** Vue.js, Svelte (simpler, lighter)

### 10.2 Component Library

**Recommended:** Headless UI + Tailwind CSS

**Reasoning:**
- Full control over styling
- Accessible out of the box
- Utility-first CSS for rapid development
- Customizable to brand

**Alternative:** Chakra UI, shadcn/ui

### 10.3 Key Libraries

| Library | Purpose |
|---------|---------|
| **React** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS** | Utility-first CSS |
| **Headless UI** | Accessible components |
| **React Hook Form** | Form handling |
| **Axios** | HTTP client |
| **React Router** | Navigation (if multi-page) |
| **Lucide React** | Icon library |

### 10.4 State Management

**Approach:** React Context + useState/useReducer

**State Structure:**
```javascript
{
  currentStep: 1-5,
  productImage: File | null,
  productInfo: {
    title: string,
    features: [string, string, string],
    targetAudience: string
  },
  paymentStatus: 'pending' | 'processing' | 'complete' | 'failed',
  generationStatus: {
    mainImage: 'pending' | 'in_progress' | 'complete' | 'error',
    infographic1: 'pending' | 'in_progress' | 'complete' | 'error',
    infographic2: 'pending' | 'in_progress' | 'complete' | 'error',
    lifestyle: 'pending' | 'in_progress' | 'complete' | 'error',
    comparison: 'pending' | 'in_progress' | 'complete' | 'error'
  },
  generatedImages: {
    mainImage: { url: string, filename: string } | null,
    infographic1: { url: string, filename: string } | null,
    // ... etc
  }
}
```

### 10.5 API Integration

**Endpoints:**
```
POST /api/upload          - Upload product image
POST /api/product-info    - Submit product information
POST /api/create-checkout - Create Stripe checkout session
GET  /api/payment-status  - Verify payment completion
POST /api/generate        - Start image generation
GET  /api/generation-status/:id - Poll generation progress
GET  /api/images/:id      - Retrieve generated images
GET  /api/download/:id    - Download individual image
GET  /api/download-zip/:id - Download all as ZIP
```

**Error Handling:**
- Network errors: Retry with exponential backoff
- Validation errors: Display inline
- Server errors: Show user-friendly message + support contact

---

## 11. Edge Cases & Error Scenarios

### 11.1 Upload Issues

| Scenario | Handling |
|----------|----------|
| File too large (>10MB) | "File must be under 10MB. Try compressing your image." |
| Wrong format | "Please upload a JPEG or PNG image." |
| Image too small | "Image must be at least 1000x1000 pixels for best results." |
| Upload fails | "Upload failed. Please check your connection and try again." |
| Slow upload | Show progress bar, "Uploading... X%" |

### 11.2 Form Validation

| Scenario | Handling |
|----------|----------|
| Empty required field | "This field is required" |
| Exceeds character limit | Prevent typing beyond limit, show red counter |
| Special characters | Allow all characters (no restriction) |
| Emoji in text | Allow (some sellers use emoji in listings) |

### 11.3 Payment Issues

| Scenario | Handling |
|----------|----------|
| Card declined | Redirect to error page, "Payment failed. Please try a different payment method." |
| Session expired | "Your session expired. Please start over." |
| Network error during payment | "Connection lost. Checking payment status..." → Verify with backend |
| User closes Stripe window | "Payment cancelled. Your information is saved. Ready to try again?" |

### 11.4 Generation Issues

| Scenario | Handling |
|----------|----------|
| Single image fails | Show error for that image, retry automatically (max 3 attempts) |
| Multiple images fail | Continue generating others, offer partial download + refund |
| All images fail | Full refund + "We're sorry, generation failed. You have not been charged." |
| Generation takes too long | "This is taking longer than expected. We're still working on it..." |
| API rate limit | Queue request, "High demand right now. Your images will be ready shortly." |

### 11.5 Download Issues

| Scenario | Handling |
|----------|----------|
| Download link expired | "Link expired. Please generate a new listing." |
| Network error during download | Browser's native retry or "Download failed. Try again?" |
| ZIP creation fails | Fall back to individual downloads |
| Large file download on mobile data | Warning: "This download is X MB. Continue on mobile data?" |

---

## 12. Future Enhancements (Post-MVP)

### 12.1 User Accounts

**Features:**
- Login/signup flow
- Generation history dashboard
- Save product information templates
- Download previous generations

**UI Additions:**
- Header: Login/Sign up buttons
- Dashboard: List of past generations
- Profile: Basic account settings

### 12.2 Advanced Customization

**Features:**
- Brand color selection
- Font style preferences
- Template selection per image type
- Re-generate individual images

**UI Additions:**
- Style customization step (between form and payment)
- Image editor for individual images
- Regenerate button per image in gallery

### 12.3 Batch Generation

**Features:**
- Upload CSV with multiple products
- Generate listings in bulk
- Progress tracking for multiple listings

**UI Additions:**
- CSV upload interface
- Batch progress dashboard
- Bulk download options

### 12.4 A+ Content Generation

**Features:**
- Generate 5 additional A+ Content images
- Add-on purchase ($14.99)
- Brand story templates

**UI Additions:**
- Add-on selection during payment
- A+ Content gallery section
- Combined download (listing + A+ images)

---

## 13. Design Deliverables

### 13.1 For Development Handoff

**Required Assets:**
1. ✓ This specification document
2. Wireframes (ASCII - included above)
3. Color palette with hex codes (included)
4. Typography specifications (included)
5. Component specifications (included)
6. Responsive breakpoints (included)
7. Animation specifications (included)

**Optional (Nice to Have):**
- High-fidelity mockups (Figma/Sketch)
- Interactive prototype
- Design system documentation
- Component library (Storybook)

### 13.2 Figma/Design Tool Structure

**Recommended Pages:**
1. **Design System** - Colors, typography, components
2. **Landing Page** - Desktop and mobile variants
3. **Upload Step** - All states (empty, uploading, preview, error)
4. **Form Step** - All states (empty, typing, valid, invalid)
5. **Payment Step** - Review screen
6. **Generation Progress** - Various progress states
7. **Gallery View** - Desktop and mobile
8. **Modal** - Image preview modal
9. **Error States** - Various error scenarios

---

## 14. Success Metrics (UX)

### 14.1 Usability Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Task Completion Rate** | >90% | Users who complete full flow |
| **Time to Complete** | <5 minutes | From landing to download |
| **Error Rate** | <10% | Form validation errors per session |
| **Mobile Completion Rate** | >80% | Mobile users who complete flow |
| **Payment Abandonment** | <20% | Users who reach payment but don't complete |

### 14.2 Satisfaction Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Net Promoter Score** | >50 | Post-generation survey |
| **Customer Satisfaction** | >4.0/5 | Post-generation rating |
| **Ease of Use** | >4.5/5 | "How easy was this to use?" |
| **Image Quality Satisfaction** | >4.0/5 | "Are you satisfied with the images?" |

### 14.3 Behavioral Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Repeat Usage** | >40% | Users who generate 2+ listings in 30 days |
| **Download Rate** | >95% | Users who download at least one image |
| **Bulk Download Rate** | >70% | Users who use "Download All" |
| **Image Preview Rate** | >60% | Users who click to preview images |

---

## 15. Appendix: Wireframe Details

### 15.1 Landing Page (Text Wireframe)

```
╔═══════════════════════════════════════════════╗
║  [Listing Genie Logo]        [How It Works]  ║
╠═══════════════════════════════════════════════╣
║                                               ║
║           Transform Your Product              ║
║          Into 5 Pro Amazon Images             ║
║                 in Minutes                    ║
║                                               ║
║      ┌─────────────────────────────┐          ║
║      │  Start Generating Now →     │          ║
║      └─────────────────────────────┘          ║
║                                               ║
║   ┌─────────┐  ┌─────────┐  ┌─────────┐      ║
║   │ 5 mins  │  │ $9.99   │  │ Amazon  │      ║
║   │ vs 5    │  │ vs      │  │ Optim-  │      ║
║   │ days    │  │ $50-200 │  │ ized    │      ║
║   └─────────┘  └─────────┘  └─────────┘      ║
║                                               ║
╠═══════════════════════════════════════════════╣
║                                               ║
║         See What You'll Get:                  ║
║                                               ║
║   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐   ║
║   │Before │ │After  │ │After  │ │After  │   ║
║   │Photo  │ │Main   │ │Info   │ │Life   │   ║
║   └───────┘ └───────┘ └───────┘ └───────┘   ║
║                                               ║
╠═══════════════════════════════════════════════╣
║                                               ║
║         How It Works:                         ║
║                                               ║
║   ① Upload Photo  →  ② Add Details  →        ║
║   ③ Get 5 Images                              ║
║                                               ║
║        ┌─────────────────────┐                ║
║        │ Get Started Now →   │                ║
║        └─────────────────────┘                ║
║                                               ║
╚═══════════════════════════════════════════════╝
```

### 15.2 Complete Flow (Mini Wireframes)

**Step 1: Upload**
```
[●]──[○]──[○]──[○]──[○]
┌─────────────────┐
│  📷 Drag or     │
│  Click to       │
│  Upload         │
└─────────────────┘
```

**Step 2: Form**
```
[●]──[●]──[○]──[○]──[○]
┌─────────────────┐
│ Title: [___]    │
│ Feature1: [___] │
│ Feature2: [___] │
│ Feature3: [___] │
│ Audience: [___] │
│   [Continue →]  │
└─────────────────┘
```

**Step 3: Payment**
```
[●]──[●]──[●]──[○]──[○]
┌─────────────────┐
│ Order Summary   │
│ ✓ 5 Images      │
│ Total: $9.99    │
│ [Pay & Generate]│
└─────────────────┘
```

**Step 4: Progress**
```
[●]──[●]──[●]──[●]──[○]
┌─────────────────┐
│ ✓ Main          │
│ ⏳ Info1 [60%]  │
│ ○ Info2         │
│ ○ Lifestyle     │
│ ○ Comparison    │
└─────────────────┘
```

**Step 5: Gallery**
```
[●]──[●]──[●]──[●]──[●]
┌─────────────────┐
│ [Download All]  │
│ [1] [2] [3]     │
│ [4] [5]         │
└─────────────────┘
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | Sally (UX Expert) | Initial front-end specification |

---

**Notes for Development:**

1. **Mobile-First Implementation:** Start with 375px mobile layout, then scale up
2. **Component-Based:** Build reusable components (Button, Input, Card, Modal)
3. **Progressive Enhancement:** Core functionality works without JavaScript (forms)
4. **Accessibility:** Test with keyboard navigation and screen readers throughout
5. **Performance:** Optimize images, lazy load, code split by route/step
6. **Browser Testing:** Chrome, Safari, Firefox, Edge (latest 2 versions)
7. **Device Testing:** iPhone (Safari), Android (Chrome), iPad, Desktop

**Priority Implementation Order:**
1. Core flow (upload → form → payment → progress → gallery)
2. Mobile responsive layouts
3. Error handling and validation
4. Accessibility features
5. Animations and micro-interactions
6. Performance optimizations

---

*This specification provides complete front-end guidance for Listing Genie MVP. All screens, states, components, and interactions are defined for efficient development handoff.*
