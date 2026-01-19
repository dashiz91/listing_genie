# Listing Genie - Complete System Flow Analysis

## PART 1: CURRENT STATE (What Actually Happens Today)

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    CURRENT SYSTEM FLOW                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                                     USER INPUTS (Frontend)                                       │  ║
║  ├─────────────────────────────────────────────────────────────────────────────────────────────────┤  ║
║  │                                                                                                  │  ║
║  │   IMAGES                          TEXT DATA                      OPTIONAL PREFERENCES            │  ║
║  │   ══════                          ═════════                      ══════════════════════          │  ║
║  │   [IMG1] Primary Product ───┐     • Product Title                • Primary Color (#hex)          │  ║
║  │   [IMG2] Additional #1  ────┤     • Feature 1                    • Brand Name                    │  ║
║  │   [IMG3] Additional #2  ────┤     • Feature 2                    • Global Note                   │  ║
║  │   [IMG4] Additional #3  ────┤     • Feature 3                                                    │  ║
║  │   [IMG5] Additional #4  ────┘     • Target Audience                                              │  ║
║  │                                                                                                  │  ║
║  │   [LOGO] Brand Logo ────────────────────────────────────────────────────────────────────────────│  ║
║  │   [STYLE] Style Reference ──────────────────────────────────────────────────────────────────────│  ║
║  │                                                                                                  │  ║
║  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 1: FRAMEWORK ANALYSIS                                          ║  ║
║  ║                              POST /api/generate/frameworks/analyze                               ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   WHAT GETS SENT TO VISION AI (Gemini Flash / GPT-4o):                                          ║  ║
║  ║   ─────────────────────────────────────────────────────                                          ║  ║
║  ║                                                                                                  ║  ║
║  ║   ┌─────────────────────┐      ┌──────────────────────────────────────────────────────────────┐ ║  ║
║  ║   │                     │      │                                                              │ ║  ║
║  ║   │   [IMG1] ONLY! ◄────┼──────┤  ⚠️  PROBLEM: Only primary image sent!                       │ ║  ║
║  ║   │   Primary Product   │      │      Additional images [IMG2-5] are IGNORED here             │ ║  ║
║  ║   │                     │      │      AI Designer cannot see multiple angles                   │ ║  ║
║  ║   └─────────────────────┘      │                                                              │ ║  ║
║  ║           +                    └──────────────────────────────────────────────────────────────┘ ║  ║
║  ║   ┌─────────────────────┐      ┌──────────────────────────────────────────────────────────────┐ ║  ║
║  ║   │  TEXT PROMPT:       │      │                                                              │ ║  ║
║  ║   │  ────────────────── │      │  ⚠️  PROBLEM: Primary color is just a "preference"           │ ║  ║
║  ║   │  Product: {title}   │      │      AI treats it as SUGGESTION, may override                │ ║  ║
║  ║   │  Features: {1,2,3}  │      │      No way to say "USE THESE EXACT COLORS"                  │ ║  ║
║  ║   │  Audience: {target} │      │                                                              │ ║  ║
║  ║   │  Brand: {name}      │      └──────────────────────────────────────────────────────────────┘ ║  ║
║  ║   │  Primary Color:     │      ┌──────────────────────────────────────────────────────────────┐ ║  ║
║  ║   │    {hex} ◄──────────┼──────┤  ⚠️  PROBLEM: Style reference image NOT sent here            │ ║  ║
║  ║   │    (as suggestion)  │      │      AI Designer doesn't see the style user wants            │ ║  ║
║  ║   └─────────────────────┘      │      Only used later in image generation                     │ ║  ║
║  ║                                └──────────────────────────────────────────────────────────────┘ ║  ║
║  ║                                                                                                  ║  ║
║  ║   VISION AI OUTPUT:                                                                              ║  ║
║  ║   ─────────────────────                                                                          ║  ║
║  ║   • Product Analysis (what AI sees in the ONE image)                                            ║  ║
║  ║   • 4 Design Frameworks, each with:                                                              ║  ║
║  ║     - Colors (5 hex codes) ◄── AI DECIDES these, may ignore user's primary_color                ║  ║
║  ║     - Typography specs                                                                           ║  ║
║  ║     - Story arc                                                                                  ║  ║
║  ║     - Headlines/copy                                                                             ║  ║
║  ║     - Layout specs                                                                               ║  ║
║  ║   • 4 Preview images generated                                                                   ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                              USER SELECTS A FRAMEWORK                                            │  ║
║  │                              (Picks 1 of 4 preview styles)                                       │  ║
║  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 2: GENERATE FINAL IMAGES                                       ║  ║
║  ║                              POST /api/generate/frameworks/generate                              ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   STEP 2A: VISION AI GENERATES 5 DETAILED PROMPTS                                               ║  ║
║  ║   ─────────────────────────────────────────────────────                                          ║  ║
║  ║                                                                                                  ║  ║
║  ║   Input to Vision AI:                                                                            ║  ║
║  ║   • Selected framework (colors, typography, etc.)                                                ║  ║
║  ║   • Product name, features, audience                                                             ║  ║
║  ║   • NO IMAGES sent! ◄── Vision AI is "blind" in this step                                       ║  ║
║  ║                                                                                                  ║  ║
║  ║   Output: 5 detailed text prompts (~500 words each)                                              ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │ Prompt 1 (MAIN):        "Professional e-commerce photo, pure white background..."       │   ║  ║
║  ║   │ Prompt 2 (INFOGRAPHIC1): "Technical breakdown infographic, callout lines..."            │   ║  ║
║  ║   │ Prompt 3 (INFOGRAPHIC2): "Benefits grid with icons, headline: 'Why Choose Us'..."       │   ║  ║
║  ║   │ Prompt 4 (LIFESTYLE):   "Editorial photo, person using product in modern kitchen..."    │   ║  ║
║  ║   │ Prompt 5 (COMPARISON):  "Package contents flatlay, 'Everything Included' headline..."   │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │ Colors EMBEDDED as text: "Use primary color #2E7D32, accent #FF5722"                    │   ║  ║
║  ║   │ Typography EMBEDDED: "Headline in Montserrat Bold"                                      │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ║   STEP 2B: GEMINI IMAGE GENERATOR CREATES 5 IMAGES                                              ║  ║
║  ║   ─────────────────────────────────────────────────────                                          ║  ║
║  ║                                                                                                  ║  ║
║  ║   For EACH of the 5 images:                                                                      ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   TEXT INPUT (prompt from Vision AI):                                                   │   ║  ║
║  ║   │   ───────────────────────────────────                                                   │   ║  ║
║  ║   │   • Detailed scene description                                                          │   ║  ║
║  ║   │   • Colors as TEXT: "primary #2E7D32"                                                   │   ║  ║
║  ║   │   • + Global Note (if provided)  ◄── ✓ This works                                       │   ║  ║
║  ║   │   • + Regeneration Note (if regenerating single image)  ◄── ✓ This works               │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   IMAGE INPUTS (reference images):                                                      │   ║  ║
║  ║   │   ────────────────────────────────                                                      │   ║  ║
║  ║   │   • [IMG1] Primary Product        ◄── ✓ Always included                                 │   ║  ║
║  ║   │   • [IMG2-5] Additional Products  ◄── ✓ Included if provided                            │   ║  ║
║  ║   │   • [STYLE] Style Reference       ◄── ✓ Included (framework preview or user-provided)  │   ║  ║
║  ║   │   • [LOGO] Brand Logo             ◄── ✓ Included for non-MAIN images                    │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ║   OUTPUT: 5 Generated 1000x1000 images                                                          ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 3: SINGLE IMAGE REGENERATION (Optional)                        ║  ║
║  ║                              POST /api/generate/single                                           ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   User clicks "Regenerate" on one image with optional note                                       ║  ║
║  ║                                                                                                  ║  ║
║  ║   CURRENT FLOW:                                                                                  ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   User Note: "Make the background warmer, add more contrast"                            │   ║  ║
║  ║   │                           │                                                             │   ║  ║
║  ║   │                           ▼                                                             │   ║  ║
║  ║   │   ┌───────────────────────────────────────────────────────────────────────────────┐    │   ║  ║
║  ║   │   │  ⚠️  PROBLEM: Note goes DIRECTLY to Gemini, BYPASSES Vision AI!               │    │   ║  ║
║  ║   │   │                                                                               │    │   ║  ║
║  ║   │   │  Original Prompt (from Vision AI, stored in framework)                        │    │   ║  ║
║  ║   │   │           +                                                                   │    │   ║  ║
║  ║   │   │  "=== REGENERATION INSTRUCTIONS ===\n{user_note}"                             │    │   ║  ║
║  ║   │   │           │                                                                   │    │   ║  ║
║  ║   │   │           ▼                                                                   │    │   ║  ║
║  ║   │   │  DIRECTLY TO GEMINI IMAGE GENERATOR                                           │    │   ║  ║
║  ║   │   │                                                                               │    │   ║  ║
║  ║   │   │  Vision AI NEVER SEES the regeneration note!                                  │    │   ║  ║
║  ║   │   │  It cannot reinterpret or enhance the prompt based on feedback                │    │   ║  ║
║  ║   │   └───────────────────────────────────────────────────────────────────────────────┘    │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## PART 2: IDENTIFIED PROBLEMS

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                       PROBLEM ANALYSIS                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║  PROBLEM #1: VISION AI ONLY SEES PRIMARY IMAGE                                                        ║
║  ══════════════════════════════════════════════                                                       ║
║                                                                                                       ║
║    Current: Vision AI receives [IMG1] only                                                            ║
║    Impact:  Cannot understand product from multiple angles                                            ║
║             Cannot see texture details, back view, size comparison, etc.                              ║
║                                                                                                       ║
║    Example: User uploads bag of candy + close-up of candy shapes                                      ║
║             AI Designer only sees the bag, misses the candy details                                   ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PROBLEM #2: COLOR PALETTE IS JUST A SUGGESTION                                                       ║
║  ═══════════════════════════════════════════════                                                      ║
║                                                                                                       ║
║    Current: primary_color passed as "Primary Color Preference: {hex}"                                 ║
║    Impact:  AI may decide to use completely different colors                                          ║
║             User has no way to FORCE specific colors                                                  ║
║                                                                                                       ║
║    User expectation: "I selected #FF5722, all 4 frameworks should use it as primary"                  ║
║    Reality: AI might say "I see green in your product, I'll use green instead"                       ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PROBLEM #3: STYLE REFERENCE NOT SHOWN TO AI DESIGNER                                                 ║
║  ════════════════════════════════════════════════════                                                 ║
║                                                                                                       ║
║    Current: Style reference goes directly to Gemini Image Gen, bypasses Vision AI                     ║
║    Impact:  AI Designer cannot analyze the style and adapt frameworks accordingly                     ║
║             Frameworks might clash with the style reference                                           ║
║                                                                                                       ║
║    Example: User provides minimalist Japanese style reference                                         ║
║             AI Designer generates bold, busy American-style frameworks                                ║
║             Final images have conflicting visual direction                                            ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PROBLEM #4: REGENERATION BYPASSES AI DESIGNER                                                        ║
║  ═════════════════════════════════════════════════                                                    ║
║                                                                                                       ║
║    Current: Regeneration note appended directly to prompt, sent to Gemini                             ║
║    Impact:  Complex feedback not properly interpreted                                                 ║
║             "Make it more premium" just gets appended, not translated to specific instructions        ║
║                                                                                                       ║
║    User writes: "This looks too cheap, make it more premium and elegant"                              ║
║    What happens: Text appended as-is to 500-word prompt                                               ║
║    What should happen: AI Designer rewrites prompt with premium lighting,                             ║
║                        refined composition, elevated typography, etc.                                 ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PROBLEM #5: NO "AI DECIDES" vs "USER DECIDES" DISTINCTION                                            ║
║  ══════════════════════════════════════════════════════════                                           ║
║                                                                                                       ║
║    Current: Everything is a soft suggestion                                                           ║
║    Impact:  User cannot lock in decisions                                                             ║
║                                                                                                       ║
║    Should support:                                                                                    ║
║    • "AI, you pick the colors" (no color input)                                                       ║
║    • "Use EXACTLY these colors" (locked palette)                                                      ║
║    • "Start with this color, complete the palette" (hybrid)                                           ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PROBLEM #6: AI DESIGNER DOESN'T KNOW ABOUT ATTACHED IMAGES                                           ║
║  ═══════════════════════════════════════════════════════════                                          ║
║                                                                                                       ║
║    Current: Prompt doesn't tell AI what images are attached or how to reference them                  ║
║    Impact:  AI cannot say "In image 2, I see the texture detail, incorporate that"                   ║
║             Cannot strategically use different reference images for different outputs                 ║
║                                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## PART 3: PROPOSED IDEAL FLOW

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    PROPOSED IDEAL SYSTEM FLOW                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                                     USER INPUTS (Frontend)                                       │  ║
║  ├─────────────────────────────────────────────────────────────────────────────────────────────────┤  ║
║  │                                                                                                  │  ║
║  │   IMAGES                          TEXT DATA                      PREFERENCES (with modes)        │  ║
║  │   ══════                          ═════════                      ═══════════════════════════     │  ║
║  │   [IMG1] Primary Product ───┐     • Product Title                                                │  ║
║  │   [IMG2] Additional #1  ────┤     • Feature 1                    COLOR MODE:                     │  ║
║  │   [IMG3] Additional #2  ────┤     • Feature 2                    ○ AI Decides (no input)         │  ║
║  │   [IMG4] Additional #3  ────┤     • Feature 3                    ○ Suggest Primary (soft)        │  ║
║  │   [IMG5] Additional #4  ────┘     • Target Audience              ● LOCK Palette (hard) ◄── NEW   │  ║
║  │                                   • Brand Name                      [#hex1] [#hex2] [#hex3]      │  ║
║  │   [LOGO] Brand Logo                                                                              │  ║
║  │   [STYLE] Style Reference ──────────────────────────────────────────────────────────────────────│  ║
║  │   [GLOBAL_NOTE] Global Instructions                                                              │  ║
║  │                                                                                                  │  ║
║  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 1: FRAMEWORK ANALYSIS (IMPROVED)                               ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   VISION AI NOW RECEIVES:                                                                        ║  ║
║  ║   ────────────────────────                                                                       ║  ║
║  ║                                                                                                  ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │  IMAGES (ALL OF THEM):                                                                  │   ║  ║
║  ║   │  ─────────────────────                                                                  │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │  [IMG1] Primary Product   ──┐                                                           │   ║  ║
║  ║   │  [IMG2] Additional #1    ───┼──▶  ALL sent to Vision AI                                │   ║  ║
║  ║   │  [IMG3] Additional #2    ───┤     with LABELS so AI knows what each is                 │   ║  ║
║  ║   │  [IMG4] Additional #3    ───┤                                                           │   ║  ║
║  ║   │  [IMG5] Additional #4    ───┘                                                           │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │  [STYLE] Style Reference ──────▶  AI can analyze target aesthetic                       │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │  [LOGO] Brand Logo ────────────▶  AI can incorporate brand identity                     │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │  TEXT PROMPT (ENHANCED):                                                                │   ║  ║
║  ║   │  ───────────────────────                                                                │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │  "You are a Principal Designer. I'm showing you MULTIPLE IMAGES:                        │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   IMAGE 1 (PRIMARY): Main product shot - use this as the hero reference                │   ║  ║
║  ║   │   IMAGE 2 (DETAIL): Close-up showing texture/detail - note materials                    │   ║  ║
║  ║   │   IMAGE 3 (ANGLE): Side view - understand product dimensions                            │   ║  ║
║  ║   │   IMAGE 4 (CONTEXT): Product in use - understand use case                               │   ║  ║
║  ║   │   IMAGE 5 (STYLE REF): This is the VISUAL STYLE the user wants                          │   ║  ║
║  ║   │   IMAGE 6 (LOGO): Brand logo - incorporate brand identity                               │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   Analyze ALL images and create frameworks that work with what you see.                 │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   COLOR INSTRUCTIONS:                                                                   │   ║  ║
║  ║   │   ───────────────────                                                                   │   ║  ║
║  ║   │   MODE: LOCKED_PALETTE                                                                  │   ║  ║
║  ║   │   You MUST use these EXACT colors in ALL 4 frameworks:                                  │   ║  ║
║  ║   │   • Primary: #2196F3 (use for backgrounds, main elements)                               │   ║  ║
║  ║   │   • Secondary: #1565C0 (supporting elements)                                            │   ║  ║
║  ║   │   • Accent: #FF5722 (CTAs, highlights)                                                  │   ║  ║
║  ║   │   • Text Dark: #212121 (dark text)                                                      │   ║  ║
║  ║   │   • Text Light: #FFFFFF (light text)                                                    │   ║  ║
║  ║   │   DO NOT deviate from these colors. Vary typography, layout, mood instead.              │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   --- OR if MODE: SUGGEST_PRIMARY ---                                                   │   ║  ║
║  ║   │   User prefers primary color: #2196F3                                                   │   ║  ║
║  ║   │   Build a harmonious palette around this, but you may adjust if needed.                 │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │   --- OR if MODE: AI_DECIDES ---                                                        │   ║  ║
║  ║   │   Analyze the product images and style reference to determine optimal colors.           │   ║  ║
║  ║   │   ..."                                                                                  │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ║   VISION AI OUTPUT (ENHANCED):                                                                   ║  ║
║  ║   ─────────────────────────────                                                                  ║  ║
║  ║   • Multi-image analysis (saw all angles, style ref, logo)                                       ║  ║
║  ║   • 4 Frameworks with:                                                                           ║  ║
║  ║     - Colors (LOCKED if user specified, or AI-chosen if not)                                     ║  ║
║  ║     - Typography (varied across frameworks)                                                      ║  ║
║  ║     - Story arc (tailored to what AI saw)                                                        ║  ║
║  ║     - Layout (varied across frameworks)                                                          ║  ║
║  ║     - NOTES on which reference images to emphasize for each image type                          ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                              USER SELECTS A FRAMEWORK                                            │  ║
║  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 2: GENERATE FINAL IMAGES (IMPROVED)                            ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   STEP 2A: VISION AI GENERATES 5 PROMPTS (with image awareness)                                 ║  ║
║  ║   ─────────────────────────────────────────────────────────────                                  ║  ║
║  ║                                                                                                  ║  ║
║  ║   Vision AI receives:                                                                            ║  ║
║  ║   • Selected framework                                                                           ║  ║
║  ║   • REMINDER of available reference images:                                                      ║  ║
║  ║     "When writing prompts, remember these images will be passed to the generator:               ║  ║
║  ║      - Product images showing [X, Y, Z]                                                         ║  ║
║  ║      - Style reference showing [aesthetic]                                                       ║  ║
║  ║      - Logo for brand integration                                                                ║  ║
║  ║      Reference them in your prompts where appropriate."                                          ║  ║
║  ║                                                                                                  ║  ║
║  ║   Output prompts can now say:                                                                    ║  ║
║  ║   "For the infographic, emphasize the texture detail visible in reference image 2..."            ║  ║
║  ║   "Match the soft lighting style from the style reference image..."                              ║  ║
║  ║                                                                                                  ║  ║
║  ║   STEP 2B: GEMINI IMAGE GENERATOR (same as before, but better prompts)                          ║  ║
║  ║   ───────────────────────────────────────────────────────────────────                            ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                               │                                                       ║
║                                               ▼                                                       ║
║  ╔═════════════════════════════════════════════════════════════════════════════════════════════════╗  ║
║  ║                              STEP 3: REGENERATION (IMPROVED)                                     ║  ║
║  ╠═════════════════════════════════════════════════════════════════════════════════════════════════╣  ║
║  ║                                                                                                  ║  ║
║  ║   TWO MODES:                                                                                     ║  ║
║  ║                                                                                                  ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │  MODE A: QUICK REGENERATE (current behavior)                                            │   ║  ║
║  ║   │  ─────────────────────────────────────────────                                          │   ║  ║
║  ║   │  • User clicks "Regenerate" with no note                                                │   ║  ║
║  ║   │  • Same prompt sent to Gemini again                                                     │   ║  ║
║  ║   │  • Fast, simple, slight variation                                                       │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ║   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   ║  ║
║  ║   │  MODE B: AI-ENHANCED REGENERATE (NEW)                                                   │   ║  ║
║  ║   │  ────────────────────────────────────────                                               │   ║  ║
║  ║   │  • User provides feedback note                                                          │   ║  ║
║  ║   │  • Note goes to VISION AI first:                                                        │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   │    User: "Make it more premium, less cluttered"                                         │   ║  ║
║  ║   │              │                                                                          │   ║  ║
║  ║   │              ▼                                                                          │   ║  ║
║  ║   │    ┌─────────────────────────────────────────────────────────────────────────────┐     │   ║  ║
║  ║   │    │  VISION AI (Prompt Enhancer):                                               │     │   ║  ║
║  ║   │    │                                                                             │     │   ║  ║
║  ║   │    │  "The user wants this image to feel more premium and less cluttered.        │     │   ║  ║
║  ║   │    │   Here's the original prompt: [...]                                         │     │   ║  ║
║  ║   │    │                                                                             │     │   ║  ║
║  ║   │    │   Rewrite this prompt to:                                                   │     │   ║  ║
║  ║   │    │   - Emphasize luxury lighting (soft, diffused, high-key)                   │     │   ║  ║
║  ║   │    │   - Reduce number of elements (show only 3 features, not 5)                │     │   ║  ║
║  ║   │    │   - Add more whitespace                                                     │     │   ║  ║
║  ║   │    │   - Use more refined typography                                             │     │   ║  ║
║  ║   │    │   - Premium background treatment"                                           │     │   ║  ║
║  ║   │    │                                                                             │     │   ║  ║
║  ║   │    │  OUTPUT: Completely rewritten, premium-focused prompt                       │     │   ║  ║
║  ║   │    └─────────────────────────────────────────────────────────────────────────────┘     │   ║  ║
║  ║   │              │                                                                          │   ║  ║
║  ║   │              ▼                                                                          │   ║  ║
║  ║   │    GEMINI IMAGE GENERATOR receives BETTER prompt                                        │   ║  ║
║  ║   │                                                                                         │   ║  ║
║  ║   └─────────────────────────────────────────────────────────────────────────────────────────┘   ║  ║
║  ║                                                                                                  ║  ║
║  ╚═════════════════════════════════════════════════════════════════════════════════════════════════╝  ║
║                                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## PART 4: INPUT ROUTING MATRIX (Proposed)

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              WHERE EACH INPUT SHOULD GO                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║                                 │ Step 1:      │ Step 2A:     │ Step 2B:      │ Step 3:              ║
║                                 │ Framework    │ Prompt       │ Image         │ Regeneration         ║
║  INPUT                          │ Analysis     │ Generation   │ Generation    │                      ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │ (Vision AI)  │ (Vision AI)  │ (Gemini Img)  │ (depends on mode)    ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │              │              │               │                      ║
║  [IMG1] Primary Product         │ ✅ SEES      │ ❌ (text)    │ ✅ Reference  │ ✅ Reference         ║
║  [IMG2-5] Additional Products   │ ✅ SEES      │ ❌ (text)    │ ✅ Reference  │ ✅ Reference         ║
║  [STYLE] Style Reference        │ ✅ SEES      │ ❌ (text)    │ ✅ Reference  │ ✅ Reference         ║
║  [LOGO] Brand Logo              │ ✅ SEES      │ ❌ (text)    │ ✅ Reference* │ ✅ Reference*        ║
║                                 │              │              │ (*non-main)   │                      ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │              │              │               │                      ║
║  Product Title                  │ ✅ Text      │ ✅ Text      │ ❌ (in prompt)│ ❌                   ║
║  Features 1-3                   │ ✅ Text      │ ✅ Text      │ ❌ (in prompt)│ ❌                   ║
║  Target Audience                │ ✅ Text      │ ✅ Text      │ ❌ (in prompt)│ ❌                   ║
║  Brand Name                     │ ✅ Text      │ ✅ Text      │ ❌ (in prompt)│ ❌                   ║
║                                 │              │              │               │                      ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │              │              │               │                      ║
║  Color Mode:                    │              │              │               │                      ║
║    • AI_DECIDES                 │ ✅ "You pick"│ ❌           │ ❌ (in prompt)│ ❌                   ║
║    • SUGGEST_PRIMARY            │ ✅ "Suggest" │ ❌           │ ❌ (in prompt)│ ❌                   ║
║    • LOCKED_PALETTE             │ ✅ "MUST use"│ ❌           │ ❌ (in prompt)│ ❌                   ║
║                                 │              │              │               │                      ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │              │              │               │                      ║
║  Global Note                    │ ❌           │ ❌           │ ✅ Appended   │ ✅ Appended          ║
║  Regeneration Note              │ ❌           │ ❌           │ ❌            │ ✅ To Vision AI      ║
║                                 │              │              │               │   (enhanced mode)    ║
║                                 │              │              │               │                      ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                 │              │              │               │                      ║
║  Selected Framework             │ ❌           │ ✅ Full      │ ❌ (in prompt)│ ✅ For context       ║
║                                 │              │              │               │                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## PART 5: IMPLEMENTATION PRIORITIES

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                  IMPLEMENTATION ROADMAP                                               ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║  PRIORITY 1: Send ALL images to Vision AI in Step 1                                                   ║
║  ════════════════════════════════════════════════════                                                 ║
║  • Files to modify:                                                                                   ║
║    - app/services/gemini_vision_service.py                                                            ║
║    - app/services/openai_vision_service.py                                                            ║
║    - app/api/endpoints/generation.py (FrameworkGenerationWithImageRequest)                            ║
║  • Changes:                                                                                           ║
║    - Accept additional_upload_paths in generate_frameworks()                                          ║
║    - Accept style_reference_path in generate_frameworks()                                             ║
║    - Accept logo_path in generate_frameworks()                                                        ║
║    - Update prompt to label each image                                                                ║
║  • Effort: Medium                                                                                     ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PRIORITY 2: Add Color Mode (AI_DECIDES / SUGGEST / LOCKED)                                           ║
║  ═══════════════════════════════════════════════════════════                                          ║
║  • Files to modify:                                                                                   ║
║    - app/schemas/generation.py (add ColorMode enum)                                                   ║
║    - frontend/src/api/types.ts                                                                        ║
║    - frontend/src/components/ProductForm.tsx (add color mode selector)                                ║
║    - app/services/gemini_vision_service.py (conditional prompt)                                       ║
║    - app/services/openai_vision_service.py (conditional prompt)                                       ║
║  • Changes:                                                                                           ║
║    - New enum: ColorMode { AI_DECIDES, SUGGEST_PRIMARY, LOCKED_PALETTE }                              ║
║    - New field: color_palette: List[str] (for locked mode)                                            ║
║    - Update PRINCIPAL_DESIGNER_VISION_PROMPT with mode-specific instructions                          ║
║  • Effort: Medium                                                                                     ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PRIORITY 3: AI-Enhanced Regeneration                                                                 ║
║  ════════════════════════════════════════                                                             ║
║  • Files to modify:                                                                                   ║
║    - app/services/generation_service.py (generate_single_image)                                       ║
║    - app/services/gemini_vision_service.py (new method: enhance_prompt_with_feedback)                 ║
║    - app/api/endpoints/generation.py                                                                  ║
║    - frontend/src/components/ImageGallery.tsx (add "Enhanced Regenerate" option)                      ║
║  • Changes:                                                                                           ║
║    - New Vision AI method to rewrite prompt based on feedback                                         ║
║    - Frontend option to choose quick vs enhanced regeneration                                         ║
║  • Effort: Medium-High                                                                                ║
║                                                                                                       ║
║  ─────────────────────────────────────────────────────────────────────────────────────────────────── ║
║                                                                                                       ║
║  PRIORITY 4: Make Vision AI aware of image labels during prompt generation                            ║
║  ══════════════════════════════════════════════════════════════════════════                           ║
║  • Files to modify:                                                                                   ║
║    - app/services/gemini_vision_service.py (generate_image_prompts)                                   ║
║    - app/services/openai_vision_service.py (generate_image_prompts)                                   ║
║  • Changes:                                                                                           ║
║    - Add image inventory to prompt:                                                                   ║
║      "The image generator will receive these references:                                              ║
║       - Primary product image (detailed shot)                                                         ║
║       - 3 additional product images showing [angles]                                                  ║
║       - Style reference (minimalist Japanese aesthetic)                                               ║
║       - Brand logo                                                                                    ║
║       You may reference these in your prompts."                                                       ║
║  • Effort: Low                                                                                        ║
║                                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## PART 6: DECISION TREE - AI vs USER

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          WHAT AI DECIDES vs WHAT USER DECIDES                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                       ║
║                         USER ALWAYS DECIDES                AI ALWAYS DECIDES                          ║
║                         ═══════════════════                ═════════════════════                      ║
║                         • Product images                   • Prompt structure                         ║
║                         • Product info (title, features)   • Composition details                      ║
║                         • Target audience                  • Specific wording                         ║
║                         • Brand name                       • Scene descriptions                       ║
║                         • Logo                             • Technical details                        ║
║                         • Style reference                  • Story arc flow                           ║
║                         • Global note                      • Image-specific tactics                   ║
║                                                                                                       ║
║                                                                                                       ║
║                         USER CAN CHOOSE (Mode-Based)                                                  ║
║                         ════════════════════════════                                                  ║
║                                                                                                       ║
║   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   ║
║   │                                                                                              │   ║
║   │   COLORS:                                                                                    │   ║
║   │   ────────                                                                                   │   ║
║   │                                                                                              │   ║
║   │   ○ AI_DECIDES              ○ SUGGEST_PRIMARY           ● LOCKED_PALETTE                     │   ║
║   │     "You pick colors          "Start with #2196F3,        "Use EXACTLY these:                │   ║
║   │      based on product"         build harmony"              #2196F3, #1565C0, #FF5722"        │   ║
║   │                                                                                              │   ║
║   │         │                           │                             │                          │   ║
║   │         ▼                           ▼                             ▼                          │   ║
║   │   AI analyzes product         AI uses as anchor,          AI uses exact colors,              │   ║
║   │   and picks all 5 colors      may adjust slightly         varies other elements              │   ║
║   │                                                                                              │   ║
║   └──────────────────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                                       ║
║   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   ║
║   │                                                                                              │   ║
║   │   TYPOGRAPHY:                                                                                │   ║
║   │   ────────────                                                                               │   ║
║   │                                                                                              │   ║
║   │   ○ AI_DECIDES              ○ SUGGEST_STYLE             ○ LOCKED_FONTS (future)              │   ║
║   │     "Pick fonts that          "I prefer modern            "Use Montserrat for headlines,     │   ║
║   │      match the product"        sans-serif"                 Inter for body"                   │   ║
║   │                                                                                              │   ║
║   └──────────────────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                                       ║
║   ┌──────────────────────────────────────────────────────────────────────────────────────────────┐   ║
║   │                                                                                              │   ║
║   │   REGENERATION:                                                                              │   ║
║   │   ──────────────                                                                             │   ║
║   │                                                                                              │   ║
║   │   ○ QUICK (no note)         ○ SIMPLE (note appended)    ● ENHANCED (AI interprets)           │   ║
║   │     Same prompt,              User note appended          AI rewrites prompt based            │   ║
║   │     slight variation          directly to prompt          on user feedback                    │   ║
║   │                                                                                              │   ║
║   └──────────────────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```
