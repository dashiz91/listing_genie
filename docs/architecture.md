# Listing Genie - Architecture Document

**Document Version:** 1.0
**Date:** December 20, 2024
**Status:** Draft
**Author:** Winston (Architect)
**Reference:** [Project Brief v1.0](./brief.md), [PRD v1.0](./prd.md), [Front-End Spec v1.0](./front-end-spec.md), [Creative Blueprint v1.0](./creative-blueprint.md)

---

## 1. System Overview

### 1.1 Executive Summary

Listing Genie is an AI-powered Amazon listing image generator that transforms a product photo and product details into 5 conversion-optimized listing images. The system is built as a single-container web application with a FastAPI backend serving a static React frontend, integrating with Gemini AI for image generation.

### 1.2 High-Level Architecture

```
                                    LISTING GENIE ARCHITECTURE

    +-----------------------------------------------------------------------------------+
    |                                   INTERNET                                         |
    +-----------------------------------------------------------------------------------+
                                           |
                                           v
    +-----------------------------------------------------------------------------------+
    |                              SINGLE CONTAINER                                      |
    |  +-----------------------------------------------------------------------------+  |
    |  |                            FastAPI Application                               |  |
    |  |  +-------------------+  +-------------------+  +-------------------------+  |  |
    |  |  |   Static Files    |  |   API Router      |  |   Background Tasks      |  |  |
    |  |  |  (React Build)    |  |  /api/*           |  |  (Image Generation)     |  |  |
    |  |  +-------------------+  +-------------------+  +-------------------------+  |  |
    |  |                                                                              |  |
    |  |  +-------------------+  +-------------------+  +-------------------------+  |  |
    |  |  |   Service Layer   |  |   Prompt Engine   |  |   Storage Service       |  |  |
    |  |  +-------------------+  +-------------------+  +-------------------------+  |  |
    |  +-----------------------------------------------------------------------------+  |
    +-----------------------------------------------------------------------------------+
              |                        |                           |
              v                        v                           v
    +------------------+    +------------------+       +----------------------+
    |   SQLite/Postgres |    |    Gemini API    |       |   Local/Cloud        |
    |    Database       |    | (Image Gen)      |       |   Storage            |
    +------------------+    +------------------+       +----------------------+
```

### 1.3 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **FastAPI Application** | HTTP server, API routing, static file serving, request validation |
| **Static Files (React)** | User interface, form handling, image display, client-side state |
| **API Router** | RESTful endpoints for upload, generation, download operations |
| **Background Tasks** | Async image generation, retry logic, status tracking |
| **Service Layer** | Business logic, orchestration between components |
| **Prompt Engine** | Template management, dynamic prompt construction, intent injection |
| **Storage Service** | File operations for uploaded and generated images |
| **Database** | Persistence for sessions, keywords, image metadata |

### 1.4 Data Flow

```
User Request Flow:

    [Browser] --> [FastAPI] --> [Validation] --> [Service Layer] --> [Database]
                      |
                      +--> [Background Task] --> [Prompt Engine] --> [Gemini API]
                                     |
                                     +--> [Storage Service] --> [Generated Images]
                                     |
                                     +--> [Database Update] --> [Status: Complete]

    [Browser] <-- [Gallery API] <-- [Storage Service] <-- [Generated Images]
```

---

## 2. Backend Architecture (FastAPI)

### 2.1 Project Structure

```
listing_genie/
|-- app/
|   |-- __init__.py
|   |-- main.py                    # FastAPI application entry point
|   |-- config.py                  # Configuration and environment variables
|   |-- dependencies.py            # Dependency injection
|   |
|   |-- api/
|   |   |-- __init__.py
|   |   |-- router.py              # Main API router
|   |   |-- endpoints/
|   |   |   |-- __init__.py
|   |   |   |-- upload.py          # Image upload endpoints
|   |   |   |-- generation.py      # Generation trigger and status
|   |   |   |-- download.py        # Image download endpoints
|   |   |   |-- health.py          # Health check endpoints
|   |
|   |-- core/
|   |   |-- __init__.py
|   |   |-- exceptions.py          # Custom exception classes
|   |   |-- logging.py             # Logging configuration
|   |   |-- middleware.py          # Request logging, error handling
|   |
|   |-- models/
|   |   |-- __init__.py
|   |   |-- database.py            # SQLAlchemy models
|   |   |-- schemas.py             # Pydantic request/response models
|   |
|   |-- services/
|   |   |-- __init__.py
|   |   |-- generation_service.py  # Orchestrates image generation
|   |   |-- storage_service.py     # File storage operations
|   |   |-- keyword_service.py     # Keyword classification logic
|   |   |-- gemini_service.py      # Gemini API client wrapper
|   |
|   |-- prompts/
|   |   |-- __init__.py
|   |   |-- engine.py              # Prompt construction engine
|   |   |-- templates/
|   |   |   |-- main_image.py      # Main image prompt template
|   |   |   |-- infographic.py     # Infographic prompt templates
|   |   |   |-- lifestyle.py       # Lifestyle prompt template
|   |   |   |-- comparison.py      # Comparison chart template
|   |   |-- intent_modifiers.py    # Intent-based prompt modifications
|   |
|   |-- tasks/
|   |   |-- __init__.py
|   |   |-- generation_task.py     # Background generation task
|   |   |-- cleanup_task.py        # Storage cleanup task
|   |
|   |-- db/
|   |   |-- __init__.py
|   |   |-- session.py             # Database session management
|   |   |-- migrations/            # Alembic migrations (if needed)
|
|-- frontend/                      # React application (Vite)
|   |-- src/
|   |-- dist/                      # Production build (served by FastAPI)
|   |-- package.json
|   |-- vite.config.js
|
|-- storage/                       # Local file storage (MVP)
|   |-- uploads/                   # Uploaded product images
|   |-- generated/                 # Generated listing images
|
|-- tests/
|   |-- __init__.py
|   |-- conftest.py
|   |-- test_api/
|   |-- test_services/
|   |-- test_prompts/
|
|-- docs/                          # Project documentation
|-- .env.example                   # Environment variable template
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- pyproject.toml
|-- README.md
```

### 2.2 API Endpoints Design

#### Core Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/health` | Health check | - | `{"status": "healthy", "version": "1.0.0"}` |
| `GET` | `/api/health` | API health with DB check | - | `{"status": "healthy", "database": "connected"}` |

#### Upload Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `POST` | `/api/upload` | Upload product image | `multipart/form-data` with `file` | `{"upload_id": "uuid", "preview_url": "/uploads/uuid.jpg"}` |
| `DELETE` | `/api/upload/{upload_id}` | Remove uploaded image | - | `{"success": true}` |

#### Generation Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `POST` | `/api/generate` | Start image generation | See below | `{"session_id": "uuid", "status": "processing"}` |
| `GET` | `/api/generation/{session_id}` | Get generation status | - | `{"status": "...", "images": [...]}` |
| `POST` | `/api/generation/{session_id}/retry` | Retry failed generation | - | `{"status": "retrying"}` |

**POST /api/generate Request Body:**
```json
{
  "upload_id": "uuid-of-uploaded-image",
  "product_info": {
    "title": "Organic Sleep Gummies",
    "features": [
      "All-natural melatonin formula",
      "Non-habit forming",
      "Delicious berry flavor"
    ],
    "target_audience": "Busy professionals seeking better sleep"
  },
  "keywords": [
    "sleep gummies",
    "natural sleep aid",
    "melatonin gummies",
    "better sleep",
    "non-habit forming"
  ]
}
```

#### Download Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/api/images/{session_id}` | Get all image URLs | `{"images": [{"type": "main", "url": "..."}, ...]}` |
| `GET` | `/api/download/{session_id}/{image_type}` | Download single image | `image/png` binary |
| `GET` | `/api/download/{session_id}/zip` | Download all as ZIP | `application/zip` binary |

### 2.3 Service Layer Organization

```python
# services/generation_service.py - Core orchestration

class GenerationService:
    """Orchestrates the complete image generation workflow"""

    def __init__(
        self,
        gemini_service: GeminiService,
        prompt_engine: PromptEngine,
        storage_service: StorageService,
        keyword_service: KeywordService,
        db_session: Session
    ):
        self.gemini = gemini_service
        self.prompts = prompt_engine
        self.storage = storage_service
        self.keywords = keyword_service
        self.db = db_session

    async def start_generation(
        self,
        upload_id: str,
        product_info: ProductInfo,
        keywords: List[str]
    ) -> GenerationSession:
        """Start a new generation session"""
        # 1. Create session in database
        # 2. Classify keywords by intent
        # 3. Queue background generation task
        # 4. Return session with status
        pass

    async def generate_image_batch(
        self,
        session_id: str
    ) -> None:
        """Background task: Generate all 5 images"""
        # 1. Load session and product image
        # 2. For each image type:
        #    a. Build prompt with intent injection
        #    b. Call Gemini API with reference image
        #    c. Save generated image
        #    d. Update session status
        # 3. Mark session complete
        pass
```

### 2.4 Request/Response Schemas

```python
# models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ImageType(str, Enum):
    MAIN = "main"
    INFOGRAPHIC_1 = "infographic_1"
    INFOGRAPHIC_2 = "infographic_2"
    LIFESTYLE = "lifestyle"
    COMPARISON = "comparison"

class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"

class ProductInfo(BaseModel):
    title: str = Field(..., max_length=200)
    features: List[str] = Field(..., min_items=3, max_items=3)
    target_audience: str = Field(..., max_length=150)

    class Config:
        schema_extra = {
            "example": {
                "title": "Organic Sleep Gummies - 60 Count",
                "features": [
                    "All-natural melatonin formula",
                    "Non-habit forming",
                    "Delicious berry flavor"
                ],
                "target_audience": "Busy professionals aged 25-45 seeking natural sleep solutions"
            }
        }

class GenerateRequest(BaseModel):
    upload_id: str
    product_info: ProductInfo
    keywords: List[str] = Field(..., min_items=5, max_items=20)

class ImageStatus(BaseModel):
    type: ImageType
    status: GenerationStatus
    url: Optional[str] = None
    error: Optional[str] = None

class GenerationResponse(BaseModel):
    session_id: str
    status: GenerationStatus
    images: List[ImageStatus]
    created_at: str
    completed_at: Optional[str] = None
```

---

## 3. Frontend Architecture (React)

### 3.1 Component Hierarchy

```
App
|-- Layout
|   |-- Header
|   |-- ProgressIndicator
|   |-- MainContent
|   |-- Footer
|
|-- Pages
|   |-- LandingPage
|   |   |-- HeroSection
|   |   |-- ValuePropositions
|   |   |-- HowItWorks
|   |   |-- CTAButton
|   |
|   |-- UploadStep
|   |   |-- UploadZone
|   |   |-- ImagePreview
|   |   |-- NavigationButtons
|   |
|   |-- FormStep
|   |   |-- ProductInfoForm
|   |   |   |-- TextField (Title)
|   |   |   |-- TextField (Feature 1)
|   |   |   |-- TextField (Feature 2)
|   |   |   |-- TextField (Feature 3)
|   |   |   |-- TextField (Target Audience)
|   |   |-- KeywordInput
|   |   |   |-- KeywordTextArea
|   |   |   |-- KeywordTags
|   |   |   |-- IntentPreview
|   |   |-- NavigationButtons
|   |
|   |-- GenerationStep
|   |   |-- GenerationProgress
|   |   |   |-- ImageProgressItem (x5)
|   |   |-- TimeEstimate
|   |
|   |-- GalleryStep
|       |-- GalleryGrid
|       |   |-- ImageCard (x5)
|       |-- DownloadAllButton
|       |-- ImagePreviewModal
|
|-- Shared Components
    |-- Button
    |-- TextField
    |-- Card
    |-- Modal
    |-- ProgressBar
    |-- LoadingSpinner
    |-- Toast/Notification
    |-- ErrorBoundary
```

### 3.2 State Management Approach

**Pattern:** React Context + useReducer for global state, useState for local component state.

```typescript
// contexts/AppContext.tsx

interface AppState {
  currentStep: 1 | 2 | 3 | 4 | 5;
  uploadId: string | null;
  productImage: {
    file: File | null;
    previewUrl: string | null;
  };
  productInfo: {
    title: string;
    features: [string, string, string];
    targetAudience: string;
  };
  keywords: string[];
  keywordIntents: Record<string, IntentType[]>;
  sessionId: string | null;
  generationStatus: {
    main: ImageGenerationStatus;
    infographic_1: ImageGenerationStatus;
    infographic_2: ImageGenerationStatus;
    lifestyle: ImageGenerationStatus;
    comparison: ImageGenerationStatus;
  };
  generatedImages: {
    main: GeneratedImage | null;
    infographic_1: GeneratedImage | null;
    infographic_2: GeneratedImage | null;
    lifestyle: GeneratedImage | null;
    comparison: GeneratedImage | null;
  };
  error: string | null;
}

type AppAction =
  | { type: 'SET_STEP'; payload: number }
  | { type: 'SET_UPLOAD'; payload: { uploadId: string; previewUrl: string; file: File } }
  | { type: 'CLEAR_UPLOAD' }
  | { type: 'SET_PRODUCT_INFO'; payload: Partial<ProductInfo> }
  | { type: 'SET_KEYWORDS'; payload: string[] }
  | { type: 'SET_KEYWORD_INTENTS'; payload: Record<string, IntentType[]> }
  | { type: 'START_GENERATION'; payload: { sessionId: string } }
  | { type: 'UPDATE_IMAGE_STATUS'; payload: { type: ImageType; status: ImageGenerationStatus } }
  | { type: 'SET_GENERATED_IMAGE'; payload: { type: ImageType; image: GeneratedImage } }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'RESET' };

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.payload };
    // ... other cases
  }
}
```

### 3.3 API Client Design

```typescript
// api/client.ts

import axios, { AxiosInstance } from 'axios';

const API_BASE = '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 60000, // 60 second timeout for generation
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle errors globally
        if (error.response?.status === 500) {
          console.error('Server error:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  // Upload
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Generation
  async startGeneration(request: GenerateRequest): Promise<GenerationResponse> {
    const response = await this.client.post('/generate', request);
    return response.data;
  }

  async getGenerationStatus(sessionId: string): Promise<GenerationResponse> {
    const response = await this.client.get(`/generation/${sessionId}`);
    return response.data;
  }

  // Download
  async downloadImage(sessionId: string, imageType: string): Promise<Blob> {
    const response = await this.client.get(`/download/${sessionId}/${imageType}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async downloadZip(sessionId: string): Promise<Blob> {
    const response = await this.client.get(`/download/${sessionId}/zip`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

### 3.4 Polling Strategy for Generation Status

```typescript
// hooks/useGenerationPolling.ts

import { useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export function useGenerationPolling(
  sessionId: string | null,
  onStatusUpdate: (status: GenerationResponse) => void,
  onComplete: () => void,
  onError: (error: string) => void
) {
  const pollStatus = useCallback(async () => {
    if (!sessionId) return;

    try {
      const status = await apiClient.getGenerationStatus(sessionId);
      onStatusUpdate(status);

      if (status.status === 'complete') {
        onComplete();
        return true; // Stop polling
      }

      if (status.status === 'failed') {
        onError('Generation failed. Please try again.');
        return true; // Stop polling
      }

      return false; // Continue polling
    } catch (error) {
      onError('Connection lost. Checking status...');
      return false; // Retry
    }
  }, [sessionId, onStatusUpdate, onComplete, onError]);

  useEffect(() => {
    if (!sessionId) return;

    let timeoutId: NodeJS.Timeout;
    let pollCount = 0;
    const maxPolls = 120; // 2 minutes at 1 second intervals
    const pollInterval = 1000; // 1 second

    const poll = async () => {
      pollCount++;
      const shouldStop = await pollStatus();

      if (!shouldStop && pollCount < maxPolls) {
        timeoutId = setTimeout(poll, pollInterval);
      } else if (pollCount >= maxPolls) {
        onError('Generation is taking longer than expected. Please refresh to check status.');
      }
    };

    poll();

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [sessionId, pollStatus, onError]);
}
```

---

## 4. Database Schema

### 4.1 Entity Relationship Diagram

```
+--------------------+       +------------------------+       +------------------+
|  GenerationSession |       |     SessionKeyword     |       |    ImageRecord   |
+--------------------+       +------------------------+       +------------------+
| id (PK)            |<---+  | id (PK)                |   +-->| id (PK)          |
| status             |    |  | session_id (FK)        |   |   | session_id (FK)  |
| upload_path        |    +--| keyword                |   |   | image_type       |
| product_title      |       | intent_types (JSON)    |   |   | storage_path     |
| feature_1          |       | created_at             |   |   | status           |
| feature_2          |       +------------------------+   |   | error_message    |
| feature_3          |                                    |   | retry_count      |
| target_audience    |                                    |   | created_at       |
| created_at         |                                    |   | completed_at     |
| completed_at       |                                    +---+------------------+
| expires_at         |
+--------------------+
```

### 4.2 SQLAlchemy Models

```python
# models/database.py

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
import enum

Base = declarative_base()

class GenerationStatusEnum(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"

class ImageTypeEnum(enum.Enum):
    MAIN = "main"
    INFOGRAPHIC_1 = "infographic_1"
    INFOGRAPHIC_2 = "infographic_2"
    LIFESTYLE = "lifestyle"
    COMPARISON = "comparison"

class IntentTypeEnum(enum.Enum):
    DURABILITY = "durability"
    USE_CASE = "use_case"
    STYLE = "style"
    PROBLEM_SOLUTION = "problem_solution"
    COMPARISON = "comparison"

class GenerationSession(Base):
    __tablename__ = "generation_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING)

    # Upload reference
    upload_path = Column(String(500), nullable=False)

    # Product information
    product_title = Column(String(200), nullable=False)
    feature_1 = Column(String(100), nullable=False)
    feature_2 = Column(String(100), nullable=False)
    feature_3 = Column(String(100), nullable=False)
    target_audience = Column(String(150), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))

    # Relationships
    keywords = relationship("SessionKeyword", back_populates="session", cascade="all, delete-orphan")
    images = relationship("ImageRecord", back_populates="session", cascade="all, delete-orphan")

class SessionKeyword(Base):
    __tablename__ = "session_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("generation_sessions.id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    intent_types = Column(JSON, default=list)  # List of IntentTypeEnum values
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("GenerationSession", back_populates="keywords")

class ImageRecord(Base):
    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("generation_sessions.id"), nullable=False)
    image_type = Column(Enum(ImageTypeEnum), nullable=False)
    storage_path = Column(String(500), nullable=True)
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("GenerationSession", back_populates="images")
```

### 4.3 Database Configuration

```python
# db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLite for MVP
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL or "sqlite:///./listing_genie.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 5. Image Generation Pipeline

### 5.1 Reference Image Handling

Following the pattern from the existing Gemini MCP implementation:

```python
# services/gemini_service.py

from google import genai
from google.genai import types
from PIL import Image as PILImage
from pathlib import Path
from typing import Optional
import base64
from io import BytesIO

class GeminiService:
    """Wrapper for Gemini API image generation with reference image support"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3-pro-image-preview"

    async def generate_image(
        self,
        prompt: str,
        reference_image_path: str,
        aspect_ratio: str = "1:1",
        max_retries: int = 3
    ) -> Optional[PILImage.Image]:
        """
        Generate an image using Gemini with a reference product image.

        Args:
            prompt: The generation prompt including style and context
            reference_image_path: Path to the uploaded product image
            aspect_ratio: Output aspect ratio (1:1 for Amazon)
            max_retries: Number of retry attempts on failure

        Returns:
            PIL Image object or None if generation failed
        """
        # Load reference image
        reference_image = PILImage.open(reference_image_path)

        # Prepare contents: prompt + reference image
        contents = [prompt, reference_image]

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['Image'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio
                        )
                    )
                )

                # Extract generated image from response
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        image = PILImage.open(BytesIO(part.inline_data.data))
                        return image

                return None  # No image in response

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return None
```

### 5.2 Prompt Template System

```python
# prompts/engine.py

from typing import Dict, List, Optional
from dataclasses import dataclass
from .templates import main_image, infographic, lifestyle, comparison
from .intent_modifiers import get_intent_modifiers

@dataclass
class ProductContext:
    title: str
    features: List[str]
    target_audience: str
    keywords: List[str]
    intents: Dict[str, List[str]]  # keyword -> list of intent types

class PromptEngine:
    """Constructs prompts for each image type with intent injection"""

    def __init__(self):
        self.templates = {
            'main': main_image.TEMPLATE,
            'infographic_1': infographic.TEMPLATE_1,
            'infographic_2': infographic.TEMPLATE_2,
            'lifestyle': lifestyle.TEMPLATE,
            'comparison': comparison.TEMPLATE,
        }

    def build_prompt(
        self,
        image_type: str,
        context: ProductContext
    ) -> str:
        """
        Build a complete prompt for the specified image type.

        Args:
            image_type: One of main, infographic_1, infographic_2, lifestyle, comparison
            context: Product information and keyword intents

        Returns:
            Complete prompt string ready for Gemini API
        """
        # Get base template
        template = self.templates[image_type]

        # Get intent modifiers for this image type
        intent_modifiers = get_intent_modifiers(image_type, context.intents)

        # Select appropriate features for this image type
        feature_mapping = {
            'main': context.features[0],
            'infographic_1': context.features[0],
            'infographic_2': context.features[1],
            'lifestyle': context.target_audience,
            'comparison': f"{context.features[1]}, {context.features[2]}",
        }

        # Build the prompt
        prompt = template.format(
            product_title=context.title,
            key_feature=feature_mapping.get(image_type, context.features[0]),
            feature_1=context.features[0],
            feature_2=context.features[1],
            feature_3=context.features[2],
            target_audience=context.target_audience,
            intent_modifiers=intent_modifiers,
            top_keywords=', '.join(context.keywords[:5])
        )

        return prompt
```

### 5.3 Prompt Templates (Based on Creative Blueprint)

```python
# prompts/templates/main_image.py

TEMPLATE = """
Create a premium Amazon main product image.

[REFERENCE IMAGE]
Use the provided product photo as the base reference.
Maintain product accuracy while applying creative direction.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {key_feature}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Pure white background (#FFFFFF)
- Product fills 85% of frame
- Use dynamic "stacking" composition with depth
- If applicable, show ingredient elements (fruits, herbs, etc.) arranged aesthetically
- Professional studio lighting with subtle natural shadows
- Premium, tactile texture quality

[STYLE DIRECTION]
- High-end commercial product photography
- Visually "dense" and interesting
- Must stand out in Amazon search results grid
- No text, logos, or watermarks

[INTENT ALIGNMENT]
{intent_modifiers}

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px minimum
- Format: PNG with RGB color mode
- Amazon compliant: white background, product-focused

Enhance and stage the product, do not alter the product itself.
"""
```

```python
# prompts/templates/infographic.py

TEMPLATE_1 = """
Create an Amazon infographic image highlighting a key benefit.

[REFERENCE IMAGE]
Use the provided product photo for accurate product representation.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {feature_1}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Product visible and prominent (center-left placement)
- Large, bold headline text highlighting the benefit
- Text is a DESIGN element, not just a caption
- High-contrast, legible at thumbnail size
- Text covers less than 20% of image area
- F-pattern reading flow consideration

[STYLE DIRECTION]
- Modern, clean infographic design
- Benefit-focused language (e.g., "Sleep Better" not "10mg Melatonin")
- Color palette matching product aesthetic
- Professional but approachable

[INTENT ALIGNMENT]
{intent_modifiers}

[KEYWORD ALIGNMENT]
Top keywords: {top_keywords}
Ensure visual elements prove the claims implied by these search terms.

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Text readable at mobile thumbnail size
"""

TEMPLATE_2 = """
Create an Amazon infographic image highlighting a secondary key benefit.

[REFERENCE IMAGE]
Use the provided product photo for accurate product representation.

[PRODUCT CONTEXT]
Product: {product_title}
Key Benefit: {feature_2}
Target Audience: {target_audience}

[COMPOSITION REQUIREMENTS]
- Product visible and prominent
- Large, bold headline text highlighting the benefit
- Text as design element with visual hierarchy
- High-contrast for mobile visibility
- Text density under 20%

[STYLE DIRECTION]
- Consistent with first infographic styling
- Different visual approach to avoid repetition
- Benefit-focused messaging
- Modern, scannable layout

[INTENT ALIGNMENT]
{intent_modifiers}

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Maintains visual cohesion with other listing images
"""
```

```python
# prompts/templates/lifestyle.py

TEMPLATE = """
Create an Instagram-style lifestyle image for Amazon.

[REFERENCE IMAGE]
Use the provided product photo. Show it being used naturally in context.

[PRODUCT CONTEXT]
Product: {product_title}
Target Audience: {target_audience}
Key Features: {feature_1}, {feature_2}

[COMPOSITION REQUIREMENTS]
- Authentic, real-world setting
- Person using/enjoying product matches target demographic
- Warm, natural lighting (sunlit room, outdoor, etc.)
- Product clearly visible but naturally integrated
- Aspirational but relatable scene

[STYLE DIRECTION]
- High-end social media aesthetic
- Warm, inviting, authentic feel
- NOT clinical or stock-photo looking
- Model expression shows positive result of using product
- Emotional resonance with target audience

[INTENT ALIGNMENT]
{intent_modifiers}

[USE CASE VISUALIZATION]
Based on target audience "{target_audience}", show the product in a context
that matches their lifestyle and usage patterns.

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Natural color grading
- Lifestyle context appropriate for product category
"""
```

```python
# prompts/templates/comparison.py

TEMPLATE = """
Create a comparison chart image for Amazon.

[REFERENCE IMAGE]
Use the provided product photo on the "our product" side.
Represent competitor as generic/unnamed alternative.

[PRODUCT CONTEXT]
Product: {product_title}
Our Advantages: {feature_2}, {feature_3}

[COMPOSITION REQUIREMENTS]
- "Us vs. Them" two-column layout
- Our product: vibrant colors, checkmarks (green)
- Generic competitor: muted/greyscale, X-marks (red/grey)
- 3-4 comparison points based on features
- Clear visual hierarchy showing our product as winner

[STYLE DIRECTION]
- Professional infographic design
- Strong color contrast (green vs. red/grey)
- Text legible at thumbnail size
- Color psychology: warm/positive for us, cool/negative for them

[INTENT ALIGNMENT]
{intent_modifiers}

[COMPARISON POINTS]
1. {feature_2} (Us: Yes, Them: No)
2. {feature_3} (Us: Yes, Them: Limited)
3. Quality/Premium (Us: Superior, Them: Basic)

[TECHNICAL REQUIREMENTS]
- Resolution: 2000x2000px
- Clear, scannable layout
- Winner should be immediately obvious
"""
```

### 5.4 Keyword Intent Injection

```python
# prompts/intent_modifiers.py

from typing import Dict, List

INTENT_VISUAL_PROOF = {
    'durability': [
        "Show rugged, premium materials and construction quality",
        "Emphasize durability through visual texture and build quality",
        "Include visual cues suggesting long-lasting performance",
    ],
    'use_case': [
        "Show product in the exact context implied by search terms",
        "Visualize the specific use case scenario",
        "Environment should match intended usage",
    ],
    'style': [
        "Match visual aesthetic to style-related keywords",
        "Color palette and composition should reflect style intent",
        "Design elements should resonate with aesthetic preferences",
    ],
    'problem_solution': [
        "Visualize the solved state / positive outcome",
        "Show relief, satisfaction, or resolution",
        "Before/after or transformation visual if appropriate",
    ],
    'comparison': [
        "Emphasize superiority and premium positioning",
        "Clear winner hierarchy in visual presentation",
        "Quality differentiation should be obvious",
    ],
}

IMAGE_TYPE_INTENT_PRIORITY = {
    'main': ['durability', 'style'],
    'infographic_1': ['problem_solution', 'durability'],
    'infographic_2': ['problem_solution', 'use_case'],
    'lifestyle': ['use_case', 'style'],
    'comparison': ['comparison', 'durability'],
}

def get_intent_modifiers(
    image_type: str,
    keyword_intents: Dict[str, List[str]]
) -> str:
    """
    Generate intent-specific prompt modifiers for an image type.

    Args:
        image_type: The type of image being generated
        keyword_intents: Mapping of keywords to their classified intents

    Returns:
        String of intent modifiers to inject into the prompt
    """
    # Collect all unique intents from keywords
    all_intents = set()
    for intents in keyword_intents.values():
        all_intents.update(intents)

    # Get priority intents for this image type
    priority_intents = IMAGE_TYPE_INTENT_PRIORITY.get(image_type, [])

    # Build modifier string
    modifiers = []
    for intent in priority_intents:
        if intent in all_intents:
            proof_statements = INTENT_VISUAL_PROOF.get(intent, [])
            if proof_statements:
                modifiers.append(f"[{intent.upper()} INTENT]")
                modifiers.extend(f"- {stmt}" for stmt in proof_statements)

    if not modifiers:
        return "Focus on professional product presentation and visual appeal."

    return '\n'.join(modifiers)
```

### 5.5 Batch Generation Flow

```python
# tasks/generation_task.py

import asyncio
from typing import List
from app.services.gemini_service import GeminiService
from app.prompts.engine import PromptEngine, ProductContext
from app.services.storage_service import StorageService
from app.models.database import GenerationSession, ImageRecord, GenerationStatusEnum, ImageTypeEnum
from sqlalchemy.orm import Session

IMAGE_TYPES = [
    ImageTypeEnum.MAIN,
    ImageTypeEnum.INFOGRAPHIC_1,
    ImageTypeEnum.INFOGRAPHIC_2,
    ImageTypeEnum.LIFESTYLE,
    ImageTypeEnum.COMPARISON,
]

async def generate_listing_images(
    session_id: str,
    db: Session,
    gemini: GeminiService,
    prompts: PromptEngine,
    storage: StorageService
):
    """
    Background task to generate all 5 listing images.

    This task runs asynchronously after the API returns the session ID,
    allowing the frontend to poll for status updates.
    """
    # Load session
    session = db.query(GenerationSession).filter_by(id=session_id).first()
    if not session:
        return

    # Update session status to processing
    session.status = GenerationStatusEnum.PROCESSING
    db.commit()

    # Build product context
    keywords = {kw.keyword: kw.intent_types for kw in session.keywords}
    context = ProductContext(
        title=session.product_title,
        features=[session.feature_1, session.feature_2, session.feature_3],
        target_audience=session.target_audience,
        keywords=list(keywords.keys()),
        intents=keywords
    )

    # Generate each image
    success_count = 0
    for image_type in IMAGE_TYPES:
        image_record = db.query(ImageRecord).filter_by(
            session_id=session_id,
            image_type=image_type
        ).first()

        if not image_record:
            image_record = ImageRecord(session_id=session_id, image_type=image_type)
            db.add(image_record)
            db.commit()

        try:
            # Update status to processing
            image_record.status = GenerationStatusEnum.PROCESSING
            db.commit()

            # Build prompt
            prompt = prompts.build_prompt(image_type.value, context)

            # Generate image
            generated_image = await gemini.generate_image(
                prompt=prompt,
                reference_image_path=session.upload_path,
                aspect_ratio="1:1"
            )

            if generated_image:
                # Save to storage
                path = storage.save_generated_image(
                    session_id=session_id,
                    image_type=image_type.value,
                    image=generated_image
                )

                # Update record
                image_record.storage_path = path
                image_record.status = GenerationStatusEnum.COMPLETE
                image_record.completed_at = datetime.utcnow()
                success_count += 1
            else:
                image_record.status = GenerationStatusEnum.FAILED
                image_record.error_message = "No image returned from API"

        except Exception as e:
            image_record.status = GenerationStatusEnum.FAILED
            image_record.error_message = str(e)
            image_record.retry_count += 1

        db.commit()

    # Update session status
    if success_count == len(IMAGE_TYPES):
        session.status = GenerationStatusEnum.COMPLETE
    elif success_count > 0:
        session.status = GenerationStatusEnum.PARTIAL
    else:
        session.status = GenerationStatusEnum.FAILED

    session.completed_at = datetime.utcnow()
    db.commit()
```

### 5.6 Error Handling and Retry Logic

```python
# services/generation_service.py (retry logic extension)

class RetryConfig:
    MAX_RETRIES = 3
    BASE_DELAY = 1  # seconds
    MAX_DELAY = 8   # seconds

async def retry_failed_image(
    session_id: str,
    image_type: ImageTypeEnum,
    db: Session,
    gemini: GeminiService,
    prompts: PromptEngine,
    storage: StorageService
) -> bool:
    """
    Retry generating a single failed image with prompt variation.

    Returns True if retry succeeded, False otherwise.
    """
    image_record = db.query(ImageRecord).filter_by(
        session_id=session_id,
        image_type=image_type
    ).first()

    if not image_record or image_record.retry_count >= RetryConfig.MAX_RETRIES:
        return False

    # Exponential backoff
    delay = min(
        RetryConfig.BASE_DELAY * (2 ** image_record.retry_count),
        RetryConfig.MAX_DELAY
    )
    await asyncio.sleep(delay)

    # Modify prompt slightly for retry (add variation)
    session = db.query(GenerationSession).filter_by(id=session_id).first()
    context = _build_context(session)

    base_prompt = prompts.build_prompt(image_type.value, context)
    retry_prompt = _add_prompt_variation(base_prompt, image_record.retry_count)

    try:
        generated_image = await gemini.generate_image(
            prompt=retry_prompt,
            reference_image_path=session.upload_path,
        )

        if generated_image:
            path = storage.save_generated_image(
                session_id=session_id,
                image_type=image_type.value,
                image=generated_image
            )

            image_record.storage_path = path
            image_record.status = GenerationStatusEnum.COMPLETE
            image_record.completed_at = datetime.utcnow()
            db.commit()
            return True

    except Exception as e:
        image_record.error_message = str(e)

    image_record.retry_count += 1
    db.commit()
    return False

def _add_prompt_variation(prompt: str, retry_count: int) -> str:
    """Add slight variations to prompt for retry attempts"""
    variations = [
        "\n[VARIATION: Emphasize clarity and simplicity]",
        "\n[VARIATION: Focus on product detail and precision]",
        "\n[VARIATION: Prioritize clean composition]",
    ]
    return prompt + variations[retry_count % len(variations)]
```

---

## 6. Prompt Engineering Architecture

### 6.1 Template Structure

```
prompts/
|-- __init__.py
|-- engine.py              # Main PromptEngine class
|-- templates/
|   |-- __init__.py
|   |-- base.py            # Base template components
|   |-- main_image.py      # Main image template
|   |-- infographic.py     # Infographic templates (1 & 2)
|   |-- lifestyle.py       # Lifestyle template
|   |-- comparison.py      # Comparison chart template
|-- intent_modifiers.py    # Intent classification and injection
|-- color_psychology.py    # Category-based color recommendations
|-- composition_rules.py   # Heatmap-based composition guidance
```

### 6.2 Dynamic Variable Injection

```python
# prompts/engine.py

from typing import Dict, Any
import re

class PromptEngine:
    def __init__(self):
        self.variable_pattern = re.compile(r'\{(\w+)\}')

    def render_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Render a template with variable substitution.

        Supports:
        - Simple variables: {variable_name}
        - Conditional blocks: {?variable_name}content{/variable_name}
        """
        # Simple variable substitution
        result = template
        for key, value in variables.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            result = result.replace(f'{{{key}}}', str(value))

        # Remove any remaining unsubstituted variables
        result = self.variable_pattern.sub('', result)

        return result.strip()
```

### 6.3 Intent-Based Prompt Modification

The intent system classifies keywords and injects relevant visual proof requirements:

| Intent Type | Visual Proof Elements |
|-------------|----------------------|
| **Durability/Quality** | Rugged textures, premium materials, professional build quality |
| **Use Case** | Product in context (camping, office, travel, etc.) |
| **Style/Aesthetic** | Matching visual style (modern, vintage, minimalist) |
| **Problem/Solution** | Before/after, relief expression, solved state |
| **Comparison** | Superiority indicators, premium positioning |

### 6.4 Style Consistency System

```python
# prompts/color_psychology.py

CATEGORY_PALETTES = {
    'health_supplements': {
        'primary': ['earthy greens', 'natural browns', 'soft whites'],
        'accent': ['gold', 'amber'],
        'mood': 'natural, trustworthy, organic'
    },
    'fitness': {
        'primary': ['bold blacks', 'energetic reds', 'electric blues'],
        'accent': ['neon green', 'orange'],
        'mood': 'powerful, energetic, motivating'
    },
    'baby_kids': {
        'primary': ['soft pastels', 'warm yellows', 'gentle blues'],
        'accent': ['white', 'cream'],
        'mood': 'safe, gentle, nurturing'
    },
    'tech_electronics': {
        'primary': ['deep blues', 'clean whites', 'sleek grays'],
        'accent': ['electric blue', 'silver'],
        'mood': 'modern, innovative, premium'
    },
    'home_kitchen': {
        'primary': ['warm neutrals', 'natural wood tones', 'white'],
        'accent': ['copper', 'brass', 'green'],
        'mood': 'warm, inviting, reliable'
    },
    'default': {
        'primary': ['professional blues', 'clean whites'],
        'accent': ['gold', 'green'],
        'mood': 'professional, trustworthy'
    }
}

def get_color_guidance(category: str) -> str:
    """Generate color palette guidance for prompts"""
    palette = CATEGORY_PALETTES.get(category, CATEGORY_PALETTES['default'])

    return f"""
[COLOR PSYCHOLOGY]
- Primary palette: {', '.join(palette['primary'])}
- Accent colors: {', '.join(palette['accent'])}
- Overall mood: {palette['mood']}
"""

def infer_category(product_title: str, keywords: List[str]) -> str:
    """Infer product category from title and keywords"""
    title_lower = product_title.lower()
    keywords_lower = [k.lower() for k in keywords]
    all_text = title_lower + ' ' + ' '.join(keywords_lower)

    category_keywords = {
        'health_supplements': ['vitamin', 'supplement', 'gummy', 'organic', 'natural', 'health'],
        'fitness': ['fitness', 'workout', 'gym', 'protein', 'exercise', 'sport'],
        'baby_kids': ['baby', 'kid', 'child', 'infant', 'toddler', 'nursery'],
        'tech_electronics': ['tech', 'electronic', 'gadget', 'smart', 'device', 'digital'],
        'home_kitchen': ['kitchen', 'home', 'cooking', 'utensil', 'organizer', 'storage'],
    }

    for category, keywords in category_keywords.items():
        if any(kw in all_text for kw in keywords):
            return category

    return 'default'
```

---

## 7. Deployment Architecture

### 7.1 Dockerfile Design

```dockerfile
# Dockerfile

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Build production assets
COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Python Application
# ============================================
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create storage directories
RUN mkdir -p storage/uploads storage/generated

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Environment Variables

```bash
# .env.example

# ======================
# Application Settings
# ======================
APP_NAME=listing-genie
APP_ENV=development  # development, staging, production
DEBUG=true
SECRET_KEY=your-secret-key-here

# ======================
# API Keys
# ======================
GEMINI_API_KEY=your-gemini-api-key

# ======================
# Database
# ======================
# SQLite (MVP)
DATABASE_URL=sqlite:///./listing_genie.db

# PostgreSQL (Production)
# DATABASE_URL=postgresql://user:password@host:5432/listing_genie

# ======================
# Storage
# ======================
STORAGE_TYPE=local  # local, s3, gcs
STORAGE_PATH=./storage

# AWS S3 (if STORAGE_TYPE=s3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
AWS_REGION=us-east-1

# ======================
# Feature Flags
# ======================
ENABLE_PAYMENT=false  # Deferred to Phase 2

# ======================
# Logging
# ======================
LOG_LEVEL=INFO
LOG_FORMAT=json

# ======================
# Rate Limiting
# ======================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600  # seconds
```

### 7.3 Configuration Management

```python
# app/config.py

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    app_name: str = "listing-genie"
    app_env: str = "development"
    debug: bool = False
    secret_key: str

    # API Keys
    gemini_api_key: str

    # Database
    database_url: str = "sqlite:///./listing_genie.db"

    # Storage
    storage_type: str = "local"
    storage_path: str = "./storage"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "us-east-1"

    # Feature Flags
    enable_payment: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 7.4 Health Check Endpoints

```python
# app/api/endpoints/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env
    }

@router.get("/api/health")
async def api_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status"""
    checks = {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {}
    }

    # Database check
    try:
        db.execute("SELECT 1")
        checks["checks"]["database"] = "connected"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "degraded"

    # Storage check
    try:
        from pathlib import Path
        storage_path = Path(settings.storage_path)
        if storage_path.exists() and storage_path.is_dir():
            checks["checks"]["storage"] = "accessible"
        else:
            checks["checks"]["storage"] = "not accessible"
            checks["status"] = "degraded"
    except Exception as e:
        checks["checks"]["storage"] = f"error: {str(e)}"
        checks["status"] = "degraded"

    return checks
```

### 7.5 Local Development Setup

```yaml
# docker-compose.yml

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - DEBUG=true
      - DATABASE_URL=sqlite:///./listing_genie.db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - STORAGE_TYPE=local
      - STORAGE_PATH=/app/storage
    volumes:
      - ./app:/app/app  # Hot reload
      - ./storage:/app/storage
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # PostgreSQL (optional for production-like testing)
  # db:
  #   image: postgres:15-alpine
  #   environment:
  #     POSTGRES_USER: listing_genie
  #     POSTGRES_PASSWORD: development
  #     POSTGRES_DB: listing_genie
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

volumes:
  postgres_data:
```

### 7.6 Deployment Configurations

**Railway/Render Configuration:**

```toml
# railway.toml (Railway)
[build]
builder = "DOCKERFILE"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

```yaml
# render.yaml (Render)
services:
  - type: web
    name: listing-genie
    env: docker
    plan: starter
    healthCheckPath: /health
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: listing-genie-db
          property: connectionString

databases:
  - name: listing-genie-db
    plan: starter
```

---

## 8. E2E Testing Strategy

### 8.1 Critical User Journeys

| Journey | Description | Priority |
|---------|-------------|----------|
| **Happy Path** | Upload -> Form -> Generate -> Download | Critical |
| **Partial Failure** | Some images fail, others succeed | High |
| **Complete Failure** | All generations fail, proper error handling | High |
| **Large File Upload** | 10MB image upload and validation | Medium |
| **Invalid Input** | Form validation and error messages | Medium |
| **Session Timeout** | Browser closed during generation, resumption | Medium |
| **Mobile Flow** | Complete flow on mobile devices | High |

### 8.2 Test Framework Recommendation

**Primary: Playwright**

Playwright is recommended for E2E testing because:
- Cross-browser support (Chrome, Firefox, Safari)
- Native mobile emulation
- Built-in API testing capabilities
- Screenshot and video recording for debugging
- Good TypeScript support

```typescript
// tests/e2e/happy-path.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Listing Genie - Happy Path', () => {
  test('complete generation flow', async ({ page }) => {
    // Navigate to landing page
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Transform Your Product');

    // Click start button
    await page.click('text=Start Generating');

    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/test-product.jpg');

    // Wait for upload to complete
    await expect(page.locator('text=Looks good')).toBeVisible();
    await page.click('text=Continue');

    // Fill form
    await page.fill('[name="title"]', 'Organic Sleep Gummies');
    await page.fill('[name="feature1"]', 'All-natural melatonin');
    await page.fill('[name="feature2"]', 'Non-habit forming');
    await page.fill('[name="feature3"]', 'Delicious berry flavor');
    await page.fill('[name="targetAudience"]', 'Busy professionals');

    // Add keywords
    await page.fill('[name="keywords"]', 'sleep gummies, natural sleep aid');
    await page.click('text=Continue');

    // Wait for generation to complete (mock API in tests)
    await expect(page.locator('text=Your Images Are Ready')).toBeVisible({ timeout: 120000 });

    // Verify gallery
    await expect(page.locator('[data-testid="image-card"]')).toHaveCount(5);

    // Download ZIP
    const downloadPromise = page.waitForEvent('download');
    await page.click('text=Download All');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.zip');
  });
});
```

### 8.3 Test Organization

```
tests/
|-- e2e/
|   |-- fixtures/
|   |   |-- test-product.jpg        # Test product image
|   |   |-- large-product.jpg       # 10MB test image
|   |   |-- invalid-format.gif      # Invalid format
|   |-- happy-path.spec.ts          # Complete success flow
|   |-- upload-validation.spec.ts   # Upload edge cases
|   |-- form-validation.spec.ts     # Form validation
|   |-- error-handling.spec.ts      # Error scenarios
|   |-- mobile.spec.ts              # Mobile-specific tests
|   |-- playwright.config.ts        # Playwright configuration
|
|-- integration/
|   |-- test_api_upload.py          # API upload tests
|   |-- test_api_generation.py      # API generation tests
|   |-- test_api_download.py        # API download tests
|   |-- test_gemini_service.py      # Gemini service tests
|
|-- unit/
|   |-- test_prompt_engine.py       # Prompt construction
|   |-- test_keyword_service.py     # Keyword classification
|   |-- test_storage_service.py     # Storage operations
```

### 8.4 Playwright Configuration

```typescript
// playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'uvicorn app.main:app --port 8000',
    url: 'http://localhost:8000/health',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 9. Security Considerations

### 9.1 API Key Management

```python
# app/core/security.py

from functools import lru_cache
from app.config import settings
import os

@lru_cache()
def get_gemini_api_key() -> str:
    """Retrieve Gemini API key with validation"""
    api_key = settings.gemini_api_key

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    if len(api_key) < 20:
        raise ValueError("GEMINI_API_KEY appears to be invalid")

    return api_key

# Never log or expose API keys
def mask_api_key(key: str) -> str:
    """Mask API key for logging purposes"""
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"
```

**Best Practices:**
1. Store API keys in environment variables only
2. Never commit API keys to version control
3. Use secrets management in production (Railway/Render secrets, AWS Secrets Manager)
4. Rotate keys regularly
5. Use different keys for development/staging/production

### 9.2 Input Validation

```python
# app/api/endpoints/upload.py

from fastapi import UploadFile, HTTPException
from PIL import Image
import magic  # python-magic for file type detection

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_IMAGE_DIMENSION = 1000

async def validate_upload(file: UploadFile) -> bytes:
    """Validate uploaded file with multiple security checks"""

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File size exceeds 10MB limit")

    # Check MIME type using magic numbers (not just extension)
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Invalid file type: {mime_type}. Only JPEG and PNG allowed.")

    # Validate image dimensions
    try:
        image = Image.open(BytesIO(content))
        width, height = image.size

        if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
            raise HTTPException(
                400,
                f"Image must be at least {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}px. "
                f"Uploaded: {width}x{height}px"
            )

        # Check for potentially malicious files (image bombs)
        if width > 10000 or height > 10000:
            raise HTTPException(400, "Image dimensions exceed maximum allowed size")

    except Image.DecompressionBombError:
        raise HTTPException(400, "Image file appears to be corrupted or malicious")
    except Exception as e:
        raise HTTPException(400, f"Invalid image file: {str(e)}")

    return content
```

### 9.3 File Upload Security

```python
# app/services/storage_service.py

import uuid
import os
from pathlib import Path
from PIL import Image
from io import BytesIO

class StorageService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.uploads_path = self.storage_path / "uploads"
        self.generated_path = self.storage_path / "generated"

        # Ensure directories exist
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)

    def save_upload(self, content: bytes, original_filename: str) -> str:
        """
        Safely save uploaded file.

        - Generate random UUID filename (prevent path traversal)
        - Re-encode image to strip EXIF and potential exploits
        - Store in isolated upload directory
        """
        # Generate safe filename
        file_id = str(uuid.uuid4())
        extension = self._get_safe_extension(original_filename)
        safe_filename = f"{file_id}.{extension}"

        # Re-encode image to strip metadata and validate
        image = Image.open(BytesIO(content))
        image = image.convert('RGB')  # Remove alpha channel if present

        output_path = self.uploads_path / safe_filename
        image.save(output_path, format='PNG', optimize=True)

        return str(output_path)

    def _get_safe_extension(self, filename: str) -> str:
        """Extract and validate file extension"""
        extension = Path(filename).suffix.lower().lstrip('.')
        if extension in ('jpg', 'jpeg'):
            return 'png'  # Normalize to PNG
        if extension == 'png':
            return 'png'
        return 'png'  # Default to PNG

    def get_upload_path(self, upload_id: str) -> Path:
        """Get path to uploaded file with validation"""
        safe_path = self.uploads_path / f"{upload_id}.png"

        # Ensure path is within uploads directory (prevent traversal)
        if not safe_path.resolve().is_relative_to(self.uploads_path.resolve()):
            raise ValueError("Invalid upload ID")

        if not safe_path.exists():
            raise FileNotFoundError("Upload not found")

        return safe_path
```

### 9.4 Rate Limiting

```python
# app/core/middleware.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from app.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_hour: int = 100):
        super().__init__(app)
        self.requests_per_hour = requests_per_hour
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/api/health']:
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old requests
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip]
            if current_time - t < 3600
        ]

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_hour:
            raise HTTPException(
                429,
                "Rate limit exceeded. Please try again later."
            )

        # Record request
        self.request_counts[client_ip].append(current_time)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        # Handle proxied requests
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'
```

### 9.5 Security Headers

```python
# app/core/middleware.py

from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        # Content Security Policy
        csp = "; ".join([
            "default-src 'self'",
            "img-src 'self' data: blob:",
            "script-src 'self' 'unsafe-inline'",  # Needed for React
            "style-src 'self' 'unsafe-inline'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
        ])
        response.headers['Content-Security-Policy'] = csp

        return response
```

---

## 10. Future Scalability (Phase 2 Preparation)

### 10.1 Payment Integration Hooks

The architecture is designed to easily add Stripe payment in Phase 2:

```python
# app/services/payment_service.py (Phase 2 placeholder)

from typing import Optional
from app.config import settings

class PaymentService:
    """
    Payment service placeholder - activated in Phase 2.

    Integration points:
    1. POST /api/create-checkout -> Create Stripe checkout session
    2. POST /api/webhooks/stripe -> Handle Stripe webhooks
    3. GET /api/payment-status/:id -> Verify payment completion
    """

    def __init__(self):
        self.enabled = settings.enable_payment
        if self.enabled:
            import stripe
            stripe.api_key = settings.stripe_secret_key

    async def create_checkout_session(
        self,
        session_id: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[str]:
        """Create Stripe checkout session and return URL"""
        if not self.enabled:
            return None  # Bypass payment in Phase 1

        # Phase 2 implementation
        pass

    async def verify_payment(self, payment_id: str) -> bool:
        """Verify payment was successful"""
        if not self.enabled:
            return True  # Always successful in Phase 1

        # Phase 2 implementation
        pass
```

**Phase 2 Environment Variables (add when ready):**
```bash
# Payment (Phase 2)
ENABLE_PAYMENT=true
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

### 10.2 User Authentication Preparation

```python
# app/core/auth.py (Phase 2 placeholder)

from typing import Optional
from fastapi import Request, Depends
from app.config import settings

class AuthService:
    """
    Authentication placeholder - activated in Phase 2.

    Planned approach: JWT tokens with optional OAuth (Google, Amazon)
    """

    def __init__(self):
        self.enabled = settings.enable_auth

    async def get_current_user(self, request: Request) -> Optional[dict]:
        """Get current user from request (if authenticated)"""
        if not self.enabled:
            return None  # Anonymous in Phase 1

        # Phase 2: Extract and validate JWT token
        pass

    async def require_auth(self, request: Request) -> dict:
        """Require authentication for protected routes"""
        if not self.enabled:
            return {"id": "anonymous", "email": None}

        # Phase 2: Validate and return user
        pass

# Dependency for protected routes
async def get_optional_user(request: Request) -> Optional[dict]:
    auth = AuthService()
    return await auth.get_current_user(request)

async def require_user(request: Request) -> dict:
    auth = AuthService()
    return await auth.require_auth(request)
```

**Database model additions for Phase 2:**
```python
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # None for OAuth
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    sessions = relationship("GenerationSession", back_populates="user")

# Add to GenerationSession:
# user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
```

### 10.3 Cloud Storage Migration Path

```python
# app/services/storage_service.py

from abc import ABC, abstractmethod
from typing import Protocol
from app.config import settings

class StorageBackend(Protocol):
    """Interface for storage backends"""

    async def save(self, key: str, data: bytes) -> str:
        """Save data and return URL/path"""
        ...

    async def get(self, key: str) -> bytes:
        """Retrieve data by key"""
        ...

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        """Get signed URL for direct access"""
        ...

    async def delete(self, key: str) -> None:
        """Delete data by key"""
        ...

class LocalStorageBackend:
    """Local filesystem storage (MVP)"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    async def save(self, key: str, data: bytes) -> str:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        # Local storage returns direct path
        return f"/storage/{key}"

class S3StorageBackend:
    """AWS S3 storage (Phase 2)"""

    def __init__(self):
        import boto3
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket = settings.aws_s3_bucket

    async def save(self, key: str, data: bytes) -> str:
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

    async def get_url(self, key: str, expires_in: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expires_in
        )

def get_storage_backend() -> StorageBackend:
    """Factory function to get appropriate storage backend"""
    if settings.storage_type == 's3':
        return S3StorageBackend()
    return LocalStorageBackend(settings.storage_path)
```

### 10.4 Scalability Considerations

| Concern | MVP Approach | Phase 2 Approach |
|---------|--------------|------------------|
| **Database** | SQLite file | PostgreSQL with connection pooling |
| **Storage** | Local filesystem | AWS S3 with CloudFront CDN |
| **Background Tasks** | In-process async | Celery with Redis broker |
| **Caching** | None | Redis for session/rate limiting |
| **Horizontal Scaling** | Single container | Multiple containers behind load balancer |
| **API Rate Limiting** | In-memory | Redis-backed distributed limiting |

---

## 11. Technology Summary

### 11.1 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend Framework** | FastAPI | 0.104+ | High-performance async API |
| **Python Runtime** | Python | 3.11+ | Language runtime |
| **Frontend Framework** | React | 18+ | User interface |
| **Build Tool** | Vite | 5+ | Frontend build and dev server |
| **CSS Framework** | Tailwind CSS | 3+ | Utility-first styling |
| **AI Model** | Gemini 3 Pro Image Preview | - | Image generation |
| **AI SDK** | google-genai | latest | Gemini API client |
| **Database (MVP)** | SQLite | 3+ | Local database |
| **Database (Prod)** | PostgreSQL | 15+ | Production database |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Validation** | Pydantic | 2.0+ | Request/response validation |
| **Testing** | Playwright | 1.40+ | E2E testing |
| **Testing** | pytest | 7+ | Unit/integration testing |
| **Container** | Docker | 24+ | Containerization |

### 11.2 Key Dependencies

**Python (requirements.txt):**
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
google-genai>=0.1.0
pillow>=10.0.0
python-magic>=0.4.27
httpx>=0.25.0
python-dotenv>=1.0.0
```

**Node.js (package.json key dependencies):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.48.0",
    "lucide-react": "^0.292.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "vite": "^5.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

---

## 12. Implementation Priority

### 12.1 Recommended Build Order

**Phase 1: Foundation (Week 1)**
1. Story 5.1: FastAPI Backend Setup
2. Story 5.3: Database Setup
3. Story 5.2: React Frontend Setup
4. Story 2.1: Gemini API Integration

**Phase 2: Core Generation (Week 2)**
5. Story 2.1b: Prompt Engineering System
6. Story 2.2: Main Image Generation
7. Story 2.3-2.5: Supporting Image Generation
8. Story 2.6-2.7: Error Handling & Storage

**Phase 3: User Interface (Week 3)**
9. Story 1.1: Product Photo Upload
10. Story 1.2: Product Information Form
11. Story 4.1-4.2: Keyword Input & Classification
12. Story 4.3: Intent-Aligned Generation

**Phase 4: Gallery & Polish (Week 4)**
13. Story 3.1-3.4: Gallery & Download
14. Story 5.5: Deployment Configuration
15. Story 4.4: Heatmap Optimization (if time)
16. E2E Testing & Bug Fixes

### 12.2 Critical Path

```
[FastAPI Setup] --> [Database] --> [Gemini Integration] --> [Prompt Engine]
                                           |
                                           v
[Frontend Setup] --> [Upload UI] --> [Form UI] --> [Generation Flow]
                                           |
                                           v
                                    [Gallery UI] --> [Download] --> [Deploy]
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 20, 2024 | Winston (Architect) | Initial architecture document |

---

*This architecture document provides the technical blueprint for Listing Genie MVP. All development work should reference this document for system design decisions. Changes to architecture require document version update and stakeholder review.*
