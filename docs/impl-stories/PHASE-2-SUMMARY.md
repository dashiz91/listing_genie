# Phase 2 (AI Core) Implementation Stories - Summary

**Created:** December 20, 2024
**Total Stories:** 8
**Status:** Ready for Implementation

---

## Overview

Phase 2 focuses on the **AI Core** - integrating with the Gemini API and implementing the prompt engineering system that generates high-conversion Amazon listing images.

---

## Story Files

### Core Integration

1. **2.1-gemini-api.md** - Gemini API Integration
   - Connect to Gemini API using google-genai SDK
   - GeminiService class with reference image support
   - Health check endpoints
   - **Test:** Generate 1 test image

2. **2.2-prompt-templates.md** - Prompt Template System
   - Complete prompt engineering system
   - 5 template files (main, infographic x2, lifestyle, comparison)
   - Intent modifiers and color psychology
   - PromptEngine class
   - **Test:** Templates load and populate

### Image Generation

3. **2.3-main-image-gen.md** - Main Image Generation
   - Dynamic composition with white background
   - Product fills 85% of frame
   - **Test:** Generate main image from test product

4. **2.4-infographic-gen.md** - Infographic Generation (2 images)
   - Bold text, benefit-focused messaging
   - <20% text density
   - **Test:** Generate both infographics

5. **2.5-lifestyle-gen.md** - Lifestyle Image Generation
   - Instagram-style aesthetic
   - Product in realistic usage context
   - **Test:** Generate lifestyle image

6. **2.6-comparison-gen.md** - Comparison Chart Generation
   - Check vs X format
   - Color psychology (green vs red/grey)
   - **Test:** Generate comparison chart

### Reliability & Storage

7. **2.7-error-retry.md** - Error Handling & Retry Logic
   - Max 3 retries with exponential backoff
   - Prompt variations on retry
   - Comprehensive error logging
   - **Test:** Mock failure, verify retry

8. **2.8-image-storage.md** - Image Storage
   - Local filesystem storage (MVP)
   - Organized by session ID
   - Security: UUID filenames, EXIF stripping
   - **Test:** Images save and retrieve correctly

---

## Implementation Order

**Recommended sequence:**

1. **Story 2.1** (Gemini API) - Foundation
2. **Story 2.2** (Prompt Templates) - Core IP
3. **Story 2.8** (Image Storage) - Required by all generation
4. **Story 2.3** (Main Image) - Most important image
5. **Story 2.4** (Infographics) - Secondary images
6. **Story 2.5** (Lifestyle) - Emotional connection
7. **Story 2.6** (Comparison) - Final convincer
8. **Story 2.7** (Error/Retry) - Production hardening

---

## Key Features

### Creative Blueprint Compliance

All prompts implement guidelines from `docs/creative-blueprint.md`:

- **Main Image:** Dynamic composition, stacking, ingredient pop
- **Infographics:** Benefit-focused, bold text, design elements
- **Lifestyle:** Instagram aesthetic, authentic settings
- **Comparison:** Check vs X, color psychology

### Reference Implementation

Code examples based on:
- `docs/architecture.md` (Sections 5-6)
- `gemini_mcp/src/tools/image_generator.py`
- `docs/prd.md` (Stories 2.1-2.7)

### Testing Requirements

Each story includes:
- Full code implementation
- Test file with pytest examples
- Manual testing instructions
- Success criteria

---

## Dependencies

### External Dependencies

```txt
google-genai>=0.1.0
pillow>=10.0.0
python-dotenv>=1.0.0
```

### Story Dependencies

```
2.1 (Gemini API)
 └─> 2.2 (Prompt Templates)
      ├─> 2.3 (Main Image)
      ├─> 2.4 (Infographics)
      ├─> 2.5 (Lifestyle)
      └─> 2.6 (Comparison)
           └─> 2.7 (Error/Retry)
                └─> 2.8 (Image Storage)
```

---

## Environment Variables Required

```bash
# .env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-3-pro-image-preview
STORAGE_PATH=./storage
```

---

## Testing Phase 2

### Run All Tests

```bash
# Individual story tests
pytest tests/test_gemini_connection.py -v
pytest tests/test_prompt_templates.py -v
pytest tests/test_main_image_generation.py -v
pytest tests/test_infographic_generation.py -v
pytest tests/test_lifestyle_generation.py -v
pytest tests/test_comparison_generation.py -v
pytest tests/test_error_retry.py -v
pytest tests/test_storage_service.py -v

# Run all Phase 2 tests
pytest tests/test_*.py -v -s
```

### Verification Checklist

- [ ] Gemini API connects successfully
- [ ] All 5 template types load correctly
- [ ] Main image generates with white background
- [ ] Both infographics generate with different features
- [ ] Lifestyle image has authentic feel
- [ ] Comparison chart shows clear winner
- [ ] Retry logic works on failures
- [ ] Images save to correct directories

---

## Success Criteria

**Phase 2 is complete when:**

1. ✅ All 5 image types generate successfully
2. ✅ Images meet Amazon requirements (2000x2000px, white bg for main)
3. ✅ Prompts follow Creative Blueprint guidelines
4. ✅ Reference images properly incorporated
5. ✅ Error handling works with retry logic
6. ✅ Images stored and retrievable
7. ✅ All tests pass
8. ✅ Code reviewed and documented

---

## Notes

- **Core IP:** Prompt templates (Story 2.2) are the key differentiator
- **Quality:** Image quality directly impacts user satisfaction
- **Reference Images:** Critical for maintaining product accuracy
- **Testing:** Manual inspection of generated images recommended
- **Iteration:** Prompt templates should be easy to improve over time

---

## Next Steps

After Phase 2 completion:
- Move to **Phase 3** (User Interface - Upload & Forms)
- Or move to **Phase 4** (Keyword Intent System)
- Or move to **Phase 5** (Gallery & Download)

See `docs/impl-stories/INDEX.md` for complete project roadmap.
