import sqlite3
conn = sqlite3.connect('scraper_hub.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get NetOne bundle records
cur.execute('''
SELECT 
  title, 
  description,
  unit_value, 
  unit_type,
  billing_period
FROM extracted_records 
WHERE entity_name = 'NetOne ZW' AND (title LIKE '%Bundle%' OR title LIKE '%Bundles%')
LIMIT 15
''')

print("NetOne Bundle Records:")
print("=" * 100)
for row in cur.fetchall():
    print(f"Title: {row['title']}")
    print(f"  Description: {row['description'][:100] if row['description'] else 'None'}")
    print(f"  unit_value: {repr(row['unit_value'])}, unit_type: {repr(row['unit_type'])}")
    print(f"  billing_period: {repr(row['billing_period'])}")
    print()

conn.close()
