import sqlite3

def migrate():
    conn = sqlite3.connect('scraper_hub.db')
    cursor = conn.cursor()
    
    tables_to_update = ['products', 'services']
    
    for table in tables_to_update:
        try:
            print(f"Adding subcategory to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN subcategory TEXT")
            print("Done.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column subcategory already exists in {table}.")
            else:
                print(f"Error updating {table}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
