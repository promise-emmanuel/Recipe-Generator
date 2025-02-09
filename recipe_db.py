import sqlite3

def create_db():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_data TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
create_db()