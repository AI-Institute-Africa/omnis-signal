import urllib.request
import re
import ssl

urls = {
    'UZ fees': 'https://www.uz.ac.zw/index.php/current-students/undergraduates/fees',
    'NUST fees': 'https://www.nust.ac.zw/index.php/students/fees-structure/undergraduate-fees.html',
    'MSU fees': 'https://www.msu.ac.zw/',
    'CUT fees': 'https://www.cut.ac.zw/bursary/fees-structure',
    'BUSE fees': 'https://www.buse.ac.zw/',
    'GZU fees': 'https://www.gzu.ac.zw/',
    'HIT fees': 'https://www.hit.ac.zw/',
    'ZOU fees': 'https://www.zou.ac.zw/',
    'LSU fees': 'https://www.lsu.ac.zw/',
    'GSU fees': 'https://www.gsu.ac.zw/',
    'AU fees': 'https://www.africau.edu/',
    'WUA fees': 'https://www.wua.ac.zw/',
    'CUZ fees': 'https://www.cuz.ac.zw/',
    'Solusi fees': 'https://www.solusi.ac.zw/',
    'RCU fees': 'https://www.rcu.ac.zw/'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/'
}

def safe_fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            return r.status, r.geturl(), r.read().decode('utf-8', 'replace')
    except Exception as e:
        return None, None, str(e)

for name, url in urls.items():
    print('===', name, url)
    status, final, content = safe_fetch(url)
    print('status=', status, 'final=', final)
    if status != 200:
        print('error', content[:300])
        continue
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', content, flags=re.I)
    pdfs = [h for h in hrefs if '.pdf' in h.lower()]
    fee_links = [h for h in hrefs if re.search(r'fee|tuition|bursary|bank|account|pdf|charge|cost|payment', h, flags=re.I)]
    print('pdfs', pdfs[:20])
    print('fee_links', fee_links[:20])
    m = re.search(r'(?is)(fee|tuition|bursary|bank|account|cost|payment).{0,250}', content)
    print('sample', m.group(0).replace('\n',' ') if m else 'none')
