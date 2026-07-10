
import httpx
import sys

BASE = "http://127.0.0.1:8000"

PAGES = {
    "Dashboard":     "/",
    "Sources":       "/sources",
    "Records":       "/records",
    "Catalog":       "/catalog",
    "Services":      "/services",
    "Intelligence":  "/intelligence",
    "Compare":       "/compare",
    "Manual Scrape": "/manual-scrape",
}

ERROR_KEYWORDS = [
    "Internal Server Error",
    "Traceback",
    "jinja2.exceptions",
    "AttributeError",
    "TypeError",
    "UndefinedError",
    "TemplateError",
    "500",
    "error occurred",
    "NoneType",
]

def check(name, path):
    url = BASE + path
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        status = r.status_code
        body = r.text

        issues = []
        for kw in ERROR_KEYWORDS:
            if kw.lower() in body.lower():
                issues.append(f"[WARN] Contains keyword: '{kw}'")

        # Check for empty main content blocks
        if "<table" not in body and "<div class=\"row" not in body:
            issues.append("[WARN] Possibly empty page (no table or row grid found)")

        if "None" in body:
            count = body.count("None")
            issues.append(f"[WARN] Found 'None' string {count}x in rendered HTML (possible null data)")

        # Check for missing Bootstrap JS (needed for dropdowns)
        if "bootstrap" not in body.lower():
            issues.append("[WARN] Bootstrap not referenced")

        print(f"\n{'='*60}")
        print(f"  {name} ({path})  ->  HTTP {status}")
        print(f"  Response size: {len(body):,} bytes")
        if issues:
            for i in issues:
                print(f"  {i}")
        else:
            print("  [OK] No obvious issues detected")

    except Exception as e:
        print(f"\n  [ERROR] FAILED to reach {name} ({path}): {e}")

print("\nScraper Hub - Full Page Audit")
for name, path in PAGES.items():
    check(name, path)
print("\nAudit complete.\n")
