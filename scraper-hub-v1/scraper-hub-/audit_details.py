
import httpx
import re

BASE = "http://127.0.0.1:8000"

def extract_context(body, keyword, context=100):
    """Extract surrounding context around each keyword occurrence."""
    results = []
    lower_body = body.lower()
    lower_kw = keyword.lower()
    start = 0
    while True:
        idx = lower_body.find(lower_kw, start)
        if idx == -1:
            break
        snippet = body[max(0, idx-context):idx+context+len(keyword)]
        # Strip tags for readability
        clean = re.sub(r'<[^>]+>', ' ', snippet).strip()
        clean = ' '.join(clean.split())
        results.append(clean)
        start = idx + 1
    return results

print("=" * 70)
print("SOURCES PAGE - 'None' occurrences")
print("=" * 70)
r = httpx.get(BASE + "/sources", timeout=15)
body = r.text

# Find all None occurrences
nones = extract_context(body, ">None<")
if not nones:
    nones = extract_context(body, "None")

seen = set()
for ctx in nones[:15]:  # first 15
    if ctx not in seen:
        seen.add(ctx)
        print(f"  >> {ctx[:200]}")

print()
print("=" * 70)
print("RECORDS PAGE - '500' occurrences")
print("=" * 70)
r2 = httpx.get(BASE + "/records", timeout=30)
body2 = r2.text

five_hundreds = extract_context(body2, "500", context=80)
seen2 = set()
for ctx in five_hundreds[:10]:
    if ctx not in seen2:
        seen2.add(ctx)
        print(f"  >> {ctx[:200]}")

print()
print("Done.")
