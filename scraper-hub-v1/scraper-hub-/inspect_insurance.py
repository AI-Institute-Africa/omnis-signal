import sqlite3
from bs4 import BeautifulSoup

# Check Fidelity Life - they had 83KB of content
conn = sqlite3.connect('scraper_hub.db')
cursor = conn.cursor()
cursor.execute("SELECT content FROM raw_snapshots WHERE id = 331")
content = cursor.fetchone()[0]
conn.close()

soup = BeautifulSoup(content, 'html.parser')
for tag in soup(['script','style','nav','footer','header']): tag.decompose()
text = soup.get_text(separator='\n', strip=True)
lines = [l for l in text.split('\n') if len(l.strip()) > 3]
print(f"Fidelity Life total text lines: {len(lines)}")
print('\n'.join(lines[:60]))
print('\n--- Searching for pricing/plan keywords ---')
for i, line in enumerate(lines):
    if any(k in line.lower() for k in ['usd','$','plan','premium','cover','policy','funeral','life','assurance','benefit','monthly']):
        print(f'[{i}] {line[:120]}')
