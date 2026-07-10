import urllib.request
import re
urls = [
    'https://www.uz.ac.zw/index.php/admissions/international-students/tuition-fees',
    'https://www.nust.ac.zw/index.php/students/fees-structure/undergraduate-fees.html',
    'https://www.cut.ac.zw/bursary/fees-structure'
]
for url in urls:
    print('===', url)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            c = r.read().decode('utf-8', 'replace')
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', c, flags=re.I)
        pdfs = [h for h in hrefs if '.pdf' in h.lower()]
        fees = [h for h in hrefs if re.search(r'fee|tuition|bursary|bank|account', h, flags=re.I)]
        print('pdfs', pdfs)
        print('fee-related links', fees[:20])
        m = re.search(r'(?s)(Tuition Fees|Fees|fee|undergraduate|Payment|account|bursary).{0,400}', c)
        print('raw', m.group(0) if m else '')
    except Exception as e:
        print('ERROR', e)
