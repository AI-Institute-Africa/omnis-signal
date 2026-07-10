import sqlite3

def check_db():
    conn = sqlite3.connect('scraper_hub.db')
    cursor = conn.cursor()
    
    print("=== Tables ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        t_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
        count = cursor.fetchone()[0]
        print(f"{t_name}: {count} records")
    
    print("\n=== Sample Organizations ===")
    cursor.execute("SELECT name, category FROM organizations LIMIT 5")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    check_db()