"""Fast PR check: the static app under app/ is self-contained.

Passes while app/ is still empty (multi-stage objectives); once
app/index.html exists, every local src/href must exist and nothing may be
loaded from another origin.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

APP = Path(__file__).resolve().parent.parent / "app"


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("src", "href") and value:
                self.refs.append(value)


def main() -> int:
    index = APP / "index.html"
    if not index.is_file():
        print("app/index.html not created yet; nothing to check")
        return 0
    failures = []
    for page in APP.rglob("*.html"):
        parser = Refs()
        parser.feed(page.read_text(encoding="utf-8"))
        for ref in parser.refs:
            if ref.startswith(("#", "data:")):
                continue
            if "//" in ref or ref.startswith(("http:", "https:")):
                failures.append(f"{page.relative_to(APP)}: external resource {ref}")
                continue
            target = (page.parent / ref.split("?")[0].split("#")[0]).resolve()
            if APP.resolve() not in target.parents or not target.is_file():
                failures.append(f"{page.relative_to(APP)}: missing local file {ref}")
    for failure in failures:
        print("::error title=smoke::" + failure)
    print("smoke:", "FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
