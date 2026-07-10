import re
import urllib.request
import ssl
import fitz

pdf_urls = {
    'HIT approved fees': 'https://www.hit.ac.zw/wp-content/uploads/2026/03/scan-fees-structure.pdf',
    'GSU fees structure': 'https://www.gsu.ac.zw/wp-content/uploads/2025/12/fees-tuitiona-and-structure.pdf',
    'GSU MPhil DPhil fees': 'https://www.gsu.ac.zw/wp-content/uploads/2025/06/Mphil-Dphil-Fees-Structure-1.pdf',
    'AU fee payment plan': 'https://africau.edu/resource/Fee_payment_plan.pdf',
    'AU fee structure 2025': 'https://africau.edu/resource/Fee_structure_2025.PDF',
    'Solusi fees': 'https://solusi.ac.zw/assets/FEES STRUCTURE Updated (1).pdf',
    'LSU fee notice': 'https://lsu.ac.zw/storage/notices/5vcAoHXSSnJbwA8IKxEvKVYYayo4ndXreChB356U.pdf'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/pdf,*/*;q=0.9',
    'Accept-Language': 'en-US,en;q=0.5',
}
context = ssl._create_unverified_context()

for name, url in pdf_urls.items():
    url = url.replace(' ', '%20')
    print('===', name, url)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=45, context=context) as r:
            data = r.read()
        doc = fitz.open(stream=data, filetype='pdf')
        text = []
        for i, page in enumerate(doc, start=1):
            text.append(page.get_text())
        text = '\n'.join(text)
        text_sample = text[:4000].replace('\r','')
        print('pages', doc.page_count, 'chars', len(text), 'sample:')
        print(text_sample)
        matches = re.findall(r'\b(?:USD|ZWL|ZWG|TZS|R(?:\$| )?\w*|dollars?|dollar|fee|tuition|bank|total|balance|account|payment|payable|deposit|per semester|per year|per annum|annual)\b[^\n]*', text, flags=re.I)
        print('matches', len(matches))
        for m in matches[:30]:
            print('-', m.strip())
    except Exception as e:
        print('ERROR', type(e).__name__, e)
    print()