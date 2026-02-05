"""
Style Library API Endpoints

Serves the pre-generated style library for users to browse without credits.
"""
from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel

from app.data.style_library import (
    get_all_styles,
    get_style_by_id,
    get_styles_by_category,
    get_categories,
)

router = APIRouter(prefix="/styles", tags=["styles"])


class StylePreset(BaseModel):
    """A pre-generated style preset."""
    id: str
    name: str
    category: str
    description: str
    colors: List[str]
    preview_image: str
    tags: List[str]


class CategoryInfo(BaseModel):
    """Category with description."""
    id: str
    name: str
    description: str


class StyleLibraryResponse(BaseModel):
    """Full style library response."""
    categories: List[CategoryInfo]
    styles: List[StylePreset]


@router.get("", response_model=StyleLibraryResponse)
async def get_style_library():
    """
    Get the complete style library with categories and all styles.

    This endpoint is free - no credits required. Users can browse
    styles and use them as starting points for their listings.
    """
    categories = get_categories()
    styles = get_all_styles()

    return StyleLibraryResponse(
        categories=[
            CategoryInfo(id=cat_id, name=cat_id.replace("-", " ").title(), description=desc)
            for cat_id, desc in categories.items()
        ],
        styles=[StylePreset(**s) for s in styles]
    )


@router.get("/category/{category_id}", response_model=List[StylePreset])
async def get_styles_in_category(category_id: str):
    """Get all styles in a specific category."""
    styles = get_styles_by_category(category_id)
    return [StylePreset(**s) for s in styles]


@router.get("/{style_id}", response_model=StylePreset)
async def get_style(style_id: str):
    """Get a specific style by ID."""
    style = get_style_by_id(style_id)
    if not style:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Style not found: {style_id}")
    return StylePreset(**style)
