#!/usr/bin/env python3
"""
Security Screen Reference Image Scraper

Scrapes product images from Boss Security Screens and American Security Screens,
classifies them using Claude's vision API, and organizes them into a reference library.
"""

import os
import sys
import json
import hashlib
import time
import re
import base64
import struct
import zlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Configuration
SITES_TO_SCRAPE = [
    {
        "name": "bosssecurityscreens",
        "pages": [
            "https://bosssecurityscreens.com/",
            "https://bosssecurityscreens.com/security-doors",
            "https://bosssecurityscreens.com/security-window-screens",
        ]
    },
    {
        "name": "americansecurityscreens",
        "pages": [
            "https://americansecurityscreens.com/gallery",
            "https://americansecurityscreens.com/residential",
        ]
    }
]

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MEDIA_DIR = PROJECT_ROOT / "media" / "references"
RAW_DIR = MEDIA_DIR / "_raw"
REJECTED_DIR = MEDIA_DIR / "_rejected"

# Categories
CATEGORIES = [
    "windows",
    "patios",
    "doors/single",
    "doors/french",
    "doors/sliding",
    "doors/accordion",
]

# Request settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REQUEST_DELAY = 1.0  # seconds between requests
MIN_IMAGE_SIZE = 200  # pixels

# Track downloaded URLs to avoid duplicates
downloaded_urls = set()
downloaded_hashes = set()


def log(message: str, level: str = "INFO"):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_image_size_from_url(url: str) -> tuple[int, int] | None:
    """Try to get image dimensions from URL without downloading full image."""
    try:
        # Request just the first few KB to get image header
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()

        # Read first 32KB which should contain image header
        data = b""
        for chunk in response.iter_content(chunk_size=1024):
            data += chunk
            if len(data) >= 32768:
                break

        # Try to get dimensions from partial data
        img = Image.open(BytesIO(data))
        return img.size
    except Exception:
        return None


def download_image(url: str, save_path: Path) -> bool:
    """Download an image and convert webp to png if needed."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get("content-type", "")
        if not any(t in content_type for t in ["image/", "application/octet-stream"]):
            log(f"Not an image: {url} (type: {content_type})", "WARN")
            return False

        # Load image
        img = Image.open(BytesIO(response.content))

        # Check size
        width, height = img.size
        if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
            log(f"Image too small ({width}x{height}): {url}", "SKIP")
            return False

        # Check for duplicate by content hash
        content_hash = hashlib.md5(response.content).hexdigest()
        if content_hash in downloaded_hashes:
            log(f"Duplicate image (by hash): {url}", "SKIP")
            return False
        downloaded_hashes.add(content_hash)

        # Convert to RGB if necessary (for PNG saving)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            # Keep alpha channel
            img = img.convert("RGBA")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Save as PNG
        save_path = save_path.with_suffix(".png")
        img.save(save_path, "PNG", optimize=True)
        log(f"Downloaded: {save_path.name} ({width}x{height})")
        return True

    except Exception as e:
        log(f"Failed to download {url}: {e}", "ERROR")
        return False


def extract_image_urls(html: str, base_url: str) -> list[str]:
    """Extract all image URLs from HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    urls = set()

    # Find all <img> tags
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if src:
            full_url = urljoin(base_url, src)
            urls.add(full_url)

        # Also check srcset
        srcset = img.get("srcset")
        if srcset:
            for part in srcset.split(","):
                src_part = part.strip().split()[0]
                if src_part:
                    full_url = urljoin(base_url, src_part)
                    urls.add(full_url)

    # Find background images in style attributes
    for elem in soup.find_all(style=True):
        style = elem["style"]
        # Match url(...) patterns
        matches = re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
        for match in matches:
            full_url = urljoin(base_url, match)
            urls.add(full_url)

    # Find <a> tags linking to images
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(href.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
            full_url = urljoin(base_url, href)
            urls.add(full_url)

    # Filter to likely image URLs
    image_urls = []
    for url in urls:
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        # Skip obvious non-product images
        if any(skip in path_lower for skip in ["logo", "icon", "favicon", "sprite", "placeholder"]):
            continue

        # Check for image extensions or image-like URLs
        if any(path_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
            image_urls.append(url)
        elif "image" in url.lower() or "photo" in url.lower() or "gallery" in url.lower():
            image_urls.append(url)

    return image_urls


def scrape_page(url: str) -> list[str]:
    """Scrape a single page for image URLs."""
    log(f"Scraping: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        image_urls = extract_image_urls(response.text, url)
        log(f"Found {len(image_urls)} potential images")
        return image_urls

    except Exception as e:
        log(f"Failed to scrape {url}: {e}", "ERROR")
        return []


def scrape_all_sites() -> dict[str, list[str]]:
    """Scrape all configured sites and return image URLs by source."""
    all_images = {}

    for site in SITES_TO_SCRAPE:
        site_name = site["name"]
        site_images = []

        for page_url in site["pages"]:
            images = scrape_page(page_url)
            for img_url in images:
                if img_url not in downloaded_urls:
                    site_images.append(img_url)
                    downloaded_urls.add(img_url)

            time.sleep(REQUEST_DELAY)

        all_images[site_name] = site_images
        log(f"Total unique images from {site_name}: {len(site_images)}")

    return all_images


def download_all_images(images_by_site: dict[str, list[str]]) -> list[dict]:
    """Download all images and return metadata."""
    downloaded = []

    for site_name, urls in images_by_site.items():
        for i, url in enumerate(urls):
            # Generate filename
            parsed = urlparse(url)
            original_name = Path(parsed.path).stem
            safe_name = re.sub(r'[^\w\-]', '_', original_name)[:50]
            filename = f"{site_name}_{safe_name}_{i:03d}"
            save_path = RAW_DIR / f"{filename}.png"

            # Skip if already downloaded
            if save_path.exists():
                log(f"Already exists: {save_path.name}", "SKIP")
                continue

            # Download
            if download_image(url, save_path):
                downloaded.append({
                    "filename": save_path.name,
                    "source_url": url,
                    "site": site_name,
                    "path": str(save_path),
                })

            time.sleep(REQUEST_DELAY * 0.5)  # Shorter delay for images

    return downloaded


def classify_image_with_claude(image_path: Path) -> dict:
    """
    Classify an image using Claude's vision API.

    Note: This requires the Anthropic API key to be set.
    Falls back to a basic heuristic if API is not available.
    """
    try:
        import anthropic

        client = anthropic.Anthropic()

        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Determine media type
        suffix = image_path.suffix.lower()
        media_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(suffix, "image/png")

        prompt = """Look at this security screen product image.

CLASSIFY INTO ONE CATEGORY:
- windows: Security screen installed on a window
- patios: Patio enclosure (floor-to-ceiling screen walls)
- doors/single: Single entry door with security screen
- doors/french: French doors (double doors that swing)
- doors/sliding: Sliding glass door with security screen
- doors/accordion: Accordion/folding door system
- _rejected: Not a product image (logo, diagram, lifestyle photo without clear product, too blurry)

RESPOND WITH JSON ONLY:
{
    "category": "windows" | "patios" | "doors/single" | "doors/french" | "doors/sliding" | "doors/accordion" | "_rejected",
    "confidence": <1-10>,
    "description": "brief description of what's shown",
    "rejection_reason": "only if _rejected, explain why"
}"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        # Parse JSON response
        response_text = response.content[0].text

        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            log(f"Could not parse JSON from response: {response_text[:100]}", "WARN")
            return {
                "category": "_rejected",
                "confidence": 1,
                "description": "Failed to parse classification",
                "rejection_reason": "API response parse error"
            }

    except ImportError:
        log("Anthropic library not installed, using filename heuristics", "WARN")
        return classify_by_filename(image_path)
    except Exception as e:
        log(f"Classification error for {image_path.name}: {e}", "ERROR")
        return {
            "category": "_rejected",
            "confidence": 1,
            "description": "Classification failed",
            "rejection_reason": str(e)
        }


def classify_by_filename(image_path: Path) -> dict:
    """Fallback classification based on filename heuristics."""
    name_lower = image_path.stem.lower()

    # Strong keyword matching - higher confidence
    # Windows
    if any(w in name_lower for w in ["window", "wndw", "casement"]):
        return {"category": "windows", "confidence": 7, "description": "Detected window keyword in filename"}

    # Patios - very specific keywords
    if any(w in name_lower for w in ["patio", "enclosure", "sunroom", "lanai", "screened_in", "pool_cage"]):
        return {"category": "patios", "confidence": 7, "description": "Detected patio keyword in filename"}

    # French doors
    if any(w in name_lower for w in ["french", "double_door"]):
        return {"category": "doors/french", "confidence": 7, "description": "Detected french door keyword in filename"}

    # Sliding doors
    if any(w in name_lower for w in ["sliding", "slider", "slide"]):
        return {"category": "doors/sliding", "confidence": 7, "description": "Detected sliding door keyword in filename"}

    # Accordion doors
    if any(w in name_lower for w in ["accordion", "folding", "bi_fold", "bifold"]):
        return {"category": "doors/accordion", "confidence": 7, "description": "Detected accordion door keyword in filename"}

    # Generic doors - check for door keywords but not window/patio context
    if any(w in name_lower for w in ["door", "entry", "front_door", "security_door", "screen_door"]):
        # Default to single unless other indicators
        return {"category": "doors/single", "confidence": 6, "description": "Detected door keyword in filename"}

    # Security screen generic - could be anything, but likely a product
    if any(w in name_lower for w in ["security_screen", "screen", "meshtec", "crimsafe"]):
        # Can't determine type, but likely valid product - mark for review
        return {"category": "_rejected", "confidence": 5, "description": "Security screen product, needs manual review", "rejection_reason": "Could not determine specific category"}

    # Reject obvious non-products
    if any(w in name_lower for w in ["logo", "icon", "banner", "hero", "team", "about", "contact"]):
        return {"category": "_rejected", "confidence": 8, "description": "Non-product image", "rejection_reason": "Marketing/website asset"}

    # Unknown - reject but note for review
    return {"category": "_rejected", "confidence": 4, "description": "Unknown category", "rejection_reason": "Could not determine category from filename"}


def classify_and_organize(downloaded_images: list[dict]) -> list[dict]:
    """Classify all downloaded images and move to appropriate folders."""
    classified = []

    for img_data in downloaded_images:
        image_path = Path(img_data["path"])
        if not image_path.exists():
            continue

        log(f"Classifying: {image_path.name}")

        # Get classification
        result = classify_image_with_claude(image_path)

        category = result.get("category", "_rejected")
        confidence = result.get("confidence", 1)

        # If low confidence, reject
        if confidence < 5 and category != "_rejected":
            log(f"Low confidence ({confidence}), rejecting: {image_path.name}", "WARN")
            result["rejection_reason"] = f"Low confidence: {confidence}"
            category = "_rejected"

        # Determine destination folder
        if category == "_rejected":
            dest_folder = REJECTED_DIR
        else:
            dest_folder = MEDIA_DIR / category

        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / image_path.name

        # Move file
        if image_path != dest_path:
            image_path.rename(dest_path)
            log(f"Moved to: {category}/{image_path.name}")

        # Update metadata
        img_data.update({
            "category": category,
            "confidence": confidence,
            "description": result.get("description", ""),
            "rejection_reason": result.get("rejection_reason"),
            "classified_path": str(dest_path),
        })

        classified.append(img_data)

        # Small delay to avoid rate limiting on API
        time.sleep(0.5)

    return classified


def generate_manifest(classified_images: list[dict]) -> dict:
    """Generate the manifest.json file."""
    # Count by category
    counts = {}
    for img in classified_images:
        cat = img.get("category", "_rejected")
        counts[cat] = counts.get(cat, 0) + 1

    # Get sources
    sources = list(set(img.get("site", "unknown") for img in classified_images))

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "sources": [f"{s}.com" for s in sources],
        "counts": counts,
        "images": [
            {
                "filename": img["filename"],
                "category": img.get("category", "_rejected"),
                "source_url": img.get("source_url", ""),
                "confidence": img.get("confidence", 0),
                "description": img.get("description", ""),
            }
            for img in classified_images
            if img.get("category") != "_rejected"
        ]
    }

    # Save manifest
    manifest_path = MEDIA_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    log(f"Manifest saved to: {manifest_path}")
    return manifest


def print_summary(manifest: dict, total_found: int, total_rejected: int, low_confidence: list):
    """Print the final quality report."""
    counts = manifest.get("counts", {})
    total_classified = sum(v for k, v in counts.items() if k != "_rejected")

    print("\n" + "=" * 50)
    print("=== Reference Image Scrape Complete ===")
    print("=" * 50)
    print(f"\nSources scraped: {len(manifest.get('sources', []))} sites")
    print(f"Total images found: {total_found}")
    print(f"Successfully classified: {total_classified}")
    print(f"Rejected: {total_rejected}")
    print("\nBy category:")

    for cat in CATEGORIES:
        count = counts.get(cat, 0)
        print(f"  {cat:20} {count:3}")

    if low_confidence:
        print(f"\nLow confidence (<7): {len(low_confidence)} images (review recommended)")
        for img in low_confidence[:5]:
            print(f"  - {img['filename']} (confidence: {img.get('confidence', 0)})")

    print(f"\nManifest saved to: {MEDIA_DIR / 'manifest.json'}")
    print("=" * 50)


def main():
    """Main entry point."""
    log("Starting security screen reference image scraper")

    # Ensure directories exist
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        (MEDIA_DIR / cat).mkdir(parents=True, exist_ok=True)

    # Step 1: Scrape all sites
    log("=" * 40)
    log("STEP 1: Scraping websites for images")
    log("=" * 40)
    images_by_site = scrape_all_sites()
    total_found = sum(len(urls) for urls in images_by_site.values())
    log(f"Total unique images found: {total_found}")

    # Step 2: Download images
    log("=" * 40)
    log("STEP 2: Downloading images")
    log("=" * 40)
    downloaded = download_all_images(images_by_site)
    log(f"Successfully downloaded: {len(downloaded)} images")

    # Also include any existing images in _raw that weren't just downloaded
    existing_raw = list(RAW_DIR.glob("*.png"))
    for raw_file in existing_raw:
        if not any(d["filename"] == raw_file.name for d in downloaded):
            downloaded.append({
                "filename": raw_file.name,
                "source_url": "existing",
                "site": "unknown",
                "path": str(raw_file),
            })

    if not downloaded:
        log("No images to classify", "WARN")
        return

    # Step 3: Classify and organize
    log("=" * 40)
    log("STEP 3: Classifying images")
    log("=" * 40)
    classified = classify_and_organize(downloaded)

    # Step 4: Generate manifest
    log("=" * 40)
    log("STEP 4: Generating manifest")
    log("=" * 40)
    manifest = generate_manifest(classified)

    # Find low confidence images for review
    low_confidence = [
        img for img in classified
        if img.get("confidence", 0) < 7 and img.get("category") != "_rejected"
    ]

    total_rejected = sum(1 for img in classified if img.get("category") == "_rejected")

    # Print summary
    print_summary(manifest, total_found, total_rejected, low_confidence)


if __name__ == "__main__":
    main()
