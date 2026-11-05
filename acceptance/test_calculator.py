"""Fixed acceptance suite for reference X (reference/calculator.md).

Owned by the fixture, not by the agents that build `app/`. It serves `app/`
locally, drives it with headless Chromium and checks behaviour, keyboard use,
layout, colours and self-containment. Exit code 0 only if every check passes.
"""
from __future__ import annotations

import functools
import os
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
PORT = 8123
TOLERANCE = 12
COLOURS = {"digit": (0x26, 0x32, 0x41), "function": (0x4A, 0x5A, 0x6E),
           "operator": (0xE0, 0x7A, 0x2E), "panel": (0x10, 0x15, 0x1C),
           "page": (0x0A, 0x0D, 0x12), "white": (0xFF, 0xFF, 0xFF)}
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f" ({detail})" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)
        if "GITHUB_ACTIONS" in os.environ:
            print(f"::error title=acceptance::{name} {detail}")


def rgb(value: str) -> tuple[int, ...] | None:
    if not value.startswith("rgb"):
        return None
    inside = value[value.index("(") + 1:value.index(")")].split(",")
    return tuple(int(float(part)) for part in inside[:3])


def near(value: str, colour: tuple[int, int, int]) -> bool:
    got = rgb(value)
    return got is not None and all(abs(a - b) <= TOLERANCE for a, b in zip(got, colour))


def serve() -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(APP))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    if not (APP / "index.html").is_file():
        print("FAIL app/index.html is missing")
        return 1
    server = serve()
    external: list[str] = []
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 360, "height": 640})

        def route(r):
            url = r.request.url
            if url.startswith(f"http://127.0.0.1:{PORT}/") or url.startswith("data:"):
                r.continue_()
            else:
                external.append(url)
                r.abort()
        page.route("**/*", route)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"http://127.0.0.1:{PORT}/index.html")
        page.wait_for_selector("#display")
        display = page.locator("#display")

        def shown() -> str:
            return display.inner_text().strip()

        def press(*keys: str) -> str:
            for key in keys:
                page.locator(f'button[data-key="{key}"]').click()
            return shown()

        # Behaviour through clicks.
        check("starts at 0", shown() == "0", shown())
        check("12 + 7 = 19", press("1", "2", "+", "7", "=") == "19", shown())
        check("AC resets", press("clear") == "0", shown())
        check("immediate execution 2+3*4=20", press("2", "+", "3", "*", "4", "=") == "20", shown())
        press("clear")
        check("0.1 + 0.2 = 0.3", press("0", ".", "1", "+", "0", ".", "2", "=") == "0.3", shown())
        press("clear")
        check("1 / 3 rounded to 12 digits",
              press("1", "/", "3", "=") == "0.333333333333", shown())
        press("clear")
        check("division by zero shows Error", press("1", "/", "0", "=") == "Error", shown())
        check("digit after Error starts again", press("5") == "5", shown())
        press("clear")
        check("sign negates", press("5", "sign") == "-5", shown())
        press("clear")
        check("percent divides by 100", press("5", "0", "percent") == "0.5", shown())
        press("clear")
        check("second operator replaces the first", press("9", "+", "-", "3", "=") == "6", shown())
        press("clear")
        check("subtraction 8 - 10 = -2", press("8", "-", "1", "0", "=") == "-2", shown())

        # Behaviour through the keyboard.
        page.keyboard.press("Escape")
        check("Escape clears", shown() == "0", shown())
        for key in ("8", "*", "7", "Enter"):
            page.keyboard.press(key)
        check("keyboard 8*7 Enter = 56", shown() == "56", shown())
        page.keyboard.press("Escape")
        for key in ("1", "2", "Backspace", "+", "1", "="):
            page.keyboard.press(key)
        check("Backspace and = key", shown() == "2", shown())

        # Layout and visual fidelity against reference X.
        boxes = {}
        keys = ["clear", "sign", "percent", "/", "7", "8", "9", "*", "4", "5", "6", "-",
                "1", "2", "3", "+", "0", ".", "="]
        for key in keys:
            boxes[key] = page.locator(f'button[data-key="{key}"]').bounding_box()
        check("all 19 keys rendered", all(boxes.values()))
        if all(boxes.values()):
            cx = {k: b["x"] + b["width"] / 2 for k, b in boxes.items()}
            cy = {k: b["y"] + b["height"] / 2 for k, b in boxes.items()}
            rows = [["clear", "sign", "percent", "/"], ["7", "8", "9", "*"],
                    ["4", "5", "6", "-"], ["1", "2", "3", "+"], [".", "="]]
            cols = [["clear", "7", "4", "1"], ["sign", "8", "5", "2"],
                    ["percent", "9", "6", "3", "."], ["/", "*", "-", "+", "="]]
            check("rows aligned", all(max(cy[k] for k in r) - min(cy[k] for k in r) <= 4 for r in rows))
            check("rows ordered top to bottom",
                  all(cy[a[0]] < cy[b[0]] for a, b in zip(rows, rows[1:])))
            check("4 aligned columns", all(max(cx[k] for k in c) - min(cx[k] for k in c) <= 4 for c in cols))
            check("columns ordered left to right",
                  all(cx[a[0]] < cx[b[0]] for a, b in zip(cols, cols[1:])))
            zero, one, two = boxes["0"], boxes["1"], boxes["2"]
            check("0 spans columns 1-2",
                  abs(zero["x"] - one["x"]) <= 6
                  and abs((zero["x"] + zero["width"]) - (two["x"] + two["width"])) <= 6
                  and abs(cy["0"] - cy["."]) <= 4)
            check("keys at least 44x44", all(b["width"] >= 44 and b["height"] >= 44
                                             for k, b in boxes.items()))
            dbox = display.bounding_box()
            check("display above keypad", dbox is not None and dbox["y"] + dbox["height"] <= boxes["clear"]["y"] + 1)

        def style(selector: str, prop: str) -> str:
            return page.eval_on_selector(selector, f"e => getComputedStyle(e).{prop}")
        groups = {"digit": ["0", "1", "5", "9", "."], "function": ["clear", "sign", "percent"],
                  "operator": ["/", "*", "-", "+", "="]}
        for group, members in groups.items():
            values = [style(f'button[data-key="{k}"]', "backgroundColor") for k in members]
            check(f"{group} key colour", all(near(v, COLOURS[group]) for v in values), ", ".join(values))
        check("key text white", near(style('button[data-key="7"]', "color"), COLOURS["white"]))
        check("panel colour", near(style("#calculator", "backgroundColor"), COLOURS["panel"]),
              style("#calculator", "backgroundColor"))
        page_bg = style("body", "backgroundColor")
        if page_bg.replace(" ", "").endswith(",0)"):  # transparent body
            page_bg = style("html", "backgroundColor")
        check("page colour", near(page_bg, COLOURS["page"]), page_bg)
        size = float(style("#display", "fontSize").replace("px", ""))
        check("display font at least 40px", size >= 40, str(size))
        align = style("#display", "textAlign") + " " + style("#display", "justifyContent")
        check("display right aligned", any(w in align for w in ("right", "end", "flex-end")), align)
        check("display text white", near(style("#display", "color"), COLOURS["white"]))
        check("no horizontal scroll at 360px",
              page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        page.screenshot(path=str(ROOT / "acceptance-screenshot.png"), full_page=True)
        browser.close()
    server.shutdown()
    check("no external resources", not external, ", ".join(external[:3]))
    check("no page errors", not errors, "; ".join(errors[:3]))
    print(f"SUMMARY {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
