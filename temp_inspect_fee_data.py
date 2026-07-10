import urllib.request
import re
import ssl

urls = [
    'https://www.uz.ac.zw/index.php/admissions/international-students/tuition-fees',
]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive', 'Referer': 'https://www.google.com/'}

for url in urls:
    print('===', url)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            c = r.read().decode('utf-8', 'replace')
        print('length', len(c))
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', c, flags=re.I)
        pdfs = [h for h in hrefs if '.pdf' in h.lower()]
        fees = [h for h in hrefs if re.search(r'fee|tuition|bursary|bank|account', h, flags=re.I)]
        print('pdfs', pdfs)
        print('fee links', fees[:30])
        for m in re.finditer(r'(?is)(fee|fees|tuition|ZWL|USD|bank|account|pdf|structure|payment).{0,300}', c):
            print('MATCH', m.group(0).replace('\n', ' ')[:250])
    except Exception as e:
        print('ERROR', e)

# inspect NUST PDF bytes for numeric and currency hints
pdf_path = 'nust_undergrad_fees.pdf'
print('=== NUST PDF inspection', pdf_path)
try:
    data = open(pdf_path, 'rb').read()
    text = data.decode('latin-1', errors='ignore')
    matches = re.findall(r'\b(?:USD|ZWL|US\$|ZWL|fee|fees|tuition|undergrad|undergraduate)\b.{0,200}', text, flags=re.I)
    print('matches', len(matches))
    for m in matches[:40]:
        print(m.replace('\n', ' '))
    digits = re.findall(r'\b\d{3,}[\.,]?\d{0,2}\b', text)
    print('digit examples', digits[:50])
except Exception as e:
    print('ERROR PDF', e)
