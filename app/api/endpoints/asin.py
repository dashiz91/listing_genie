"""
ASIN Import API Endpoints

Import product data from Amazon by ASIN to auto-fill the listing generator.
"""
import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.core.auth import get_current_user, User
from app.services.amazon_scraper_service import (
    get_amazon_scraper,
    AmazonScraperError,
    AmazonProductData,
)
from app.services.supabase_storage_service import SupabaseStorageService
from app.dependencies import get_storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ASINImportRequest(BaseModel):
    """Request to import product data from Amazon"""
    asin: str = Field(..., description="Amazon Standard Identification Number (10 chars)")
    marketplace: str = Field(default="com", description="Amazon marketplace (com, co.uk, de, etc.)")
    download_images: bool = Field(default=True, description="Whether to download product images")
    max_images: int = Field(default=3, ge=1, le=5, description="Maximum images to download (1-5)")


class ASINImportResponse(BaseModel):
    """Response containing imported product data"""
    asin: str
    title: Optional[str]
    brand_name: Optional[str]
    feature_1: Optional[str]
    feature_2: Optional[str]
    feature_3: Optional[str]
    category: Optional[str]
    image_uploads: List[dict] = []  # List of {upload_id, file_path}
    source_image_urls: List[str] = []  # Original Amazon URLs for reference


@router.post("/import", response_model=ASINImportResponse)
async def import_from_asin(
    request: ASINImportRequest,
    user: User = Depends(get_current_user),
    storage: SupabaseStorageService = Depends(get_storage_service),
):
    """
    Import product data from Amazon by ASIN.

    Scrapes publicly available product information:
    - Product title
    - Brand name
    - Feature bullet points (up to 3)
    - Product images (downloaded and saved as uploads)

    Returns data in a format ready to populate the listing generator form.
    """
    logger.info(f"[ASIN] User {user.id} importing ASIN: {request.asin} (marketplace: {request.marketplace})")

    scraper = get_amazon_scraper()

    try:
        # Fetch product data from Amazon
        product: AmazonProductData = await scraper.fetch_product(
            asin=request.asin,
            marketplace=request.marketplace
        )
    except AmazonScraperError as e:
        logger.warning(f"[ASIN] Scraping failed for {request.asin}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ASIN] Unexpected error for {request.asin}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch product data")

    # Prepare response
    response = ASINImportResponse(
        asin=product.asin,
        title=product.title[:200] if product.title else None,  # Truncate to fit schema
        brand_name=product.brand_name[:100] if product.brand_name else None,
        feature_1=product.features[0][:500] if len(product.features) > 0 else None,
        feature_2=product.features[1][:500] if len(product.features) > 1 else None,
        feature_3=product.features[2][:500] if len(product.features) > 2 else None,
        category=product.category,
        source_image_urls=product.image_urls,
    )

    # Download and save images if requested
    if request.download_images and product.image_urls:
        image_uploads = []
        images_to_download = product.image_urls[:request.max_images]

        for idx, url in enumerate(images_to_download):
            try:
                logger.info(f"[ASIN] Downloading image {idx + 1}/{len(images_to_download)}: {url[:80]}...")

                # Download image
                image_bytes = await scraper.download_image(url)

                # Save to Supabase storage
                upload_id, file_path = storage.save_upload(
                    image_bytes,
                    f"asin_{product.asin}_img{idx + 1}.png"
                )

                image_uploads.append({
                    "upload_id": upload_id,
                    "file_path": file_path,
                })

                logger.info(f"[ASIN] Saved image: {upload_id}")

            except Exception as e:
                # Log error but continue with other images
                logger.warning(f"[ASIN] Failed to download image {idx + 1}: {e}")

        response.image_uploads = image_uploads

    logger.info(f"[ASIN] Import complete for {request.asin}: "
               f"title='{response.title[:30] if response.title else None}...', "
               f"{len(response.image_uploads)} images saved")

    return response


@router.get("/validate/{asin}")
async def validate_asin(
    asin: str,
    user: User = Depends(get_current_user),
):
    """
    Validate ASIN format without fetching product data.

    Returns the normalized ASIN if valid.
    """
    scraper = get_amazon_scraper()

    try:
        normalized = scraper.validate_asin(asin)
        return {"valid": True, "asin": normalized}
    except AmazonScraperError as e:
        return {"valid": False, "error": str(e)}
