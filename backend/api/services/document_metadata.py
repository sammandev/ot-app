from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests
from django.utils import timezone


METADATA_REQUEST_TIMEOUT = (3.05, 5)
METADATA_MAX_BYTES = 512 * 1024
HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}
REQUEST_HEADERS = {
    "User-Agent": "PTB-OT-DocumentsBot/1.0 (+internal)",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
}


class LinkMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_chunks = []
        self.meta = {}
        self.links = []

    def handle_starttag(self, tag, attrs):
        normalized_attrs = {key.lower(): value for key, value in attrs if key and value}
        if tag == "title":
            self.in_title = True
            return
        if tag == "meta":
            key = (normalized_attrs.get("property") or normalized_attrs.get("name") or "").strip().lower()
            content = (normalized_attrs.get("content") or "").strip()
            if key and content and key not in self.meta:
                self.meta[key] = content
            return
        if tag == "link":
            rel = (normalized_attrs.get("rel") or "").strip().lower()
            href = (normalized_attrs.get("href") or "").strip()
            if rel and href:
                self.links.append({"rel": rel, "href": href})

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and data:
            self.title_chunks.append(data)

    @property
    def title(self):
        return " ".join(part.strip() for part in self.title_chunks if part.strip()).strip()


def _extract_html(response):
    chunks = []
    total = 0
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
        if not chunk:
            continue
        if total >= METADATA_MAX_BYTES:
            break
        remaining = METADATA_MAX_BYTES - total
        truncated = chunk[:remaining]
        chunks.append(truncated)
        total += len(truncated)

    encoding = response.encoding or response.apparent_encoding or "utf-8"
    return b"".join(chunks).decode(encoding, errors="replace")


def _absolute_url(base_url, maybe_relative_url):
    if not maybe_relative_url:
        return ""
    return urljoin(base_url, maybe_relative_url.strip())


def fetch_link_metadata(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc or parsed_url.path or url

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=METADATA_REQUEST_TIMEOUT, allow_redirects=True, stream=True)
        response.raise_for_status()

        content_type = (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type and content_type not in HTML_CONTENT_TYPES:
            return {
                "normalized_url": response.url or url,
                "link_title": "",
                "link_description": "",
                "link_site_name": host,
                "link_favicon_url": "",
                "link_image_url": "",
                "metadata_status": "failed",
                "metadata_error": f"Unsupported content type: {content_type}",
                "metadata_fetched_at": timezone.now(),
            }

        html = _extract_html(response)
        parser = LinkMetadataParser()
        parser.feed(html)

        final_url = response.url or url
        og_title = parser.meta.get("og:title", "")
        og_description = parser.meta.get("og:description", "")
        meta_description = parser.meta.get("description", "")
        og_site_name = parser.meta.get("og:site_name", "")
        og_image = parser.meta.get("og:image", "")
        favicon = ""

        for link in parser.links:
            if "icon" in link["rel"]:
                favicon = link["href"]
                break

        resolved_host = urlparse(final_url).netloc or host
        return {
            "normalized_url": final_url,
            "link_title": og_title or parser.title,
            "link_description": og_description or meta_description,
            "link_site_name": og_site_name or resolved_host,
            "link_favicon_url": _absolute_url(final_url, favicon),
            "link_image_url": _absolute_url(final_url, og_image),
            "metadata_status": "success",
            "metadata_error": "",
            "metadata_fetched_at": timezone.now(),
        }
    except requests.RequestException as exc:
        return {
            "normalized_url": url,
            "link_title": "",
            "link_description": "",
            "link_site_name": host,
            "link_favicon_url": "",
            "link_image_url": "",
            "metadata_status": "failed",
            "metadata_error": str(exc)[:500],
            "metadata_fetched_at": timezone.now(),
        }