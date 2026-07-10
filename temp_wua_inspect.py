import ssl
import urllib.request

url = 'https://www.wua.ac.zw/fees-and-finance/'
ctx = ssl._create_unverified_context()
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html',
})
with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
    html = r.read().decode('utf-8', 'replace')
print(html.count('Fees for Local students'))
for i, line in enumerate(html.splitlines(), 1):
    if any(k in line for k in ['Fees for Local students', 'Total Fees per Semester', 'Diploma Programmes', 'Sociology', 'Psychology', 'USD', 'EUR', 'ZWL', '531', '534', '375', '415', '571', '415']):
        print(i, line)
print('\n---- CONTEXT ----')
import re
for m in re.finditer(r'(<td[^>]*>.*?</td>)+', html, flags=re.I|re.S):
    chunk = m.group(0)
    if any(k in chunk for k in ['Total Fees per Semester', 'Diploma Programmes', 'Sociology', 'Psychology', 'USD', 'ZWL', '531', '534', '375', '415', '571']):
        print(chunk[:1200])
