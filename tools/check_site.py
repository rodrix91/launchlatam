#!/usr/bin/env python3
"""Offline integrity check for the committed LaunchLatam GitHub Pages artifact.

Uses only Python's standard library. No traffic, deployments or credentials.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

BASE = "https://rodrix91.github.io/launchlatam"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title = ""
        self._in_title = False
        self.canonical: list[str] = []
        self.csp: list[str] = []
        self.local_refs: list[str] = []
        self.jsonld: list[str] = []
        self._json_chunks: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang") or ""
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and (a.get("http-equiv") or "").lower() == "content-security-policy":
            self.csp.append(a.get("content") or "")
        elif tag == "link":
            rel = set((a.get("rel") or "").lower().split())
            if "canonical" in rel:
                self.canonical.append(a.get("href") or "")
            if rel.intersection({"stylesheet", "icon", "preload", "modulepreload", "alternate"}):
                self.local_refs.append(a.get("href") or "")
        elif tag in {"a", "script", "img", "source"}:
            field = "href" if tag == "a" else "src"
            if a.get(field):
                self.local_refs.append(a[field] or "")
        if tag == "script" and a.get("type") == "application/ld+json":
            self._json_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._json_chunks is not None:
            self._json_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._json_chunks is not None:
            self.jsonld.append("".join(self._json_chunks))
            self._json_chunks = None


def resolve_local(root: Path, url: str, source: str | None = None) -> Path | None:
    """Resolve project URLs, including document-relative links, inside root only."""
    origin = urlsplit(BASE)
    prefix = origin.path.rstrip("/") + "/"
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise ValueError(f"Unsafe local URL path: {url}") from exc

    if source is not None and not parsed.scheme and not parsed.netloc:
        # An in-page anchor does not refer to a different local file.
        if not parsed.path and not parsed.query:
            return None
        parsed = urlsplit(urljoin(source, url))
        if parsed.netloc == origin.netloc and not parsed.path.startswith(prefix):
            raise ValueError(f"Unsafe local URL path outside project: {url}")

    if parsed.scheme not in {"http", "https"} or parsed.netloc != origin.netloc:
        return None
    if not parsed.path.startswith(prefix):
        return None
    relative = unquote(parsed.path[len(prefix):])
    parts = Path(relative).parts
    if ".." in parts or "\\" in relative or relative.startswith("/") or "\x00" in relative:
        raise ValueError(f"Unsafe local URL path: {url}")

    target = root.joinpath(*parts)
    if parsed.path.endswith("/") or target.is_dir():
        target = target / "index.html"
    # A symlink inside a build could redirect a nominally local link outside
    # the artifact. Reject traversal even when target.is_file() is True.
    try:
        if not target.resolve(strict=False).is_relative_to(root.resolve(strict=False)):
            raise ValueError(f"Unsafe local URL path: {url}")
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Unsafe local URL path: {url}") from exc
    return target


def check(root: Path) -> list[str]:
    failures: list[str] = []

    def require(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)

    sitemap = root / "sitemap.xml"
    require(sitemap.is_file(), "Missing sitemap.xml")
    if not sitemap.is_file():
        return failures
    try:
        xml = ElementTree.parse(sitemap)
    except ElementTree.ParseError as exc:
        return [f"Invalid sitemap.xml: {exc}"]

    pages: list[str] = []
    for item in xml.findall(f"{SITEMAP_NS}url"):
        loc = item.findtext(f"{SITEMAP_NS}loc") or ""
        lastmod = item.findtext(f"{SITEMAP_NS}lastmod") or ""
        require(loc.startswith(BASE + "/"), f"Sitemap URL outside project: {loc}")
        require(bool(lastmod), f"Missing lastmod: {loc}")
        if lastmod:
            try:
                date.fromisoformat(lastmod)
            except ValueError:
                failures.append(f"Invalid ISO lastmod {lastmod}: {loc}")
        if loc:
            pages.append(loc)
    require(len(pages) >= 10, f"Unexpectedly small sitemap: {len(pages)} URLs")
    require(len(pages) == len(set(pages)), "Duplicate sitemap entries")
    for expected in (BASE + "/", BASE + "/pt/", BASE + "/en/", BASE + "/escaneo/"):
        require(expected in pages, f"Missing key page from sitemap: {expected}")

    for loc in pages:
        try:
            path = resolve_local(root, loc)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if not path or not path.is_file():
            failures.append(f"Sitemap target missing: {loc}")
            continue
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            failures.append(f"Could not parse {path}: {exc}")
            continue
        require(bool(parser.title.strip()), f"Missing title: {loc}")
        require(bool(parser.lang.strip()), f"Missing html lang: {loc}")
        require(parser.canonical == [loc], f"Canonical mismatch: {loc} -> {parser.canonical}")
        require(len(parser.csp) == 1, f"Expected one Content-Security-Policy: {loc}")
        for policy in parser.csp:
            require("object-src 'none'" in policy, f"CSP missing object-src restriction: {loc}")
            require("base-uri 'self'" in policy, f"CSP missing base-uri restriction: {loc}")
            require("PLACEHOLDER" not in policy, f"Unprocessed CSP placeholder: {loc}")
        for i, body in enumerate(parser.jsonld, 1):
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                failures.append(f"Invalid JSON-LD script {i} at {loc}: {exc}")
        for ref in set(parser.local_refs):
            try:
                target = resolve_local(root, ref, source=loc)
            except ValueError as exc:
                failures.append(str(exc))
                continue
            if target is not None:
                require(target.is_file(), f"Broken internal link on {loc}: {ref}")

    robots = root / "robots.txt"
    require(robots.is_file(), "Missing robots.txt")
    if robots.is_file():
        require(f"Sitemap: {BASE}/sitemap.xml" in robots.read_text(encoding="utf-8"),
                "robots.txt points to the wrong sitemap")
    manifest = root / "site.webmanifest"
    require(manifest.is_file(), "Missing web manifest")
    if manifest.is_file():
        try:
            m = json.loads(manifest.read_text(encoding="utf-8"))
            require(m.get("start_url") == "/launchlatam/", "Wrong manifest start_url")
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid web manifest: {exc}")
    return failures


if __name__ == "__main__":
    location = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "site"
    errors = check(location)
    if errors:
        for err in errors:
            print(f"FAIL {err}", file=sys.stderr)
        print(f"Site integrity: {len(errors)} issue(s)", file=sys.stderr)
        sys.exit(1)
    print("Site integrity OK: sitemap, canonical URLs, local links, JSON-LD, CSP, robots and manifest")
