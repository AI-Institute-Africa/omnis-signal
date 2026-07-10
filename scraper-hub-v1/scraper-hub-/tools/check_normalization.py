import sys, os
# ensure project root is on sys.path
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from app.scraping.extractors import banking
import json

rules = banking.BANKING_SERVICE_NORMALIZATION
print('total_rules:', len(rules))
external = [r for r in rules if r.get('source_bank')]
print('external_rules_count:', len(external))
if external:
    print('sample_external:')
    for r in external[:5]:
        print(json.dumps({'pattern': r.get('pattern'), 'title': r.get('title'), 'subcategory': r.get('subcategory'), 'source_bank': r.get('source_bank')}, ensure_ascii=False))

print('sample_rules:')
for r in rules[:10]:
    print(json.dumps({
        'pattern': r.get('pattern'),
        'title': r.get('title'),
        'subcategory': r.get('subcategory'),
        'source_bank': r.get('source_bank') if 'source_bank' in r else None
    }, ensure_ascii=False))
