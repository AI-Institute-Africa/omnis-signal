from app.scraping.normalization_loader import load_banking_normalization
import json
rules = load_banking_normalization()
print('rules:', len(rules))
print(json.dumps(rules[:10], indent=2, default=str))
