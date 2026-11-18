"""Offline regression checks for the committed Pages artifact validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

# Import by path so that the site validator need not be a Python package.
MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_site.py"
spec = importlib.util.spec_from_file_location("launchlatam_check_site", MODULE_PATH)
assert spec is not None and spec.loader is not None
site_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site_check)
BASE = site_check.BASE
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class SiteValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "site"
        self.root.mkdir()
        self.urls = ["/", "/pt/", "/en/", "/escaneo/", *(f"/blog/example-{i}/" for i in range(6))]
        assets = self.root / "assets"
        assets.mkdir()
        (assets / "site.css").write_text("body {margin: 0}\n", encoding="utf-8")
        self.pages = {}
        for path in self.urls:
            fp = self.root / path.lstrip("/") / "index.html"
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(self.html(path), encoding="utf-8")
            self.pages[path] = fp
        self.sitemap = self.root / "sitemap.xml"
        ET.register_namespace("", NS)
        doc = ET.Element(f"{{{NS}}}urlset")
        for path in self.urls:
            entry = ET.SubElement(doc, f"{{{NS}}}url")
            ET.SubElement(entry, f"{{{NS}}}loc").text = BASE + path
            ET.SubElement(entry, f"{{{NS}}}lastmod").text = "2026-11-17"
        ET.ElementTree(doc).write(self.sitemap, encoding="unicode", xml_declaration=True)
        (self.root / "robots.txt").write_text(f"Sitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
        (self.root / "site.webmanifest").write_text(
            json.dumps({"name": "Fixture", "start_url": "/launchlatam/"}), encoding="utf-8"
        )

    @staticmethod
    def html(path: str) -> str:
        return (
            '<!doctype html><html lang="es"><head><title>Fixture page</title>'
            f'<link rel="canonical" href="{BASE}{path}">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
            "object-src 'none'; base-uri 'self'\">"
            f'<link rel="stylesheet" href="{BASE}/assets/site.css">'
            '<script type="application/ld+json">{"@type":"WebPage"}</script>'
            f'</head><body><a href="{BASE}/en/">English</a></body></html>'
        )

    def mutate(self, path: str, find: str, replacement: str) -> None:
        fp = self.pages[path]
        text = fp.read_text(encoding="utf-8")
        assert find in text
        fp.write_text(text.replace(find, replacement, 1), encoding="utf-8")

    def assert_reports(self, expected: str) -> None:
        issues = site_check.check(self.root)
        self.assertTrue(any(expected in issue for issue in issues), issues)

    def test_complete_fixture_is_valid(self) -> None:
        self.assertEqual(site_check.check(self.root), [])

    def test_broken_local_link_is_detected_but_external_links_are_not_fetched(self) -> None:
        self.mutate("/", f'{BASE}/en/', f'{BASE}/missing/')
        self.assert_reports("Broken internal link")
        self.mutate("/", f'{BASE}/missing/', "https://example.org/absent")
        self.assertEqual(site_check.check(self.root), [])

    def test_missing_asset_is_detected(self) -> None:
        (self.root / "assets" / "site.css").unlink()
        self.assert_reports("Broken internal link")

    def test_canonical_mismatch_is_detected(self) -> None:
        self.mutate("/", f'canonical" href="{BASE}/', f'canonical" href="{BASE}/en/')
        self.assert_reports("Canonical mismatch")

    def test_invalid_json_ld_is_detected(self) -> None:
        self.mutate("/", '{"@type":"WebPage"}', '{"@type":')
        self.assert_reports("Invalid JSON-LD")

    def test_unsafe_csp_and_unprocessed_placeholder_are_detected(self) -> None:
        self.mutate("/", "object-src 'none'", "object-src 'self'")
        self.assert_reports("CSP missing object-src restriction")
        self.mutate("/", "base-uri 'self'", "base-uri 'self'; PLACEHOLDER")
        self.assert_reports("Unprocessed CSP placeholder")

    def test_duplicate_sitemap_entries_are_detected(self) -> None:
        tree = ET.parse(self.sitemap)
        root = tree.getroot()
        url = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(url, f"{{{NS}}}loc").text = BASE + "/en/"
        ET.SubElement(url, f"{{{NS}}}lastmod").text = "2026-11-17"
        tree.write(self.sitemap, encoding="unicode", xml_declaration=True)
        self.assert_reports("Duplicate sitemap entries")

    def test_invalid_sitemap_lastmod_is_detected(self) -> None:
        tree = ET.parse(self.sitemap)
        tree.getroot().find(f"{{{NS}}}url/{{{NS}}}lastmod").text = "not-a-date"
        tree.write(self.sitemap, encoding="unicode", xml_declaration=True)
        self.assert_reports("Invalid ISO lastmod")

    def test_web_manifest_must_be_valid_and_target_this_project(self) -> None:
        manifest = self.root / "site.webmanifest"
        manifest.write_text("{broken", encoding="utf-8")
        self.assert_reports("Invalid web manifest")
        manifest.write_text('{"start_url":"/wrong-project/"}', encoding="utf-8")
        self.assert_reports("Wrong manifest start_url")

    def test_unsafe_encoded_traversal_url_is_rejected(self) -> None:
        self.mutate("/", f'{BASE}/en/', f'{BASE}/%2E%2E/outside.txt')
        self.assert_reports("Unsafe local URL path")


    def test_valid_document_relative_link_is_checked(self) -> None:
        self.mutate("/", f'{BASE}/en/', "./en/?source=menu#intro")
        self.assertEqual(site_check.check(self.root), [])

    def test_valid_root_relative_project_link_is_checked(self) -> None:
        self.mutate("/", f'{BASE}/en/', "/launchlatam/en/#intro")
        self.assertEqual(site_check.check(self.root), [])

    def test_missing_document_relative_link_is_reported(self) -> None:
        self.mutate("/", f'{BASE}/en/', "./missing-local-target/")
        self.assert_reports("Broken internal link")

    def test_document_relative_parent_navigation_within_site_is_valid(self) -> None:
        self.mutate("/en/", f'<a href="{BASE}/en/"', '<a href="../pt/"')
        self.assertEqual(site_check.check(self.root), [])

    def test_relative_parent_navigation_outside_site_is_unsafe(self) -> None:
        self.mutate("/", f'{BASE}/en/', "../outside/")
        self.assert_reports("Unsafe local URL path outside project")

    def test_encoded_relative_parent_traversal_is_unsafe(self) -> None:
        self.mutate("/", f'{BASE}/en/', "%2e%2e/%2e%2e/secret")
        self.assert_reports("Unsafe local URL path")

    def test_symlink_escape_does_not_validate_external_artifacts(self) -> None:
        outside = Path(self.temp.name) / "outside.css"
        outside.write_text("body{color:red}", encoding="utf-8")
        style = self.root / "assets" / "site.css"
        style.unlink()
        try:
            style.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("Symlinks unavailable on this test runner")
        self.assert_reports("Unsafe local URL path")

    def test_fragment_only_reference_does_not_resolve_as_broken_file(self) -> None:
        self.mutate("/", f'{BASE}/en/', "#main")
        self.assertEqual(site_check.check(self.root), [])



if __name__ == "__main__":
    unittest.main()
