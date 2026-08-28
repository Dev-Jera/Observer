"""Digital Eye scraper: fetch approved sources, extract items, dedupe via fingerprints."""
import hashlib
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from ..database import SessionLocal
from .. import models
from .sources import APPROVED_SOURCES
from ..ai.pipeline import process_content
from ..services.sms import queue_notification

logger = logging.getLogger("citizeneye.eye")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CitizenEyeBot/1.0; +https://citizeneye.app)"
}
ROBOTS_USER_AGENT = "CitizenEyeBot"
TIMEOUT = 20.0
ROBOTS_CACHE: dict[str, RobotFileParser | None] = {}


def fingerprint(url: str, title: str) -> str:
    raw = f"{url.strip().lower()}|{title.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def scraping_allowed(url: str) -> bool:
    """Honor robots.txt before requesting a source or discovered article."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url not in ROBOTS_CACHE:
        try:
            response = httpx.get(robots_url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
            if response.status_code in (401, 403):
                ROBOTS_CACHE[robots_url] = None
            else:
                parser = RobotFileParser()
                parser.parse(response.text.splitlines() if response.status_code == 200 else [])
                ROBOTS_CACHE[robots_url] = parser
        except httpx.HTTPError:
            ROBOTS_CACHE[robots_url] = None
    parser = ROBOTS_CACHE[robots_url]
    return parser is not None and parser.can_fetch(ROBOTS_USER_AGENT, url)


def fetch_page(url: str) -> str | None:
    if not scraping_allowed(url):
        logger.info("Skipping disallowed source: %s", url)
        return None
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None


def extract_content(html: str, limit: int = 12000) -> str:
    """Return readable page text for the AI pipeline."""
    soup = BeautifulSoup(html, "xml" if "<rss" in html[:500].lower() or "<feed" in html[:500].lower() else "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    blocks = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = " ".join(element.get_text(" ", strip=True).split())
        if text and text not in blocks:
            blocks.append(text)
    return "\n\n".join(blocks)[:limit] or " ".join(soup.get_text(" ", strip=True).split())[:limit]


def extract_image_url(html: str, base_url: str) -> str:
    """Find a publisher-provided preview image for smartphone clients."""
    soup = BeautifulSoup(html, "html.parser")
    image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
    value = image.get("content", "").strip() if image else ""
    return urljoin(base_url, value) if value else ""


def extract_items(html: str, base_url: str, limit: int = 10) -> list[dict]:
    """Extract candidate content items (links with titles) from an HTML page."""
    soup = BeautifulSoup(html, "xml" if "<rss" in html[:500].lower() or "<feed" in html[:500].lower() else "html.parser")
    items = []
    seen_urls = set()
    rss_items = soup.find_all("item")
    if rss_items:
        for rss_item in rss_items[:limit]:
            title = rss_item.find("title")
            link = rss_item.find("link")
            description = rss_item.find("description")
            title_text = title.get_text(" ", strip=True) if title else ""
            href = link.get_text(strip=True) if link else ""
            if title_text and href.startswith("http"):
                items.append({"url": href, "title": title_text, "content": description.get_text(" ", strip=True) if description else ""})
        return items
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"].strip()
        if not title or len(title) < 25:
            continue
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(base_url, href)
        if not href.startswith("http") or href in seen_urls:
            continue
        # skip nav / boilerplate links
        skip_words = ("login", "contact", "about", "privacy policy", "terms", "home page")
        if any(w in title.lower() for w in skip_words):
            continue
        seen_urls.add(href)
        items.append({"url": href, "title": title})
        if len(items) >= limit:
            break
    return items


def run_scrape() -> dict:
    """One full pass over all approved sources. Returns stats."""
    stats = {"checked_sources": 0, "new_items": 0, "skipped_duplicates": 0, "errors": []}

    for source in APPROVED_SOURCES:
        stats["checked_sources"] += 1
        html = fetch_page(source["url"])
        if html is None:
            stats["errors"].append(f"fetch failed: {source['name']}")
            continue

        items = extract_items(html, source["url"])
        db = SessionLocal()
        try:
            for item in items:
                fp = fingerprint(item["url"], item["title"])
                exists = db.query(models.SeenContent).filter_by(fingerprint=fp).first()
                if exists:
                    stats["skipped_duplicates"] += 1
                    continue

                item_html = fetch_page(item["url"])
                item["content"] = extract_content(item_html) if item_html else item.get("content", "")
                item["image_url"] = extract_image_url(item_html, item["url"]) if item_html else ""

                # Mark as seen first so failures don't loop forever
                db.add(models.SeenContent(
                    fingerprint=fp, url=item["url"], title=item["title"]
                ))

                processed = process_content(
                    title=item["title"],
                    url=item["url"],
                    source_name=source["name"],
                    content=item["content"],
                )
                article = models.Article(
                    title=processed["title"],
                    category=source["kind"].upper(),
                    topic=processed["topic"],
                    summary=processed["summary"],
                    full_text=processed["full_text"],
                    jurisdiction=processed["jurisdiction"],
                    plain_explanation=processed["plain_explanation"],
                    original_wording=processed["original_wording"],
                    law_citation=processed["law_citation"],
                    amendment_history=processed["amendment_history"],
                    source_name=source["name"],
                    source_url=item["url"],
                    image_url=item["image_url"],
                    rights_impact=processed["rights_impact"],
                    dyk_text=processed["dyk_text"],
                    sms_text=processed["sms_text"],
                    is_live=True,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(article)

                notification = models.Notification(
                    title=processed["title"],
                    message=processed["summary"],
                    sms_text=(processed["sms_text"] or processed["summary"]) + f" Read: {item['url']}",
                    image_url=item["image_url"],
                    source_name=source["name"],
                    source_url=item["url"],
                    source_reference=processed["source_reference"],
                    source_quote=processed["source_quote"],
                    tag=source["kind"].upper(),
                    is_read=False,
                )
                db.add(notification)

                db.flush()
                queue_notification(db, notification)
                db.commit()
                stats["new_items"] += 1
        except Exception as exc:
            db.rollback()
            logger.exception("Error processing %s", source["name"])
            stats["errors"].append(f"processing failed: {source['name']}: {exc}")
        finally:
            db.close()

    return stats
