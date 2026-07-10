import sqlite3

def check_counts():
    conn = sqlite3.connect('scraper_hub.db')
    cursor = conn.cursor()
    
    tables = ['organizations', 'products', 'services', 'price_entries']
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'Total {table}: {count}')
        except sqlite3.OperationalError as e:
            print(f'Error checking {table}: {e}')
            
    conn.close()

if __name__ == "__main__":
    check_counts()
