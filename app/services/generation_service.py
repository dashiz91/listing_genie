"""
Image Generation Service
Orchestrates prompt building, image generation, and storage with robust error handling
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.database import (
    GenerationSession,
    SessionKeyword,
    ImageRecord,
    GenerationStatusEnum,
    ImageTypeEnum,
    DesignContext,
    PromptHistory,
    ColorModeEnum,
)
from app.prompts import PromptEngine, ProductContext, get_prompt_engine, get_all_styles
from app.services.gemini_service import GeminiService
from app.services.supabase_storage_service import SupabaseStorageService
from app.schemas.generation import (
    GenerationRequest,
    StylePreviewRequest,
    StylePreviewResult,
    ImageResult,
    GenerationStatusEnum as SchemaStatus,
    ImageTypeEnum as SchemaImageType,
    DesignFramework,
)
# Note: OpenAIVisionService is imported dynamically to avoid circular imports

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    MAX_RETRIES = 3
    BASE_DELAY = 1  # seconds
    MAX_DELAY = 8   # seconds

    # Prompt variations to try on retry
    VARIATIONS = [
        "",  # First attempt uses original prompt
        "\n\n[VARIATION: Emphasize clarity and simplicity. Use clean lines and minimal elements.]",
        "\n\n[VARIATION: Focus on product detail and precision. Showcase texture and quality.]",
        "\n\n[VARIATION: Prioritize clean composition. Ensure strong visual hierarchy.]",
    ]


class GenerationService:
    """Orchestrates the full image generation pipeline with robust error handling"""

    IMAGE_TYPES = [
        ImageTypeEnum.MAIN,
        ImageTypeEnum.INFOGRAPHIC_1,
        ImageTypeEnum.INFOGRAPHIC_2,
        ImageTypeEnum.LIFESTYLE,
        ImageTypeEnum.COMPARISON,
    ]

    def __init__(
        self,
        db: Session,
        gemini: GeminiService,
        storage: SupabaseStorageService,
        prompt_engine: PromptEngine = None,
    ):
        self.db = db
        self.gemini = gemini
        self.storage = storage
        self.prompt_engine = prompt_engine or get_prompt_engine()
        # Store framework for current session (set during create_session)
        self._current_framework: Optional[DesignFramework] = None

    def create_session(self, request: GenerationRequest, user_id: Optional[str] = None) -> GenerationSession:
        """
        Create a new generation session with all image records.

        Args:
            request: Generation request with product details
            user_id: Optional Supabase user ID (from authenticated request)

        Returns:
            Created GenerationSession object
        """
        # Store the design framework if provided (MASTER level)
        if request.design_framework:
            self._current_framework = request.design_framework
            logger.info(f"Using MASTER level framework: {request.design_framework.framework_name}")

        # Create session
        session = GenerationSession(
            user_id=user_id,  # Associate with authenticated user
            upload_path=request.upload_path,
            additional_upload_paths=request.additional_upload_paths or [],
            product_title=request.product_title,
            feature_1=request.feature_1,
            feature_2=request.feature_2,
            feature_3=request.feature_3,
            target_audience=request.target_audience,
            brand_name=request.brand_name,
            brand_colors=request.brand_colors or [],
            logo_path=request.logo_path,
            style_id=request.style_id,
            # MASTER Level: Brand vibe for creative brief system
            brand_vibe=request.brand_vibe.value if request.brand_vibe else None,
            primary_color=request.primary_color,
            style_reference_path=request.style_reference_path,
            color_count=request.color_count,
            color_palette=request.color_palette or [],
            status=GenerationStatusEnum.PENDING,
            # Store framework as JSON if provided
            design_framework_json=request.design_framework.model_dump() if request.design_framework else None,
            # Global note/instructions for all images
            global_note=request.global_note,
        )
        self.db.add(session)
        self.db.flush()  # Get ID

        # Add keywords
        for kw in request.keywords:
            keyword = SessionKeyword(
                session_id=session.id,
                keyword=kw.keyword,
                intent_types=kw.intents,
            )
            self.db.add(keyword)

        # Create image records for each type
        for image_type in self.IMAGE_TYPES:
            image_record = ImageRecord(
                session_id=session.id,
                image_type=image_type,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)

        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Created generation session: {session.id}")
        return session

    def create_design_context(
        self,
        session: GenerationSession,
        color_mode: ColorModeEnum = ColorModeEnum.AI_DECIDES,
        locked_colors: Optional[List[str]] = None,
        product_analysis: Optional[Dict] = None,
    ) -> DesignContext:
        """
        Create a DesignContext for AI Designer memory.

        This enables the AI Designer to remember:
        - What prompts it generated
        - What framework was selected
        - User feedback and regeneration history
        - Product analysis from initial vision (for regeneration context)

        Args:
            session: The generation session
            color_mode: How colors should be determined
            locked_colors: Specific hex colors if mode is LOCKED_PALETTE
            product_analysis: AI's analysis of the product from framework generation

        Returns:
            Created DesignContext
        """
        # Check if context already exists
        existing = self.db.query(DesignContext).filter(
            DesignContext.session_id == session.id
        ).first()

        if existing:
            logger.info(f"DesignContext already exists for session {session.id}")
            return existing

        # Build image inventory from session
        image_inventory = []
        if session.upload_path:
            image_inventory.append({
                "type": "primary",
                "path": session.upload_path,
                "description": "Primary product photo"
            })

        if session.additional_upload_paths:
            for i, path in enumerate(session.additional_upload_paths):
                image_inventory.append({
                    "type": f"additional_{i+1}",
                    "path": path,
                    "description": f"Additional product photo {i+1}"
                })

        if session.style_reference_path:
            image_inventory.append({
                "type": "style_reference",
                "path": session.style_reference_path,
                "description": "Style reference image"
            })

        if session.logo_path:
            image_inventory.append({
                "type": "logo",
                "path": session.logo_path,
                "description": "Brand logo"
            })

        # Create context
        context = DesignContext(
            session_id=session.id,
            image_inventory=image_inventory,
            color_mode=color_mode,
            locked_colors=locked_colors or [],
            product_analysis=product_analysis,  # Store AI's analysis for regeneration context
        )

        # Store selected framework info if available
        if session.design_framework_json:
            fw = session.design_framework_json
            context.selected_framework_id = fw.get('framework_id')
            context.selected_framework_name = fw.get('framework_name')

        if product_analysis:
            logger.info(f"Storing product_analysis in DesignContext for session {session.id}")

        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)

        logger.info(f"Created DesignContext for session {session.id}")
        return context

    def get_design_context(self, session_id: str) -> Optional[DesignContext]:
        """Get the DesignContext for a session"""
        return self.db.query(DesignContext).filter(
            DesignContext.session_id == session_id
        ).first()

    def store_prompt_in_history(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum,
        prompt_text: str,
        user_feedback: Optional[str] = None,
        change_summary: Optional[str] = None,
        reference_image_paths: Optional[List[Dict]] = None,
    ) -> PromptHistory:
        """
        Store a prompt in the history for future reference.

        This enables AI Designer to see what it wrote before when regenerating.

        Args:
            context: The DesignContext
            image_type: Which image type this prompt is for
            prompt_text: The actual prompt sent to image generator
            user_feedback: User feedback that triggered this version (null for v1)
            change_summary: AI's interpretation of changes made
            reference_image_paths: Actual reference images passed to generation
                Format: [{"type": "primary", "path": "..."}, {"type": "previous_module", "path": "..."}]

        Returns:
            Created PromptHistory record
        """
        # Get current max version for this image type
        max_version = self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).count()

        new_version = max_version + 1

        history = PromptHistory(
            context_id=context.id,
            image_type=image_type,
            version=new_version,
            prompt_text=prompt_text,
            user_feedback=user_feedback,
            change_summary=change_summary,
            reference_image_paths=reference_image_paths,
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        logger.info(f"Stored prompt v{new_version} for {image_type.value} in history")
        return history

    def get_latest_prompt(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum
    ) -> Optional[PromptHistory]:
        """Get the most recent prompt for an image type"""
        return self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).order_by(PromptHistory.version.desc()).first()

    def get_prompt_history(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum
    ) -> List[PromptHistory]:
        """Get all prompt versions for an image type"""
        return self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).order_by(PromptHistory.version.asc()).all()

    def _build_product_context(
        self,
        session: GenerationSession,
        style_override: Optional[str] = None
    ) -> ProductContext:
        """Build ProductContext from session data"""
        # Convert keywords to dict format for PromptEngine
        keyword_intents: Dict[str, List[str]] = {}
        keywords: List[str] = []

        for kw in session.keywords:
            keywords.append(kw.keyword)
            keyword_intents[kw.keyword] = kw.intent_types or []

        # Filter out None features
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]

        return ProductContext(
            title=session.product_title,
            features=features,
            target_audience=session.target_audience or "",
            keywords=keywords,
            intents=keyword_intents,
            brand_colors=session.brand_colors or [],
            brand_name=session.brand_name,
            has_logo=bool(session.logo_path),
            style_id=style_override or session.style_id,
            # MASTER Level: Brand vibe for creative brief system
            brand_vibe=session.brand_vibe,
            primary_color=session.primary_color,
            has_style_reference=bool(session.style_reference_path),
            color_count=session.color_count,
            color_palette=session.color_palette or [],
        )

    def _build_framework_prompt(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum
    ) -> str:
        """
        Build a RADICALLY DIFFERENT prompt for each image type using the design framework.

        PRIORITY ORDER:
        1. If GPT-4o generated detailed prompts exist in the framework, USE THEM DIRECTLY
        2. If not, fall back to our template-based prompts

        Each of the 5 Amazon listing images serves a COMPLETELY DIFFERENT PURPOSE:
        1. MAIN: Pure product on white - NO text, NO graphics, CLEAN extraction
        2. INFOGRAPHIC_1: Technical breakdown with callouts, arrows, dimensions
        3. INFOGRAPHIC_2: Benefits/features with icons and organized layout
        4. LIFESTYLE: Real person using product in natural environment
        5. COMPARISON: Multiple use cases or trust-building elements
        """
        if not self._current_framework:
            raise ValueError("No design framework available")

        fw = self._current_framework

        # Map image type to image number (1-5)
        image_type_map = {
            ImageTypeEnum.MAIN: 1,
            ImageTypeEnum.INFOGRAPHIC_1: 2,
            ImageTypeEnum.INFOGRAPHIC_2: 3,
            ImageTypeEnum.LIFESTYLE: 4,
            ImageTypeEnum.COMPARISON: 5,
        }
        image_num = image_type_map.get(image_type, 1)

        # PRIORITY 1: Check if GPT-4o generated prompts exist in the framework
        if fw.generation_prompts:
            for gen_prompt in fw.generation_prompts:
                if gen_prompt.image_number == image_num:
                    logger.info(f"Using GPT-4o generated prompt for {image_type.value} (image {image_num})")
                    # Return the GPT-4o generated prompt directly!
                    return gen_prompt.prompt

        # PRIORITY 2: Fall back to template-based prompts
        logger.info(f"No GPT-4o prompt found, using template for {image_type.value}")

        # Get the specific copy for this image type
        image_copy = None
        for copy in fw.image_copy:
            if copy.image_number == image_num:
                image_copy = copy
                break
        if not image_copy and fw.image_copy:
            image_copy = fw.image_copy[0]

        # Dispatch to specialized template prompt builder
        if image_type == ImageTypeEnum.MAIN:
            return self._build_main_image_prompt(session, fw)
        elif image_type == ImageTypeEnum.INFOGRAPHIC_1:
            return self._build_infographic_1_prompt(session, fw, image_copy)
        elif image_type == ImageTypeEnum.INFOGRAPHIC_2:
            return self._build_infographic_2_prompt(session, fw, image_copy)
        elif image_type == ImageTypeEnum.LIFESTYLE:
            return self._build_lifestyle_prompt(session, fw, image_copy)
        elif image_type == ImageTypeEnum.COMPARISON:
            return self._build_comparison_prompt(session, fw, image_copy)
        else:
            return self._build_main_image_prompt(session, fw)

    def _build_main_image_prompt(
        self,
        session: GenerationSession,
        fw: DesignFramework
    ) -> str:
        """
        Build prompt for MAIN/HERO image.

        This is THE most important image - it's what shoppers see first.
        Amazon REQUIRES: Pure white background, product only, NO text, NO graphics.
        Think: Apple product photography level of clean extraction.
        """
        # Get product features for context
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]
        features_str = ', '.join(features) if features else 'premium quality product'

        prompt = f"""=== AMAZON MAIN LISTING IMAGE - HERO SHOT ===

PRODUCT: {session.product_title}
KEY FEATURES: {features_str}

=== CRITICAL AMAZON REQUIREMENTS (MANDATORY) ===
This is Image 1 of 5 - The MAIN HERO image that appears in search results.
Amazon has STRICT requirements that MUST be followed:

1. PURE WHITE BACKGROUND (#FFFFFF)
   - The background MUST be completely white, no gradients, no off-white
   - No shadows on the background (product shadow on white is OK if subtle)
   - White must extend to all edges of the image

2. PRODUCT ONLY - ABSOLUTELY NO TEXT
   - NO headlines, NO captions, NO watermarks, NO logos
   - NO call-to-action text, NO feature callouts
   - NO brand names written in the image
   - The ONLY element in the image is the product itself

3. NO ADDITIONAL GRAPHICS
   - NO icons, NO badges, NO stickers
   - NO "Best Seller" labels or similar
   - NO decorative elements whatsoever
   - NO lifestyle props or accessories (unless part of the actual product)

4. PRODUCT FILLS 85% OF FRAME
   - The product should dominate the image
   - Some white space around edges (but product is prominent)
   - Product should be shown at its most flattering angle

=== PHOTOGRAPHY STYLE ===
Think: Apple product photography, high-end catalog, premium e-commerce

LIGHTING:
- Soft, diffused studio lighting from multiple angles
- No harsh shadows - use fill lights to soften
- Subtle product shadows allowed (grounds the product, adds dimension)
- Even illumination across the entire product
- Highlight the product's best features through strategic lighting

ANGLE & COMPOSITION:
- 3/4 view angle is often most flattering (shows depth)
- Or straight-on hero shot if product is flat/simple
- Center the product in the frame
- Slight elevation can add gravitas
- Show the full product - no cropping of important features

PRODUCT PRESENTATION:
- Product should look pristine, perfect condition
- Show the product in its "hero state" - how it looks when brand new
- If the product has multiple parts, show them arranged attractively
- Any packaging should be removed unless packaging IS the product

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format (Amazon standard)
- High resolution, sharp focus on product
- No motion blur, no depth of field effects that obscure product
- True-to-life colors (accurate product representation)
- Professional e-commerce product photography quality

=== DESIGN CONTEXT (FOR CONSISTENCY) ===
Framework: {fw.framework_name}
Visual Mood: {', '.join(fw.visual_treatment.mood_keywords)}

The product photography style should subtly reflect the premium, professional nature
of the {fw.framework_name} design system while strictly adhering to Amazon requirements.

=== FINAL OUTPUT ===
Generate a PURE PRODUCT PHOTOGRAPHY image:
- Pristine white background
- Product as the sole hero
- Zero text, zero graphics
- Professional studio lighting
- 85% frame fill
- Ready for Amazon search results

This image must STOP THE SCROLL when shoppers browse Amazon search results.
It should communicate quality, professionalism, and trustworthiness through
the product presentation alone - no text needed.
"""
        return prompt

    def _build_infographic_1_prompt(
        self,
        session: GenerationSession,
        fw: DesignFramework,
        image_copy
    ) -> str:
        """
        Build prompt for INFOGRAPHIC 1 - Technical Breakdown.

        This image shows the TECHNICAL aspects of the product:
        - Dimensions with measurement lines
        - Materials callouts with arrows pointing to specific parts
        - Exploded view showing components
        - Technical specifications in clean callout boxes
        """
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]

        # Build color instructions
        primary_color = fw.colors[0].hex if fw.colors else '#1a1a1a'
        accent_color = fw.colors[1].hex if len(fw.colors) > 1 else '#4a90d9'

        # Build callouts from features and image copy
        callouts = []
        if image_copy and image_copy.feature_callouts:
            callouts = image_copy.feature_callouts
        elif features:
            callouts = features[:4]

        callouts_str = '\n'.join([f"   - {c}" for c in callouts]) if callouts else "   - Premium Materials\n   - Quality Construction"

        prompt = f"""=== AMAZON INFOGRAPHIC IMAGE 1 - TECHNICAL BREAKDOWN ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 2 of 5 - The TECHNICAL INFOGRAPHIC.
Purpose: Show customers the TECHNICAL DETAILS, MATERIALS, and SPECIFICATIONS.
Think: Product engineering diagram meets clean marketing infographic.

=== VISUAL COMPOSITION TYPE ===
This is NOT a simple product photo with text overlay.
This is a TECHNICAL BREAKDOWN with the following elements:

1. CENTRAL PRODUCT IMAGE
   - Product shown from an angle that reveals multiple components
   - Could be: 3/4 view, exploded view, or cross-section view
   - Product is still the hero but not filling entire frame
   - Leave space around product for callouts

2. CALLOUT LINES & ARROWS (MANDATORY)
   - Clean, thin lines (2-3px) extending from product to text
   - Lines should be straight with 90-degree bends (not curved)
   - Arrow tips pointing TO specific product features
   - Color: {accent_color} or white with subtle shadow
   - Professional engineering drawing style

3. FEATURE CALLOUT BOXES
   - Small, clean text boxes at the end of each callout line
   - Semi-transparent or solid background for readability
   - Each box highlights ONE specific feature

   CALLOUTS TO INCLUDE:
{callouts_str}

4. DIMENSION ANNOTATIONS (if applicable)
   - Include measurement lines showing product size
   - Use standard dimension notation: arrows on both ends
   - Display key measurements (height, width, depth)
   - Professional technical drawing style

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Primary text/elements: {primary_color}
- Accent color (arrows, highlights): {accent_color}
- Background: Clean gradient or subtle pattern (NOT pure white - distinguish from main image)
- Recommended: Light gray to white gradient, or subtle brand color tint

TYPOGRAPHY:
- Font: {fw.typography.headline_font} or clean sans-serif
- Callout text: Bold, legible at thumbnail size (14-18pt equivalent)
- Use ALL CAPS for feature names, sentence case for descriptions
- High contrast for readability

LAYOUT:
- Product centered or slightly left/right to balance callouts
- Callouts distributed evenly around product
- Visual flow guides eye from product to features
- Whitespace between elements for clarity

=== INFOGRAPHIC ELEMENTS STYLE ===
DO include:
- Technical callout lines with arrows
- Small icons next to features (optional)
- Dimension lines with measurements
- Clean boxes/badges for feature text
- Subtle background pattern or gradient

DO NOT include:
- Lifestyle elements or people
- Busy or cluttered backgrounds
- Decorative swirls or flourishes
- Too many competing focal points
- Text that overlaps the product

=== VISUAL MOOD ===
Framework: {fw.framework_name}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

This should feel: Technical, Informative, Premium, Professional, Trustworthy
Think: High-end product specification sheet as a beautiful infographic

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text must be legible at 100x100px thumbnail
- High contrast between text and background
- Professional, clean, engineering-meets-marketing aesthetic

=== FINAL OUTPUT ===
Generate an INFOGRAPHIC-STYLE technical breakdown showing:
- Product with space for callouts
- 3-5 callout lines with arrows pointing to specific features
- Feature text in clean boxes
- Dimension annotations (if applicable)
- Professional, technical, yet beautiful presentation

This image should EDUCATE the customer about product specifications
while maintaining visual appeal and brand consistency.
"""
        return prompt

    def _build_infographic_2_prompt(
        self,
        session: GenerationSession,
        fw: DesignFramework,
        image_copy
    ) -> str:
        """
        Build prompt for INFOGRAPHIC 2 - Benefits & Features Grid.

        This image shows the BENEFITS in an organized, icon-driven layout:
        - Feature icons with short descriptions
        - Organized grid or list layout
        - Benefit-focused messaging (what it does FOR the customer)
        - Could include headline and supporting points
        """
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]

        # Build color palette
        primary_color = fw.colors[0].hex if fw.colors else '#1a1a1a'
        secondary_color = fw.colors[1].hex if len(fw.colors) > 1 else '#4a90d9'
        accent_color = fw.colors[2].hex if len(fw.colors) > 2 else '#27ae60'

        # Get headline if available
        headline = image_copy.headline if image_copy else "Why Choose Our Product?"

        # Build benefits list
        benefits = []
        if image_copy and image_copy.feature_callouts:
            benefits = image_copy.feature_callouts
        elif features:
            benefits = features

        benefits_str = '\n'.join([f"   {i+1}. {b}" for i, b in enumerate(benefits)]) if benefits else "   1. Premium Quality\n   2. Durable Design\n   3. Easy to Use"

        prompt = f"""=== AMAZON INFOGRAPHIC IMAGE 2 - BENEFITS & FEATURES ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 3 of 5 - The BENEFITS INFOGRAPHIC.
Purpose: Show customers the KEY BENEFITS in an organized, scannable format.
Think: Marketing flyer meets modern icon-driven design.

=== VISUAL COMPOSITION TYPE ===
This is a BENEFITS-FOCUSED INFOGRAPHIC with organized layout:

1. HEADLINE (Top section)
   - Bold, attention-grabbing headline
   - Text: "{headline}"
   - Font: {fw.typography.headline_font}, {fw.typography.headline_weight}
   - Color: {primary_color}

2. PRODUCT IMAGE (Center or Side)
   - Product shown at medium size (not dominating like main image)
   - Position: Center with benefits around it, OR left side with benefits on right
   - Product should be clearly visible but not competing with benefit icons

3. BENEFIT ICONS + TEXT (THE MAIN FEATURE)
   - 3-5 benefit points with ICONS and short text

   BENEFITS TO DISPLAY:
{benefits_str}

   ICON STYLE:
   - Simple, flat icons (not 3D or overly detailed)
   - Consistent style across all icons (all outline OR all filled)
   - Size: Medium (visible at thumbnail)
   - Color: {secondary_color} or {accent_color}

   TEXT STYLE:
   - Bold benefit name/headline
   - Optional: 1-line description below
   - High contrast for readability

4. ORGANIZED LAYOUT
   Options (choose most appropriate):
   - GRID: 2x2 or 3x2 grid of icon+text blocks
   - VERTICAL LIST: Icons stacked with text to the right
   - CIRCULAR: Benefits arranged around central product
   - BANNER: Horizontal rows of benefits

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Headlines: {primary_color}
- Icons: {secondary_color} or {accent_color}
- Background: Subtle gradient or clean solid (brand-aligned)
- Text backgrounds: Optional subtle boxes for contrast

TYPOGRAPHY:
- Headline: {fw.typography.headline_font}, {fw.typography.headline_weight}
- Benefit titles: Bold, {fw.typography.subhead_font}
- Descriptions: Regular weight, good contrast

LAYOUT PRINCIPLES:
- Clear visual hierarchy: Headline > Product > Benefits
- Even spacing between benefit blocks
- Aligned icons and text (professional grid)
- Breathing room (not cluttered)

=== VISUAL STYLE ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

STYLE GUIDE:
- Modern, clean, organized
- Scannable at a glance
- Professional marketing quality
- Consistent icon style throughout
- Clear visual hierarchy

DO include:
- Simple, recognizable icons
- Bold benefit headlines
- Subtle supporting text
- Professional layout grid
- Product image (but not dominating)

DO NOT include:
- Photo collages
- Busy backgrounds
- Too many font styles
- Cluttered layouts
- Illegible small text

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text must be legible at 100x100px thumbnail
- Icons should be recognizable at small sizes
- High contrast for accessibility

=== FINAL OUTPUT ===
Generate a BENEFIT-FOCUSED infographic with:
- Clear headline at top
- Product image (center or side)
- 3-5 benefit icons with short text
- Organized grid or list layout
- Professional, modern, marketing aesthetic

This image should CONVINCE customers of the product's value
through clear, scannable benefit communication.
"""
        return prompt

    def _build_lifestyle_prompt(
        self,
        session: GenerationSession,
        fw: DesignFramework,
        image_copy
    ) -> str:
        """
        Build prompt for LIFESTYLE image.

        This image shows the product IN USE by a REAL PERSON:
        - Authentic, natural setting
        - Person actively using/enjoying the product
        - Emotional connection - show the EXPERIENCE
        - Makes the customer imagine themselves with the product
        """
        # Determine target audience context
        audience = session.target_audience or "everyday consumers"

        # Get mood keywords for atmosphere
        mood = ', '.join(fw.visual_treatment.mood_keywords) if fw.visual_treatment.mood_keywords else 'natural, authentic, relatable'

        # Headline (if we want text overlay - optional for lifestyle)
        headline = image_copy.headline if image_copy else None

        prompt = f"""=== AMAZON LIFESTYLE IMAGE - REAL PERSON IN REAL ENVIRONMENT ===

PRODUCT: {session.product_title}
TARGET AUDIENCE: {audience}

=== IMAGE PURPOSE ===
This is Image 4 of 5 - The LIFESTYLE IMAGE.
Purpose: Show a REAL PERSON using the product in a REAL ENVIRONMENT.
This creates EMOTIONAL CONNECTION and helps customers visualize ownership.
Think: Magazine editorial, authentic photography, aspirational yet relatable.

=== CRITICAL REQUIREMENTS ===
This image MUST feature:

1. A REAL HUMAN BEING (MANDATORY)
   - NOT just the product alone
   - NOT just hands holding the product
   - A FULL or PARTIAL person visible in the image
   - Person should be using/enjoying the product naturally

2. AUTHENTIC ENVIRONMENT (MANDATORY)
   - Real-world setting (home, office, outdoors, etc.)
   - NOT a studio white background
   - NOT an abstract or artificial setting
   - Environment should match product use case

3. NATURAL INTERACTION (MANDATORY)
   - Person actively using or demonstrating the product
   - Natural, candid pose (not stiff or posed)
   - Shows the EXPERIENCE of using the product
   - Product is clearly visible but person is primary subject

=== PERSON SPECIFICATIONS ===
Based on target audience ({audience}):

DEMOGRAPHICS:
- Select a person that represents or appeals to the target audience
- Age, style, and appearance should resonate with likely buyers
- Authentic, relatable, aspirational but not unrealistic

EXPRESSION & POSE:
- Natural, genuine expression (not forced smile)
- Active engagement with product (using, examining, enjoying)
- Body language suggests satisfaction/enjoyment
- Candid feel, not overly posed

CLOTHING & STYLING:
- Appropriate to the environment and activity
- Clean, tasteful, not distracting from product
- Aligns with brand mood: {mood}

=== ENVIRONMENT SPECIFICATIONS ===
SETTING:
- Choose a setting where this product would naturally be used
- Examples based on product type:
  * Kitchen product → Modern home kitchen
  * Fitness product → Gym or outdoor exercise space
  * Office product → Clean, well-lit workspace
  * Beauty product → Bathroom or vanity area
  * Outdoor product → Nature, park, backyard
  * Tech product → Modern living room or office

LIGHTING:
- Natural lighting preferred (window light, golden hour, etc.)
- Soft, flattering lighting on both person and product
- {fw.visual_treatment.lighting_style}
- Warm, inviting atmosphere

BACKGROUND:
- Real environment, slightly blurred (depth of field)
- Not distracting but adds context
- Complementary to brand colors when possible
- Clean but lived-in feel

=== PRODUCT VISIBILITY ===
The product should be:
- Clearly visible in the shot
- Being actively used or held
- NOT the primary focus (person is primary)
- Naturally integrated into the scene
- Visible enough to recognize what it is

Product prominence: 30-40% of viewer attention
Person prominence: 60-70% of viewer attention

=== TEXT OVERLAY (OPTIONAL) ===
{"Include this headline if it enhances the image: " + chr(34) + headline + chr(34) if headline else "Text overlay is OPTIONAL for lifestyle images. The image should tell the story visually."}

If including text:
- Keep it minimal (headline only, if anything)
- Position where it doesn't obscure person or product
- Use brand typography: {fw.typography.headline_font}

=== PHOTOGRAPHY STYLE ===
OVERALL AESTHETIC:
- Editorial/magazine quality photography
- Natural, candid feel (not stock photo fake)
- Warm, inviting atmosphere
- Professional but relatable
- Aspirational without being unattainable

TECHNICAL:
- Shallow depth of field (subject in focus, background slightly soft)
- Natural color grading (not over-processed)
- Good composition following rule of thirds
- Person positioned at 1/3 line, product visible

MOOD:
- {mood}
- {fw.design_philosophy}

=== VISUAL MOOD ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}

The image should feel:
- Authentic and natural
- Warm and inviting
- Aspirational but achievable
- Connected to real life

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- High resolution, professional photography quality
- Natural color grading
- Sharp focus on subject (person with product)

=== FINAL OUTPUT ===
Generate a LIFESTYLE PHOTOGRAPH featuring:
- A real person actively using the product
- Authentic, real-world environment
- Natural lighting and candid feel
- Editorial/magazine photography quality
- Emotional connection that helps customers visualize ownership

This image should make customers FEEL what it's like to own and use this product.
It sells the EXPERIENCE, not just the item.
"""
        return prompt

    def _build_comparison_prompt(
        self,
        session: GenerationSession,
        fw: DesignFramework,
        image_copy
    ) -> str:
        """
        Build prompt for COMPARISON/CLOSING image.

        This is the 5th image - it serves to CLOSE THE SALE with:
        - Multiple use cases shown
        - What's included (package contents)
        - Trust elements (awards, certifications, guarantees)
        - Comparison showing product advantages
        - Or a final styled beauty shot
        """
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]

        # Build color palette
        primary_color = fw.colors[0].hex if fw.colors else '#1a1a1a'
        secondary_color = fw.colors[1].hex if len(fw.colors) > 1 else '#4a90d9'
        accent_color = fw.colors[2].hex if len(fw.colors) > 2 else '#27ae60'

        # Get CTA if available
        cta = image_copy.cta if image_copy and image_copy.cta else "Order Now"
        headline = image_copy.headline if image_copy else "Everything You Need"

        prompt = f"""=== AMAZON FINAL IMAGE - COMPARISON/CLOSING IMAGE ===

PRODUCT: {session.product_title}

=== IMAGE PURPOSE ===
This is Image 5 of 5 - The CLOSING IMAGE.
Purpose: CLOSE THE SALE. This image should eliminate remaining objections
and give the customer confidence to purchase.
Think: The final push that converts browsers to buyers.

=== COMPOSITION OPTIONS ===
Choose ONE of these approaches based on what would best close the sale:

OPTION A: MULTIPLE USE CASES
- Show 2-4 scenarios where the product excels
- Grid layout showing versatility
- "Use it for X, Y, and Z" visual story
- Demonstrates value through variety

OPTION B: PACKAGE CONTENTS / WHAT'S INCLUDED
- Show all items that come with purchase
- Organized flatlay or arranged display
- Clearly shows everything customer receives
- "You get all of this" presentation

OPTION C: TRUST & CREDIBILITY
- Include trust badges, certifications, awards
- Satisfaction guarantee badges
- Star ratings or review snippets
- "100% Satisfaction Guaranteed" messaging

OPTION D: STYLED BEAUTY SHOT
- Premium styled product photography
- Complementary props that elevate perception
- Aspirational setting (marble surface, greenery, etc.)
- Editorial magazine quality presentation

For this generation, create OPTION A or B (most common for Amazon).

=== VISUAL COMPOSITION ===

IF MULTIPLE USE CASES (Option A):
- 2x2 grid or triptych layout
- Each section shows a different use case
- Consistent styling across all sections
- Labels for each use case (optional)
- Product visible in each scenario

IF PACKAGE CONTENTS (Option B):
- Clean flatlay arrangement
- All items organized aesthetically
- Main product as hero, accessories around it
- Clear labeling of each item (optional)
- Premium presentation of what's included

=== DESIGN SPECIFICATIONS ===
COLOR PALETTE:
- Primary: {primary_color}
- Secondary: {secondary_color}
- Accent: {accent_color}
- Background: Clean, premium (subtle gradient or solid)

HEADLINE:
- Text: "{headline}"
- Position: Top or bottom of image
- Font: {fw.typography.headline_font}, bold
- Color: High contrast for readability

OPTIONAL CTA:
- Text: "{cta}"
- Position: Bottom of image
- Style: Button or badge format
- Color: {accent_color} or contrasting

LAYOUT:
- Clear visual hierarchy
- Organized, professional grid (if applicable)
- Product(s) prominently featured
- Text enhances but doesn't overwhelm

=== VISUAL ELEMENTS ===
DO include:
- Product shown in multiple scenarios OR complete package
- Clear, organized layout
- Optional headline and CTA
- Trust elements (if applicable)
- Premium, professional styling

OPTIONAL additions:
- Satisfaction guarantee badge
- "What's Included" label
- Use case labels
- Subtle icons representing benefits

DO NOT include:
- Cluttered or messy layouts
- Low-quality graphics
- Overwhelming amount of text
- Disconnected visual elements

=== BRAND ALIGNMENT ===
Framework: {fw.framework_name}
Brand Voice: {fw.brand_voice}
Mood: {', '.join(fw.visual_treatment.mood_keywords)}

Visual Treatment:
- Lighting: {fw.visual_treatment.lighting_style}
- Background: {fw.visual_treatment.background_treatment}
- Overall feel: Premium, trustworthy, compelling

=== CLOSING PSYCHOLOGY ===
This image should address:
1. "Is this product versatile enough?" → Show multiple uses
2. "What exactly do I get?" → Show package contents
3. "Can I trust this brand?" → Include trust elements
4. "Is this really premium?" → Styled beauty presentation

The image should make the customer think:
"Yes, I need this. I'm confident in this purchase."

=== TECHNICAL SPECIFICATIONS ===
- 1000x1000 pixel square format
- All text legible at 100x100px thumbnail
- High contrast, clear visual hierarchy
- Professional, e-commerce ready quality

=== FINAL OUTPUT ===
Generate a CLOSING/COMPARISON image that:
- Shows multiple use cases OR package contents
- Includes compelling headline
- Features trust elements or premium styling
- Maintains professional, organized layout
- Creates confidence and urgency to purchase

This image is the FINAL impression before the customer decides to buy.
Make it count.
"""
        return prompt

    def _get_story_beat(self, image_num: int, story_arc) -> str:
        """Get the story beat for a specific image number"""
        beats = {
            1: f"HOOK - {story_arc.hook}",
            2: f"REVEAL - {story_arc.reveal}",
            3: f"PROOF - {story_arc.proof}",
            4: f"DREAM - {story_arc.dream}",
            5: f"CLOSE - {story_arc.close}",
        }
        return beats.get(image_num, "HOOK")

    def _get_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = RetryConfig.BASE_DELAY * (2 ** attempt)
        return min(delay, RetryConfig.MAX_DELAY)

    def _get_prompt_variation(self, attempt: int) -> str:
        """Get prompt variation for retry attempt"""
        if attempt < len(RetryConfig.VARIATIONS):
            return RetryConfig.VARIATIONS[attempt]
        return RetryConfig.VARIATIONS[-1]

    async def generate_single_image(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        note: Optional[str] = None,
        use_ai_enhancement: bool = True,
    ) -> ImageResult:
        """
        Generate a single image type for a session with retry logic.

        Args:
            session: The generation session
            image_type: Which image type to generate
            note: Optional note/instructions for this specific image generation
            use_ai_enhancement: If True and note provided, use AI Designer to enhance prompt

        Returns:
            ImageResult with status and path
        """
        # Load design framework from session if not already loaded (for regeneration)
        if session.design_framework_json and not self._current_framework:
            try:
                self._current_framework = DesignFramework(**session.design_framework_json)
                logger.info(f"[REGENERATION] Loaded framework: {self._current_framework.framework_name}")
            except Exception as e:
                logger.warning(f"[REGENERATION] Failed to load framework: {e}")

        # Find the image record
        image_record = None
        for img in session.images:
            if img.image_type == image_type:
                image_record = img
                break

        if not image_record:
            raise ValueError(f"No image record found for type: {image_type}")

        # Update status to processing
        image_record.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        template_key = image_type.value

        # Get or create design context for prompt history
        design_context = self.get_design_context(session.id)
        if not design_context:
            design_context = self.create_design_context(session)

        # Track whether this is a regeneration with AI enhancement
        user_feedback = None
        change_summary = None

        # MASTER LEVEL: Use framework-based prompt if available
        if self._current_framework:
            base_prompt = self._build_framework_prompt(session, image_type)
        else:
            context = self._build_product_context(session)
            base_prompt = self.prompt_engine.build_prompt(template_key, context)

        # NOTE: global_note is now handled by AI Designer during generate_image_prompts()
        # It interprets the user's instructions differently for each image type
        # DO NOT append it raw here - that bypasses the intelligent interpretation
        if session.global_note:
            logger.info(f"[{template_key}] Global note exists but was already processed by AI Designer")

        # Handle regeneration note - use AI Designer to enhance if enabled
        if note:
            user_feedback = note  # Store for prompt history

            if use_ai_enhancement:
                # Try to get the previous prompt from history
                latest_prompt = self.get_latest_prompt(design_context, image_type)
                original_prompt = latest_prompt.prompt_text if latest_prompt else base_prompt

                # Use AI Designer to intelligently enhance the prompt
                try:
                    from app.services.openai_vision_service import get_openai_vision_service
                    vision_service = get_openai_vision_service()

                    # Get framework dict for context
                    framework_dict = None
                    if self._current_framework:
                        framework_dict = self._current_framework.model_dump()

                    # Get product_analysis from DesignContext for regeneration context
                    product_analysis_text = None
                    if design_context and design_context.product_analysis:
                        analysis = design_context.product_analysis
                        if isinstance(analysis, dict):
                            # Convert structured analysis to readable text
                            parts = []
                            if analysis.get('what_i_see'):
                                parts.append(f"What I see: {analysis['what_i_see']}")
                            if analysis.get('visual_characteristics'):
                                parts.append(f"Visual characteristics: {analysis['visual_characteristics']}")
                            if analysis.get('product_category'):
                                parts.append(f"Category: {analysis['product_category']}")
                            if analysis.get('natural_mood'):
                                parts.append(f"Mood: {analysis['natural_mood']}")
                            if analysis.get('ideal_customer'):
                                parts.append(f"Ideal customer: {analysis['ideal_customer']}")
                            product_analysis_text = "\n".join(parts) if parts else str(analysis)
                        else:
                            product_analysis_text = str(analysis)
                        logger.info(f"[REGENERATION] Using stored product_analysis for context")

                    logger.info(f"Using AI Designer to enhance prompt for {template_key}")
                    enhancement = await vision_service.enhance_prompt_with_feedback(
                        original_prompt=original_prompt,
                        user_feedback=note,
                        image_type=template_key,
                        framework=framework_dict,
                        product_analysis=product_analysis_text,
                    )

                    base_prompt = enhancement["enhanced_prompt"]
                    change_summary = enhancement.get("interpretation", "AI-enhanced based on feedback")
                    logger.info(f"AI Designer interpretation: {change_summary}")

                except Exception as e:
                    logger.warning(f"AI enhancement failed, falling back to append: {e}")
                    # Fallback: just append the note
                    base_prompt += f"\n\n=== REGENERATION INSTRUCTIONS ===\n{note}\n"
                    change_summary = "Direct append (AI enhancement unavailable)"
            else:
                # Direct append without AI enhancement
                base_prompt += f"\n\n=== REGENERATION INSTRUCTIONS ===\n{note}\n"
                change_summary = "Direct append"
                logger.info(f"Appending regeneration note to prompt for {template_key}")

        last_error = None

        for attempt in range(RetryConfig.MAX_RETRIES):
            try:
                # Add variation to prompt for retries
                variation = self._get_prompt_variation(attempt)
                prompt = base_prompt + variation

                logger.info(
                    f"Generating {template_key} for session {session.id} "
                    f"(attempt {attempt + 1}/{RetryConfig.MAX_RETRIES})"
                )

                # Build reference image paths:
                # 1. Product photo (always first - primary reference)
                # 2. Additional product photos (for better AI context)
                # 3. Style reference image (if provided - for all images)
                # 4. Logo (only for non-main images)
                reference_paths = [session.upload_path]

                # Track image indices for style reference
                current_index = 2  # Image 1 is primary product

                # Add additional product images for better context
                additional_count = 0
                if session.additional_upload_paths:
                    reference_paths.extend(session.additional_upload_paths)
                    additional_count = len(session.additional_upload_paths)
                    current_index += additional_count

                # Add style reference image (applies to ALL images including main)
                style_image_index = None
                if session.style_reference_path:
                    reference_paths.append(session.style_reference_path)
                    style_image_index = current_index
                    current_index += 1

                # Only add logo for non-main images (main/hero should be clean)
                logo_image_index = None
                if session.logo_path and image_type != ImageTypeEnum.MAIN:
                    reference_paths.append(session.logo_path)
                    logo_image_index = current_index

                # === COMPREHENSIVE REFERENCE IMAGE LOGGING ===
                logger.info("=" * 80)
                logger.info(f"[GENERATION] === IMAGE GENERATION REQUEST for {template_key.upper()} ===")
                logger.info(f"[GENERATION] Session ID: {session.id}")
                logger.info(f"[GENERATION] Product: {session.product_title}")
                logger.info(f"[GENERATION] Image Type: {template_key}")
                logger.info(f"[GENERATION] Attempt: {attempt + 1}/{RetryConfig.MAX_RETRIES}")
                logger.info("-" * 40)
                logger.info(f"[GENERATION] REFERENCE IMAGES ({len(reference_paths)} total):")
                for i, path in enumerate(reference_paths):
                    label = ""
                    if i == 0:
                        label = " (PRIMARY PRODUCT)"
                    elif style_image_index and i + 1 == style_image_index:
                        label = " (STYLE REFERENCE)"
                    elif logo_image_index and i + 1 == logo_image_index:
                        label = " (LOGO)"
                    elif i > 0 and i < 1 + additional_count:
                        label = f" (ADDITIONAL PRODUCT {i})"
                    logger.info(f"[GENERATION]   [Image {i+1}] {path}{label}")
                logger.info("-" * 40)
                logger.info(f"[GENERATION] FRAMEWORK: {self._current_framework.framework_name if self._current_framework else 'None'}")
                logger.info(f"[GENERATION] Has Style Reference: {style_image_index is not None}")
                logger.info(f"[GENERATION] Has Logo: {logo_image_index is not None}")
                logger.info(f"[GENERATION] Additional Images: {additional_count}")
                logger.info("=" * 80)

                # Prepend style reference instructions to prompt if style image provided
                if style_image_index:
                    from app.prompts.ai_designer import STYLE_REFERENCE_PROMPT_PREFIX

                    # Build additional images description
                    additional_desc = ""
                    for i in range(additional_count):
                        additional_desc += f"- Image {2 + i}: Additional product photo {i + 1}\n"

                    # Build logo description
                    logo_desc = ""
                    if logo_image_index:
                        logo_desc = f"- Image {logo_image_index}: Brand logo\n"

                    style_prefix = STYLE_REFERENCE_PROMPT_PREFIX.format(
                        style_image_index=style_image_index,
                        additional_images_desc=additional_desc,
                        logo_image_desc=logo_desc,
                    )
                    prompt = style_prefix + prompt
                    logger.info(f"[{template_key.upper()}] Added style reference prefix (style is Image #{style_image_index})")

                # Generate image with reference(s)
                generated_image = await self.gemini.generate_image(
                    prompt=prompt,
                    reference_image_paths=reference_paths,
                    aspect_ratio="1:1",
                    max_retries=1,  # Let our retry logic handle retries
                )

                if generated_image is None:
                    raise ValueError("No image returned from Gemini API")

                # Save to storage
                storage_path = self.storage.save_generated_image(
                    session_id=session.id,
                    image_type=template_key,
                    image=generated_image,
                )

                # Update record - success!
                image_record.storage_path = storage_path
                image_record.status = GenerationStatusEnum.COMPLETE
                image_record.completed_at = datetime.now(timezone.utc)
                image_record.retry_count = attempt
                image_record.error_message = None
                self.db.commit()

                # Store prompt in history for future reference
                if design_context:
                    try:
                        self.store_prompt_in_history(
                            context=design_context,
                            image_type=image_type,
                            prompt_text=prompt,  # The final prompt that was sent
                            user_feedback=user_feedback,
                            change_summary=change_summary,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store prompt in history: {e}")

                logger.info(
                    f"Successfully generated {template_key} for session {session.id} "
                    f"on attempt {attempt + 1}"
                )

                return ImageResult(
                    image_type=SchemaImageType(template_key),
                    status=SchemaStatus.COMPLETE,
                    storage_path=storage_path,
                )

            except Exception as e:
                last_error = e
                image_record.retry_count = attempt + 1

                logger.warning(
                    f"Generation attempt {attempt + 1} failed for {template_key} "
                    f"(session: {session.id}): {e}"
                )

                # Wait before retry (except on last attempt)
                if attempt < RetryConfig.MAX_RETRIES - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.info(f"Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)

        # All retries exhausted
        logger.error(
            f"All {RetryConfig.MAX_RETRIES} attempts failed for {template_key} "
            f"(session: {session.id}). Last error: {last_error}"
        )

        # Update record with final failure
        image_record.status = GenerationStatusEnum.FAILED
        image_record.error_message = str(last_error)
        self.db.commit()

        return ImageResult(
            image_type=SchemaImageType(template_key),
            status=SchemaStatus.FAILED,
            error_message=str(last_error),
        )

    async def edit_single_image(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        edit_instructions: str,
    ) -> ImageResult:
        """
        Edit an existing generated image with specific instructions.

        Unlike regenerate (which creates NEW images from product photos),
        this MODIFIES the existing generated image based on user instructions.

        Use for:
        - "Change the headline to 'New Text'"
        - "Make the background lighter"
        - "Remove the icon in the corner"
        - "Fill the empty area with the gradient"

        Args:
            session: The generation session
            image_type: Which image to edit
            edit_instructions: What to change

        Returns:
            ImageResult with status and path
        """
        template_key = image_type.value

        # Find the image record
        image_record = None
        for img in session.images:
            if img.image_type == image_type:
                image_record = img
                break

        if not image_record:
            raise ValueError(f"No image record found for type: {image_type}")

        # Validate image exists and is complete
        if image_record.status != GenerationStatusEnum.COMPLETE:
            raise ValueError(f"Cannot edit image - status is {image_record.status.value}, must be 'complete'")

        if not image_record.storage_path:
            raise ValueError("No existing image to edit - storage path is empty")

        # The storage_path is already the full path to the generated image
        existing_image_path = image_record.storage_path

        logger.info(f"Editing {template_key} for session {session.id}")
        logger.info(f"Edit instructions: {edit_instructions[:100]}...")

        # Mark as processing during edit
        original_path = image_record.storage_path  # Save in case we need to revert
        image_record.status = GenerationStatusEnum.PROCESSING
        image_record.error_message = None
        self.db.commit()

        try:
            # Call Gemini to edit the image
            edited_image = await self.gemini.edit_image(
                source_image_path=existing_image_path,
                edit_instructions=edit_instructions,
                aspect_ratio="1:1",
                max_retries=3,
            )

            if edited_image is None:
                raise ValueError("No image returned from Gemini edit API")

            # Save edited image (this will overwrite or create new file)
            storage_path = self.storage.save_generated_image(
                session_id=session.id,
                image_type=template_key,
                image=edited_image,
            )

            # Update record - success!
            image_record.storage_path = storage_path
            image_record.status = GenerationStatusEnum.COMPLETE
            image_record.completed_at = datetime.now(timezone.utc)
            image_record.error_message = None
            self.db.commit()

            logger.info(f"Successfully edited {template_key} for session {session.id}")

            return ImageResult(
                image_type=SchemaImageType(template_key),
                status=SchemaStatus.COMPLETE,
                storage_path=storage_path,
            )

        except Exception as e:
            logger.error(f"Edit failed for {template_key} (session: {session.id}): {e}")

            # Revert to complete status with original path (image still exists)
            image_record.status = GenerationStatusEnum.COMPLETE
            image_record.storage_path = original_path
            image_record.error_message = f"Edit failed: {str(e)}"
            self.db.commit()

            return ImageResult(
                image_type=SchemaImageType(template_key),
                status=SchemaStatus.FAILED,
                storage_path=original_path,  # Return original path so UI still shows image
                error_message=str(e),
            )

    async def generate_all_images(
        self,
        session: GenerationSession,
    ) -> List[ImageResult]:
        """
        Generate all 5 image types for a session.

        Args:
            session: The generation session

        Returns:
            List of ImageResult for each type
        """
        # Load design framework from session if available
        if session.design_framework_json and not self._current_framework:
            try:
                self._current_framework = DesignFramework(**session.design_framework_json)
                logger.info(f"Loaded MASTER level framework from session: {self._current_framework.framework_name}")
            except Exception as e:
                logger.warning(f"Failed to load design framework from session: {e}")

        # Update session status
        session.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        logger.info(f"Starting SEQUENTIAL generation of all 5 images for session {session.id}")

        # Generate all 5 images SEQUENTIALLY (one at a time)
        # This allows the frontend to show progress as each image completes
        results = []
        for i, image_type in enumerate(self.IMAGE_TYPES):
            logger.info(f"Generating image {i+1}/5: {image_type.value}")
            result = await self.generate_single_image(session, image_type)
            results.append(result)
            # Commit after each image so frontend can poll and see progress
            self.db.commit()
            logger.info(f"Completed image {i+1}/5: {image_type.value} - status: {result.status}")

        logger.info(f"All 5 images generated sequentially for session {session.id}")

        # Update session status based on results
        complete_count = sum(1 for r in results if r.status == SchemaStatus.COMPLETE)
        total_count = len(results)

        if complete_count == total_count:
            session.status = GenerationStatusEnum.COMPLETE
        elif complete_count > 0:
            session.status = GenerationStatusEnum.PARTIAL
        else:
            session.status = GenerationStatusEnum.FAILED

        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info(
            f"Session {session.id} completed with status: {session.status.value} "
            f"({complete_count}/{total_count} images successful)"
        )

        return results

    async def retry_failed_images(
        self,
        session: GenerationSession,
    ) -> List[ImageResult]:
        """
        Retry generation of failed images only - IN PARALLEL.

        Args:
            session: The generation session

        Returns:
            List of ImageResult for retried images
        """
        # Collect failed images to retry
        failed_image_types = []
        for img in session.images:
            if img.status == GenerationStatusEnum.FAILED:
                # Reset status for retry
                img.status = GenerationStatusEnum.PENDING
                img.error_message = None
                failed_image_types.append(img.image_type)

        self.db.commit()

        if not failed_image_types:
            return []

        logger.info(f"Retrying {len(failed_image_types)} failed images in PARALLEL")

        # Retry all failed images in parallel
        results = await asyncio.gather(
            *[self.generate_single_image(session, image_type) for image_type in failed_image_types]
        )

        # Update session status
        self._update_session_status(session)

        return results

    def _update_session_status(self, session: GenerationSession) -> None:
        """Update session status based on image statuses"""
        statuses = [img.status for img in session.images]

        if all(s == GenerationStatusEnum.COMPLETE for s in statuses):
            session.status = GenerationStatusEnum.COMPLETE
        elif any(s == GenerationStatusEnum.COMPLETE for s in statuses):
            session.status = GenerationStatusEnum.PARTIAL
        elif any(s == GenerationStatusEnum.PROCESSING for s in statuses):
            session.status = GenerationStatusEnum.PROCESSING
        elif any(s == GenerationStatusEnum.PENDING for s in statuses):
            session.status = GenerationStatusEnum.PENDING
        else:
            session.status = GenerationStatusEnum.FAILED

        self.db.commit()

    def get_session_status(self, session_id: str) -> Optional[GenerationSession]:
        """Get a session by ID"""
        return self.db.query(GenerationSession).filter(
            GenerationSession.id == session_id
        ).first()

    def get_session_results(self, session: GenerationSession) -> List[ImageResult]:
        """Get image results for a session"""
        results = []
        for img in session.images:
            results.append(ImageResult(
                image_type=SchemaImageType(img.image_type.value),
                status=SchemaStatus(img.status.value),
                storage_path=img.storage_path,
                error_message=img.error_message,
            ))
        return results

    def get_generation_stats(self, session: GenerationSession) -> Dict:
        """Get statistics about a generation session"""
        statuses = {}
        for status in GenerationStatusEnum:
            statuses[status.value] = sum(
                1 for img in session.images if img.status == status
            )

        return {
            "session_id": session.id,
            "total_images": len(session.images),
            "by_status": statuses,
            "retry_counts": {
                img.image_type.value: img.retry_count
                for img in session.images
            }
        }

    def create_preview_session(self, request: StylePreviewRequest, user_id: Optional[str] = None) -> GenerationSession:
        """
        Create a session for style preview generation.

        Args:
            request: Style preview request with product details
            user_id: Optional Supabase user ID (from authenticated request)

        Returns:
            Created GenerationSession object
        """
        session = GenerationSession(
            user_id=user_id,  # Associate with authenticated user
            upload_path=request.upload_path,
            product_title=request.product_title,
            feature_1=request.feature_1,
            brand_colors=request.brand_colors or [],
            logo_path=request.logo_path,
            style_reference_path=request.style_reference_path,
            color_count=request.color_count,
            color_palette=request.color_palette or [],
            status=GenerationStatusEnum.PENDING,
        )
        self.db.add(session)
        self.db.flush()

        # Create image records for each style preview
        for style_id in request.style_ids:
            image_record = ImageRecord(
                session_id=session.id,
                image_type=ImageTypeEnum.STYLE_PREVIEW,
                style_id=style_id,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)

        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Created style preview session: {session.id}")
        return session

    async def generate_style_preview(
        self,
        session: GenerationSession,
        style_id: str,
    ) -> StylePreviewResult:
        """
        Generate a single style preview image.

        Args:
            session: The generation session
            style_id: Which style to preview

        Returns:
            StylePreviewResult with status and image URL
        """
        from app.prompts import get_style_preset

        style = get_style_preset(style_id)
        if not style:
            return StylePreviewResult(
                style_id=style_id,
                style_name="Unknown",
                status=SchemaStatus.FAILED,
                error_message=f"Unknown style: {style_id}"
            )

        # Find the image record for this style
        image_record = None
        for img in session.images:
            if img.image_type == ImageTypeEnum.STYLE_PREVIEW and img.style_id == style_id:
                image_record = img
                break

        if not image_record:
            # Create one if it doesn't exist
            image_record = ImageRecord(
                session_id=session.id,
                image_type=ImageTypeEnum.STYLE_PREVIEW,
                style_id=style_id,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)
            self.db.commit()

        # Update status to processing
        image_record.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        # Build context with style override
        context = self._build_product_context(session, style_override=style_id)
        prompt = self.prompt_engine.build_style_preview_prompt(context, style_id)

        try:
            logger.info(f"Generating style preview for {style_id} (session: {session.id})")

            # Build reference paths for style preview
            # Include product image and style reference (if provided)
            # No logo for style previews - that's for final generation
            reference_paths = [session.upload_path]
            if session.style_reference_path:
                reference_paths.append(session.style_reference_path)

            generated_image = await self.gemini.generate_image(
                prompt=prompt,
                reference_image_paths=reference_paths,
                aspect_ratio="1:1",
                max_retries=2,
            )

            if generated_image is None:
                raise ValueError("No image returned from Gemini API")

            # Save to storage
            storage_path = self.storage.save_generated_image(
                session_id=session.id,
                image_type=f"style_preview_{style_id}",
                image=generated_image,
            )

            # Update record
            image_record.storage_path = storage_path
            image_record.status = GenerationStatusEnum.COMPLETE
            image_record.completed_at = datetime.now(timezone.utc)
            self.db.commit()

            logger.info(f"Successfully generated style preview for {style_id}")

            return StylePreviewResult(
                style_id=style_id,
                style_name=style.name,
                status=SchemaStatus.COMPLETE,
                image_url=f"/api/images/{session.id}/style_preview_{style_id}",
            )

        except Exception as e:
            logger.error(f"Style preview generation failed for {style_id}: {e}")

            image_record.status = GenerationStatusEnum.FAILED
            image_record.error_message = str(e)
            self.db.commit()

            return StylePreviewResult(
                style_id=style_id,
                style_name=style.name,
                status=SchemaStatus.FAILED,
                error_message=str(e),
            )

    async def generate_all_style_previews(
        self,
        session: GenerationSession,
        style_ids: List[str],
    ) -> List[StylePreviewResult]:
        """
        Generate preview images for multiple styles.

        Args:
            session: The generation session
            style_ids: List of style IDs to preview

        Returns:
            List of StylePreviewResult for each style
        """
        session.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        logger.info(f"Generating {len(style_ids)} style previews in PARALLEL")

        # Generate all style previews in parallel
        results = await asyncio.gather(
            *[self.generate_style_preview(session, style_id) for style_id in style_ids]
        )

        logger.info(f"All {len(style_ids)} style previews generated")

        # Update session status
        complete_count = sum(1 for r in results if r.status == SchemaStatus.COMPLETE)
        if complete_count == len(results):
            session.status = GenerationStatusEnum.COMPLETE
        elif complete_count > 0:
            session.status = GenerationStatusEnum.PARTIAL
        else:
            session.status = GenerationStatusEnum.FAILED

        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        return results

    def select_style(self, session_id: str, style_id: str) -> Optional[GenerationSession]:
        """
        Set the selected style for a session.

        Args:
            session_id: The session ID
            style_id: The selected style ID

        Returns:
            Updated session or None if not found
        """
        session = self.get_session_status(session_id)
        if not session:
            return None

        session.style_id = style_id
        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Selected style {style_id} for session {session_id}")
        return session
