"""
Tests for Prompt Engineering System
"""
import pytest
from app.prompts import (
    PromptEngine,
    ProductContext,
    get_prompt_engine,
    get_intent_modifiers,
    get_color_guidance,
    infer_category,
)


# Test fixtures
@pytest.fixture
def sample_context():
    """Sample product context for testing"""
    return ProductContext(
        title="Organic Vitamin D3 Gummies - Natural Immune Support",
        features=[
            "5000 IU Vitamin D3 per serving",
            "Organic, non-GMO ingredients",
            "Great-tasting natural berry flavor"
        ],
        target_audience="Health-conscious adults 30-55",
        keywords=["vitamin d gummies", "immune support", "organic vitamins"],
        intents={
            "vitamin d gummies": ["durability", "style"],
            "immune support": ["problem_solution", "use_case"],
            "organic vitamins": ["style"]
        }
    )


@pytest.fixture
def fitness_context():
    """Fitness product context for testing"""
    return ProductContext(
        title="Pro Resistance Bands Set - Heavy Duty Workout Kit",
        features=[
            "Military-grade latex construction",
            "5 resistance levels (5-150 lbs)",
            "Complete home gym replacement"
        ],
        target_audience="Fitness enthusiasts 25-45",
        keywords=["resistance bands", "workout bands", "home gym"],
        intents={
            "resistance bands": ["durability", "comparison"],
            "workout bands": ["use_case"],
            "home gym": ["problem_solution"]
        }
    )


@pytest.fixture
def prompt_engine():
    """Get prompt engine instance"""
    return get_prompt_engine()


class TestPromptEngine:
    """Tests for PromptEngine class"""

    def test_engine_singleton(self):
        """Test that get_prompt_engine returns singleton"""
        engine1 = get_prompt_engine()
        engine2 = get_prompt_engine()
        assert engine1 is engine2

    def test_engine_has_all_templates(self, prompt_engine):
        """Test that engine has all 5 image type templates"""
        expected_types = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison']
        for image_type in expected_types:
            assert image_type in prompt_engine.templates

    def test_build_main_prompt(self, prompt_engine, sample_context):
        """Test main image prompt generation"""
        prompt = prompt_engine.build_prompt('main', sample_context)

        assert sample_context.title in prompt
        assert sample_context.features[0] in prompt
        assert sample_context.target_audience in prompt
        assert "white background" in prompt.lower()
        assert "2000x2000" in prompt

    def test_build_infographic_1_prompt(self, prompt_engine, sample_context):
        """Test infographic 1 prompt includes color guidance"""
        prompt = prompt_engine.build_prompt('infographic_1', sample_context)

        assert sample_context.title in prompt
        assert sample_context.features[0] in prompt
        assert "COLOR PSYCHOLOGY" in prompt
        assert "headline" in prompt.lower()

    def test_build_infographic_2_prompt(self, prompt_engine, sample_context):
        """Test infographic 2 prompt generation"""
        prompt = prompt_engine.build_prompt('infographic_2', sample_context)

        assert sample_context.title in prompt
        assert sample_context.features[1] in prompt
        assert "COLOR PSYCHOLOGY" in prompt

    def test_build_lifestyle_prompt(self, prompt_engine, sample_context):
        """Test lifestyle prompt generation"""
        prompt = prompt_engine.build_prompt('lifestyle', sample_context)

        assert sample_context.title in prompt
        assert sample_context.target_audience in prompt
        assert "COLOR PSYCHOLOGY" in prompt
        assert "lifestyle" in prompt.lower() or "instagram" in prompt.lower()

    def test_build_comparison_prompt(self, prompt_engine, sample_context):
        """Test comparison chart prompt generation"""
        prompt = prompt_engine.build_prompt('comparison', sample_context)

        assert sample_context.title in prompt
        # Comparison uses features 2 and 3
        assert "Them" in prompt or "competitor" in prompt.lower()
        assert "checkmarks" in prompt.lower() or "green" in prompt.lower()

    def test_build_all_prompts(self, prompt_engine, sample_context):
        """Test building all prompts at once"""
        prompts = prompt_engine.build_all_prompts(sample_context)

        assert len(prompts) == 5
        assert 'main' in prompts
        assert 'infographic_1' in prompts
        assert 'infographic_2' in prompts
        assert 'lifestyle' in prompts
        assert 'comparison' in prompts

        for image_type, prompt in prompts.items():
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Prompts should be substantial

    def test_prompts_contain_intent_modifiers(self, prompt_engine, fitness_context):
        """Test that prompts include intent modifiers"""
        # Fitness context has durability intent which should show in main image
        prompt = prompt_engine.build_prompt('main', fitness_context)
        # Main image prioritizes durability and style
        assert "DURABILITY INTENT" in prompt or "STYLE INTENT" in prompt or "professional" in prompt.lower()

    def test_short_features_list_handled(self, prompt_engine):
        """Test handling of less than 3 features"""
        context = ProductContext(
            title="Simple Product",
            features=["Only one feature"],
            target_audience="Everyone",
            keywords=["product"],
            intents={}
        )
        # Should not raise an error
        prompt = prompt_engine.build_prompt('main', context)
        assert "Simple Product" in prompt


class TestIntentModifiers:
    """Tests for intent modifier system"""

    def test_get_intent_modifiers_durability(self):
        """Test durability intent modifiers for main image"""
        intents = {"keyword1": ["durability"]}
        modifiers = get_intent_modifiers('main', intents)

        assert "DURABILITY INTENT" in modifiers
        assert "premium materials" in modifiers.lower() or "quality" in modifiers.lower()

    def test_get_intent_modifiers_use_case(self):
        """Test use_case intent modifiers for lifestyle"""
        intents = {"keyword1": ["use_case"]}
        modifiers = get_intent_modifiers('lifestyle', intents)

        assert "USE_CASE INTENT" in modifiers
        assert "context" in modifiers.lower() or "scenario" in modifiers.lower()

    def test_get_intent_modifiers_problem_solution(self):
        """Test problem_solution intent for infographic"""
        intents = {"keyword1": ["problem_solution"]}
        modifiers = get_intent_modifiers('infographic_1', intents)

        assert "PROBLEM_SOLUTION INTENT" in modifiers

    def test_get_intent_modifiers_comparison(self):
        """Test comparison intent for comparison chart"""
        intents = {"keyword1": ["comparison"]}
        modifiers = get_intent_modifiers('comparison', intents)

        assert "COMPARISON INTENT" in modifiers
        assert "superiority" in modifiers.lower() or "premium" in modifiers.lower()

    def test_empty_intents_fallback(self):
        """Test fallback when no matching intents"""
        modifiers = get_intent_modifiers('main', {})
        assert "professional" in modifiers.lower()

    def test_multiple_intents_combined(self):
        """Test combining multiple intents"""
        intents = {
            "keyword1": ["durability", "style"],
            "keyword2": ["use_case"]
        }
        modifiers = get_intent_modifiers('main', intents)
        # Main prioritizes durability and style
        assert "DURABILITY INTENT" in modifiers or "STYLE INTENT" in modifiers


class TestColorPsychology:
    """Tests for color psychology system"""

    def test_infer_health_supplements_category(self):
        """Test category inference for health products"""
        category = infer_category(
            "Organic Vitamin D3 Gummies",
            ["vitamin", "supplement", "organic"]
        )
        assert category == "health_supplements"

    def test_infer_fitness_category(self):
        """Test category inference for fitness products"""
        category = infer_category(
            "Pro Workout Resistance Bands",
            ["gym", "fitness", "exercise"]
        )
        assert category == "fitness"

    def test_infer_baby_category(self):
        """Test category inference for baby products"""
        category = infer_category(
            "Soft Baby Blanket",
            ["baby", "nursery", "infant"]
        )
        assert category == "baby_kids"

    def test_infer_tech_category(self):
        """Test category inference for tech products"""
        category = infer_category(
            "Wireless Bluetooth Earbuds",
            ["tech", "electronic", "wireless"]
        )
        assert category == "tech_electronics"

    def test_infer_default_category(self):
        """Test default category for unknown products"""
        category = infer_category(
            "Generic Item",
            ["random", "stuff"]
        )
        assert category == "default"

    def test_get_color_guidance_health(self):
        """Test color guidance for health category"""
        guidance = get_color_guidance("health_supplements")

        assert "COLOR PSYCHOLOGY" in guidance
        assert "green" in guidance.lower()
        assert "natural" in guidance.lower() or "organic" in guidance.lower()

    def test_get_color_guidance_fitness(self):
        """Test color guidance for fitness category"""
        guidance = get_color_guidance("fitness")

        assert "COLOR PSYCHOLOGY" in guidance
        assert "energetic" in guidance.lower() or "powerful" in guidance.lower()

    def test_get_color_guidance_default(self):
        """Test default color guidance"""
        guidance = get_color_guidance("unknown_category")

        assert "COLOR PSYCHOLOGY" in guidance
        assert "professional" in guidance.lower()


class TestProductContext:
    """Tests for ProductContext dataclass"""

    def test_context_creation(self):
        """Test ProductContext creation"""
        context = ProductContext(
            title="Test Product",
            features=["Feature 1", "Feature 2", "Feature 3"],
            target_audience="Test Audience",
            keywords=["keyword1", "keyword2"],
            intents={"keyword1": ["durability"]}
        )

        assert context.title == "Test Product"
        assert len(context.features) == 3
        assert context.target_audience == "Test Audience"
        assert len(context.keywords) == 2
        assert "keyword1" in context.intents

    def test_context_with_empty_intents(self):
        """Test ProductContext with empty intents"""
        context = ProductContext(
            title="Simple Product",
            features=["Feature"],
            target_audience="Everyone",
            keywords=[],
            intents={}
        )

        assert context.intents == {}
