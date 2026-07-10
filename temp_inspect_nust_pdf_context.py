from pathlib import Path
import re
text = Path('nust_undergrad_fees.pdf').read_bytes().decode('latin-1', errors='ignore')
for pat in ['610.56', '829.44', '2544', '3456']:
    print('===', pat)
    for m in re.finditer(re.escape(pat), text):
        start = max(0, m.start() - 120)
        end = min(len(text), m.end() + 120)
        print(text[start:end].replace('\n', ' '))
        print('---')
