# Listing Genie - Project Brief

**Document Version:** 1.0
**Date:** December 20, 2024
**Status:** Draft
**Author:** Mary (Business Analyst)

---

## 1. Executive Summary

Listing Genie is an AI-powered Amazon listing image generator that transforms a single product photo and basic product information into a complete set of professional, high-conversion listing images in minutes rather than days.

The platform targets solo Amazon FBA sellers and marketing agencies who currently spend $50-200 and 3-5 days per listing on professional photography and design. Listing Genie reduces this to approximately $15 and 5 minutes while maintaining quality standards aligned with proven Amazon conversion frameworks.

**MVP Deliverable:** An internal web application that accepts a product photo, product details, and keywords, then generates 5 optimized listing images aligned with keyword intent, ready for Amazon upload.

**Note:** Payment integration deferred to Phase 2. Current version is for internal team use.

---

## 2. Problem Statement

### The Core Problem

Amazon sellers face a critical bottleneck in their product launch workflow: creating professional listing images that convert browsers into buyers.

### Current Pain Points

| Pain Point | Current State | Impact |
|------------|---------------|--------|
| **Time** | 3-5 days minimum turnaround | Delays product launches, missed seasonal windows |
| **Cost** | $50-200 per listing | Unsustainable for sellers with 20+ SKUs |
| **Quality Variance** | Dependent on individual designers | Inconsistent brand presentation |
| **Iteration Speed** | Days for revisions | Unable to A/B test quickly |
| **Amazon Compliance** | Manual checking required | Risk of listing rejection |

### Why This Problem Persists

1. Professional product photography requires specialized equipment and skills
2. Graphic designers unfamiliar with Amazon's specific requirements
3. No turnkey solution exists for "Amazon-optimized" image generation
4. AI image tools (Midjourney, DALL-E) lack Amazon-specific training and workflows

---

## 3. Target Users & Personas

### Primary Persona: Solo FBA Seller

**Name:** Marcus
**Profile:** 32-year-old entrepreneur running a private label brand
**SKU Count:** 15-30 active products
**Technical Skill:** Moderate (comfortable with web apps, not design tools)

**Goals:**
- Launch new products faster than competitors
- Maintain professional brand appearance
- Minimize per-product costs to protect margins

**Frustrations:**
- Spending $2,000-4,000 annually on listing images alone
- Waiting weeks for designers during peak seasons
- Explaining Amazon requirements to every new designer

**Quote:** "I just need images that look professional and convert. I don't have time to become a Photoshop expert."

### Secondary Persona: Amazon Marketing Agency

**Name:** Sarah
**Profile:** Founder of a 5-person Amazon brand management agency
**Client Count:** 8-12 brands under management
**Technical Skill:** High (power user of multiple SaaS tools)

**Goals:**
- Deliver faster turnaround to clients
- Standardize quality across all client brands
- Improve margins on listing creation services

**Frustrations:**
- Designer bottlenecks limiting client capacity
- Inconsistent quality from freelance designers
- Difficulty scaling operations

**Quote:** "If I could generate first-draft images instantly, my designers could focus on refinement instead of creation."

---

## 4. Value Proposition

### Primary Value Statement

> Listing Genie transforms your product photo into 5 Amazon-optimized listing images in 5 minutes for $9.99 - replacing the $200 and 5-day wait for traditional design services.

### Value Pillars

| Dimension | Traditional Approach | Listing Genie | Improvement |
|-----------|---------------------|---------------|-------------|
| **Time** | 3-5 days | 5 minutes | 99%+ faster |
| **Cost** | $50-200/listing | $9.99/listing | 80-95% savings |
| **Consistency** | Variable | AI-standardized | Predictable quality |
| **Compliance** | Manual verification | Built-in rules | Reduced rejection risk |
| **Iteration** | Days per revision | Minutes per generation | Rapid A/B testing |

### Unique Differentiators

1. **Amazon-Specific Optimization:** Trained on high-conversion Amazon listing patterns, not generic product photography
2. **Complete Suite Generation:** Produces a cohesive set of images, not individual assets
3. **Conversion-Focused:** Built around proven frameworks (infographics, lifestyle, comparison charts)
4. **Instant Turnaround:** Enables same-day product launches

---

## 5. MVP Scope & Features

### In Scope (Phase 1)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Product Photo Upload** | Single image upload with format validation | Must Have |
| **Product Info Form** | Title, 3 key features, target audience fields | Must Have |
| **5-Image Generation** | Main + 4 supporting listing images | Must Have |
| **Gallery View** | Preview generated images before download | Must Have |
| **Individual Download** | Download single images as PNG/JPG | Must Have |
| **Bulk Download** | Download all 5 as ZIP archive | Must Have |
| **Stripe Payment** | $9.99 per listing, pay-per-use | Must Have |
| **Generation History** | View past generations (logged-in users) | Should Have |

### Image Types Generated (MVP)

1. **Main Image** - Dynamic composition with premium textures, ingredient pops, stacking
2. **Infographic 1** - Large bold text highlighting key benefit #1
3. **Infographic 2** - Large bold text highlighting key benefit #2
4. **Lifestyle Image** - Instagram-style authentic photography feel
5. **Comparison Chart** - Visual check vs. X format with color contrast

### Out of Scope (Phase 2+)

- A+ Content / Brand Story images (5 additional images)
- Multiple product photo uploads
- Brand style customization
- Subscription pricing tiers
- White-label / API access for agencies
- Video generation or motion stills
- Multi-language support
- Direct Amazon Seller Central integration

---

## 6. Success Metrics

### Launch Success Criteria (First 90 Days)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Listings Generated** | 500+ | Database count |
| **Paying Customers** | 100+ unique | Stripe dashboard |
| **Revenue** | $5,000+ | Stripe dashboard |
| **Generation Success Rate** | >95% | Error logs / completions |
| **Average Generation Time** | <3 minutes | Application metrics |

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Customer Satisfaction** | >4.0/5 stars | Post-generation survey |
| **Regeneration Rate** | <30% | Users generating twice for same product |
| **Support Tickets** | <5% of transactions | Help desk volume |

### Business Health Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Gross Margin** | >70% | API cost ~$1.50-2.50, price $9.99 |
| **Customer Acquisition Cost** | <$20 | Target 2-month payback |
| **Repeat Usage Rate** | >40% | Users return within 30 days |

---

## 7. Key Risks & Mitigations

### High Priority Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Amazon Compliance Rejection** | Medium | High | Implement white background detection, text density checks, build compliance rules into prompts |
| **AI Output Quality Variance** | High | High | Develop robust prompt templates, implement quality scoring before display, offer free regeneration |
| **Prompt Engineering Dependency** | High | Critical | Document prompts as core IP, version control all templates, A/B test systematically |

### Medium Priority Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Brand Inconsistency Across Batch** | Medium | Medium | Include style consistency parameters in prompts, use seed values for coherence |
| **API Cost Increases** | Low | High | Monitor Gemini pricing, architect for model swappability, maintain margin buffer |
| **Competitor Entry** | Medium | Medium | Move fast, build brand, focus on Amazon specialization moat |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Gemini API Rate Limits** | Low | Medium | Implement queuing system, graceful degradation messaging |
| **Image Generation Failures** | Medium | Medium | Retry logic, clear error messaging, automatic refund triggers |
| **Slow Generation Times** | Medium | Low | Async processing with status updates, set proper expectations |

---

## 8. Business Model

### Revenue Model

**Phase 1: Pay-Per-Use**
- $9.99 per listing (5 images)
- No subscription required
- Target margin: 70-80% after API costs

**Cost Structure (Per Listing)**
| Component | Cost | Notes |
|-----------|------|-------|
| Gemini API | $1.34-2.40 | 5 images @ $0.13-0.24 each |
| Stripe Fees | $0.59 | 2.9% + $0.30 |
| Infrastructure | ~$0.10 | Railway/Render per-request |
| **Total COGS** | ~$2.00-3.10 | |
| **Gross Profit** | ~$6.90-8.00 | 69-80% margin |

### Future Revenue Opportunities (Phase 2+)

1. **Subscription Tiers**
   - Starter: $49/month (10 listings)
   - Pro: $149/month (50 listings)
   - Agency: $499/month (200 listings + API access)

2. **A+ Content Add-on**
   - Additional $14.99 for 5 Brand Story images

3. **White-Label Licensing**
   - Agency white-label for custom pricing

---

## 9. Competitive Analysis

### Direct Competitors

**None identified** - No existing solution provides automated, Amazon-optimized listing image suite generation.

### Indirect Competitors

| Competitor | Offering | Strengths | Weaknesses | Price Point |
|------------|----------|-----------|------------|-------------|
| **Canva** | Template-based design | Flexible, known brand | Manual work, no Amazon optimization | $13/month |
| **Fiverr Designers** | Custom design services | Human creativity, revisions | Slow (3-7 days), inconsistent quality | $50-200/listing |
| **Midjourney** | AI image generation | High quality output | No Amazon focus, requires prompt skill | $10-60/month |
| **ProductScope AI** | AI background removal | Quick, Amazon-focused | Only backgrounds, not full suites | $29/month |

### Competitive Positioning

```
                    SPECIALIZED (Amazon-Focused)
                              ^
                              |
                   ProductScope    [LISTING GENIE]
                              |
    MANUAL <------------------+-------------------> AUTOMATED
                              |
                    Fiverr        Midjourney
                    Canva              |
                              |
                    GENERAL PURPOSE
```

### Sustainable Competitive Advantages

1. **First-Mover in Niche:** No direct competitor in AI-powered Amazon listing suites
2. **Prompt Engineering IP:** Accumulating know-how on Amazon-converting prompts
3. **Feedback Loop:** Each generation improves system understanding
4. **Switching Cost:** Users build workflow around the tool

---

## 10. Technical Constraints

### Platform Requirements

| Requirement | Specification | Rationale |
|-------------|---------------|-----------|
| **Architecture** | FastAPI + Static React (single container) | Simplified deployment, reduced DevOps |
| **AI Provider** | Gemini 3 Pro Image Preview | Best price/quality for image generation |
| **SDK** | google-genai Python SDK | Official Google SDK |
| **Deployment** | Railway / Render / AWS Lightsail | Single container hosting, simple scaling |
| **Payment** | Stripe Checkout | Industry standard, fast integration |

### Performance Requirements

| Metric | Requirement | Notes |
|--------|-------------|-------|
| **Image Generation Time** | <60 seconds per image | User expectation benchmark |
| **Total Listing Time** | <5 minutes | Including upload, payment, download |
| **Concurrent Users** | 20+ simultaneous | Initial scale target |
| **Image Resolution** | 2000x2000px minimum | Amazon HD requirement |

### Integration Requirements

| System | Integration Type | Priority |
|--------|-----------------|----------|
| **Gemini API** | REST via SDK | Critical |
| **Stripe** | Checkout Sessions | Critical |
| **Cloud Storage** | Generated image storage | High |
| **Analytics** | Usage tracking | Medium |

### Compliance Requirements

| Requirement | Specification |
|-------------|---------------|
| **Image Format** | JPEG or PNG, RGB color mode |
| **Main Image Background** | Pure white (#FFFFFF) or transparent |
| **File Size** | <10MB per image |
| **Aspect Ratio** | 1:1 (square) for main, flexible for supporting |
| **Text Density** | <20% of image area (Amazon guideline) |

---

## Appendix A: Amazon Image Requirements Summary

### Main Image Requirements
- Pure white background (RGB 255, 255, 255)
- Product fills 85%+ of frame
- No text, logos, or watermarks
- Professional lighting and shadows
- No lifestyle elements or props

### Supporting Image Guidelines
- Can include text (but limited)
- Lifestyle contexts allowed
- Infographics encouraged
- Comparison charts effective
- Must be high resolution (1000px+ on longest side)

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **FBA** | Fulfillment by Amazon - Amazon's warehousing and shipping service |
| **SKU** | Stock Keeping Unit - unique product identifier |
| **A+ Content** | Enhanced brand content section on Amazon product pages |
| **Listing Images** | The main product photos shown in Amazon search and product pages |
| **Private Label** | Products manufactured by third party but sold under seller's brand |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | Mary (BA) | Initial draft |

---

*This document serves as the foundational brief for Listing Genie development. All subsequent PRD, architecture, and design documents should reference and align with the scope and constraints defined herein.*
