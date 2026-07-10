import sqlite3
conn = sqlite3.connect('scraper_hub.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get sample records
cur.execute('''SELECT title, billing_period, unit_type, unit_value, entity_name 
               FROM extracted_records 
               LIMIT 20''')

print("Sample records:")
for row in cur.fetchall():
    print(f"Title: {row['title']}")
    print(f"  billing_period: {repr(row['billing_period'])}")
    print(f"  unit: {row['unit_type']} {row['unit_value']}")
    print()

# Count by billing_period
print("\n\nBilling period distribution:")
cur.execute('''SELECT billing_period, COUNT(*) as cnt 
               FROM extracted_records 
               GROUP BY billing_period 
               ORDER BY cnt DESC''')
for row in cur.fetchall():
    print(f"{repr(row['billing_period'])}: {row['cnt']}")

conn.close()
