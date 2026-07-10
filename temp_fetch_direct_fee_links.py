import urllib.request
import re
import ssl
urls = {
    'GZU fees': 'https://www.gzu.ac.zw/fees-structure/',
    'HIT approved fees note': 'https://www.hit.ac.zw/2026/03/05/approved-fees-for-second-semester-january-june-2026/',
    'ZOU fees': 'https://www.zou.ac.zw/fees-2/',
    'GSU fees': 'https://www.gsu.ac.zw/fees-structure/',
    'AU fees': 'https://africau.edu/study-at-au/tuition-and-fees/',
    'WUA fees': 'https://www.wua.ac.zw/fees-and-finance/',
    'Solusi fees': 'https://solusi.ac.zw/fees.php',
    'CUZ home': 'https://cuz.ac.zw/',
    'RCU home': 'https://rcu.ac.zw/',
    'MSU home': 'https://www.msu.ac.zw/',
    'LSU home': 'https://www.lsu.ac.zw/'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

context = ssl._create_unverified_context()

for name, url in urls.items():
    print('===', name, url)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25, context=context) as r:
            content = r.read().decode('utf-8', 'replace')
        print('len', len(content))
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', content, flags=re.I)
        pdfs = [h for h in hrefs if '.pdf' in h.lower()]
        fee_links = [h for h in hrefs if re.search(r'fee|tuition|bursary|bank|account|payment|finance|fees-structure|fees-2', h, flags=re.I)]
        print('pdfs', pdfs[:20])
        print('fee_links', fee_links[:20])
        amounts = re.findall(r'\b(?:USD|ZWL|ZWG|TZS|R\$?|\$)\s*[0-9,]+(?:\.\d{1,2})?\b', content, flags=re.I)
        print('amounts', amounts[:20])
        m = re.search(r'(?is)(USD|ZWL|ZWG|TZS|R[ ]?dollar|Fees|Tuition|Fee|Payment|Account|Bank|Charge|Cost).{0,350}', content)
        print('sample', m.group(0).replace('\n',' ') if m else 'none')
    except Exception as e:
        print('ERROR', e)
