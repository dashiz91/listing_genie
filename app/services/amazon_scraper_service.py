"""
Amazon ASIN Scraper Service

Scrapes publicly available product data from Amazon product pages.
Used to auto-fill listing generator form from an existing Amazon listing.
"""
import re
import logging
import asyncio
from dataclasses import dataclass
from typing import List, Optional, Tuple
from io import BytesIO

import httpx
from bs4 import BeautifulSoup
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# User agents to rotate (looks like real browsers)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


@dataclass
class AmazonProductData:
    """Data extracted from Amazon product page"""
    asin: str
    title: Optional[str] = None
    brand_name: Optional[str] = None
    features: List[str] = None  # Bullet points
    image_urls: List[str] = None  # Product image URLs
    category: Optional[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.image_urls is None:
            self.image_urls = []


class AmazonScraperError(Exception):
    """Custom exception for scraping failures"""
    pass


class AmazonScraperService:
    """
    Scrapes Amazon product pages to extract listing data.

    Uses BeautifulSoup with httpx for async HTTP requests.
    Implements basic anti-detection measures (user-agent rotation, delays).
    """

    def __init__(self):
        self.timeout = 30.0
        self._ua_index = 0

    def _get_headers(self) -> dict:
        """Get request headers with rotating user agent"""
        ua = USER_AGENTS[self._ua_index % len(USER_AGENTS)]
        self._ua_index += 1

        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def validate_asin(self, asin: str) -> str:
        """
        Validate and normalize ASIN format.

        ASINs are 10-character alphanumeric strings.
        Can start with B0 (most products) or numbers (books/ISBN).
        """
        # Remove whitespace and convert to uppercase
        asin = asin.strip().upper()

        # Remove common prefixes users might include
        if asin.startswith("ASIN:"):
            asin = asin[5:].strip()
        if asin.startswith("AMAZON.COM/DP/"):
            asin = asin[14:].strip()

        # Extract ASIN from full URL if pasted
        url_match = re.search(r'/dp/([A-Z0-9]{10})', asin, re.IGNORECASE)
        if url_match:
            asin = url_match.group(1).upper()

        # Validate format: 10 alphanumeric characters
        if not re.match(r'^[A-Z0-9]{10}$', asin):
            raise AmazonScraperError(
                f"Invalid ASIN format: '{asin}'. ASIN must be 10 alphanumeric characters."
            )

        return asin

    async def fetch_product(self, asin: str, marketplace: str = "com") -> AmazonProductData:
        """
        Fetch product data from Amazon by ASIN.

        Args:
            asin: Amazon Standard Identification Number
            marketplace: Amazon marketplace domain (com, co.uk, de, etc.)

        Returns:
            AmazonProductData with extracted information

        Raises:
            AmazonScraperError on network or parsing failures
        """
        # Validate ASIN
        asin = self.validate_asin(asin)

        # Build URL
        url = f"https://www.amazon.{marketplace}/dp/{asin}"
        logger.info(f"Fetching Amazon product: {url}")

        # Fetch with retries
        max_retries = 3
        last_error = None

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            for attempt in range(max_retries):
                try:
                    # Add delay between retries
                    if attempt > 0:
                        await asyncio.sleep(2 * attempt)

                    response = await client.get(url, headers=self._get_headers())

                    # Check for bot detection
                    if response.status_code == 503:
                        logger.warning(f"Amazon returned 503 (bot detection) on attempt {attempt + 1}")
                        last_error = AmazonScraperError("Amazon detected automated access. Please try again later.")
                        continue

                    if response.status_code == 404:
                        raise AmazonScraperError(f"Product not found: ASIN {asin}")

                    response.raise_for_status()

                    # Parse the HTML
                    return self._parse_product_page(asin, response.text)

                except httpx.TimeoutException:
                    logger.warning(f"Timeout on attempt {attempt + 1} for ASIN {asin}")
                    last_error = AmazonScraperError("Request timed out. Amazon may be slow or blocking requests.")
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error {e.response.status_code} for ASIN {asin}")
                    last_error = AmazonScraperError(f"Failed to fetch product: HTTP {e.response.status_code}")

        # All retries failed
        raise last_error or AmazonScraperError("Failed to fetch product after multiple attempts")

    def _parse_product_page(self, asin: str, html: str) -> AmazonProductData:
        """Parse Amazon product page HTML to extract data"""
        soup = BeautifulSoup(html, 'lxml')

        # Check for CAPTCHA page
        if soup.find('form', {'action': '/errors/validateCaptcha'}):
            raise AmazonScraperError("Amazon is showing a CAPTCHA. Please try again later.")

        # Extract product data
        product = AmazonProductData(asin=asin)

        # Title
        product.title = self._extract_title(soup)

        # Brand
        product.brand_name = self._extract_brand(soup)

        # Features (bullet points)
        product.features = self._extract_features(soup)

        # Images
        product.image_urls = self._extract_images(soup)

        # Category
        product.category = self._extract_category(soup)

        logger.info(f"Parsed ASIN {asin}: title='{product.title[:50] if product.title else None}...', "
                   f"{len(product.features)} features, {len(product.image_urls)} images")

        return product

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title"""
        # Primary: productTitle span
        title_elem = soup.find('span', {'id': 'productTitle'})
        if title_elem:
            return title_elem.get_text(strip=True)

        # Fallback: title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove " : Amazon.com" suffix
            title = re.sub(r'\s*:\s*Amazon\.com.*$', '', title)
            return title

        return None

    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand name"""
        # Method 1: bylineInfo link
        byline = soup.find('a', {'id': 'bylineInfo'})
        if byline:
            text = byline.get_text(strip=True)
            # Remove "Visit the X Store" or "Brand: X"
            text = re.sub(r'^(Visit the |Brand:\s*)', '', text)
            text = re.sub(r'\s+Store$', '', text)
            return text

        # Method 2: Brand row in product details
        brand_row = soup.find('tr', class_='po-brand')
        if brand_row:
            value = brand_row.find('span', class_='po-break-word')
            if value:
                return value.get_text(strip=True)

        # Method 3: Product details table
        for th in soup.find_all('th'):
            if 'brand' in th.get_text().lower():
                td = th.find_next_sibling('td')
                if td:
                    return td.get_text(strip=True)

        return None

    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product feature bullet points"""
        features = []

        # Primary: feature-bullets section
        bullets_div = soup.find('div', {'id': 'feature-bullets'})
        if bullets_div:
            for li in bullets_div.find_all('li'):
                # Skip hidden items
                if 'aok-hidden' in li.get('class', []):
                    continue

                span = li.find('span', class_='a-list-item')
                if span:
                    text = span.get_text(strip=True)
                    if text and len(text) > 5:  # Skip very short items
                        features.append(text)

        # Fallback: aboutThisItem section
        if not features:
            about_div = soup.find('div', {'id': 'aboutThisItem'})
            if about_div:
                for li in about_div.find_all('li'):
                    text = li.get_text(strip=True)
                    if text and len(text) > 5:
                        features.append(text)

        # Limit to first 5 features
        return features[:5]

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product image URLs"""
        image_urls = []

        # Method 1: Main image
        main_img = soup.find('img', {'id': 'landingImage'})
        if main_img:
            # Get high-res version from data-old-hires or src
            src = main_img.get('data-old-hires') or main_img.get('src')
            if src and 'no-image' not in src.lower():
                # Convert to high-res URL
                src = self._get_hires_url(src)
                image_urls.append(src)

        # Method 2: Thumbnail images (for additional angles)
        thumb_container = soup.find('div', {'id': 'altImages'})
        if thumb_container:
            for img in thumb_container.find_all('img'):
                src = img.get('src')
                if src and 'sprite' not in src.lower() and 'no-image' not in src.lower():
                    # Convert thumbnail to full-size
                    src = self._get_hires_url(src)
                    if src not in image_urls:
                        image_urls.append(src)

        # Method 3: Check for image data in scripts (newer Amazon layout)
        for script in soup.find_all('script'):
            script_text = script.string or ''
            # Look for colorImages JSON
            match = re.search(r'"hiRes"\s*:\s*"([^"]+)"', script_text)
            if match:
                url = match.group(1).replace('\\/', '/')
                if url not in image_urls:
                    image_urls.append(url)

        # Limit to first 5 images
        return image_urls[:5]

    def _get_hires_url(self, url: str) -> str:
        """Convert Amazon image URL to high-resolution version"""
        if not url:
            return url

        # Remove size constraints from URL
        # Pattern: ._SX300_ or ._SS40_ etc
        url = re.sub(r'\._[A-Z]{2}\d+_', '.', url)
        url = re.sub(r'\._[A-Z]{2}\d+,[A-Z]+_', '.', url)

        # Replace common low-res indicators
        url = url.replace('._SL1500_', '.')
        url = url.replace('._AC_UL', '._AC_SL1500')

        return url

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product category from breadcrumbs"""
        breadcrumb = soup.find('div', {'id': 'wayfinding-breadcrumbs_feature_div'})
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if links:
                # Return the last (most specific) category
                return links[-1].get_text(strip=True)

        return None

    async def download_image(self, url: str) -> bytes:
        """
        Download an image from URL and return as bytes.

        Validates that the response is actually an image.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._get_headers())
            response.raise_for_status()

            # Validate it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise AmazonScraperError(f"URL did not return an image: {content_type}")

            # Validate and re-encode image
            try:
                image = Image.open(BytesIO(response.content))
                image = image.convert('RGB')

                # Save to bytes
                output = BytesIO()
                image.save(output, format='PNG', optimize=True)
                output.seek(0)
                return output.getvalue()
            except Exception as e:
                raise AmazonScraperError(f"Failed to process image: {e}")


# Singleton instance
_scraper_instance: Optional[AmazonScraperService] = None


def get_amazon_scraper() -> AmazonScraperService:
    """Get or create singleton scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = AmazonScraperService()
    return _scraper_instance
