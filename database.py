import sqlite3
from datetime import datetime

def setup_database():
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            category_id INTEGER,
            start_time TEXT NOT NULL,
            end_time TEXT,
            notes TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_category(name):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Category '{name}' already exists.")
    finally:
        conn.close()

def get_categories():
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()
    return categories

def delete_category(category_id):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()

def start_tracking(task_name, category_id, notes):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO time_entries (task_name, category_id, start_time, notes) VALUES (?, ?, ?, ?)",
        (task_name, category_id, start_time, notes)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def stop_tracking(entry_id, task_name, notes):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("UPDATE time_entries SET end_time = ?, task_name = ?, notes = ? WHERE id = ?", (end_time, task_name, notes, entry_id))
    conn.commit()
    conn.close()

def add_manual_entry(task_name, category_id, start_time, end_time, notes):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO time_entries (task_name, category_id, start_time, end_time, notes) VALUES (?, ?, ?, ?, ?)",
        (task_name, category_id, start_time, end_time, notes)
    )
    conn.commit()
    conn.close()

def update_entry(entry_id, task_name, category_id, start_time, end_time, notes):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE time_entries SET task_name=?, category_id=?, start_time=?, end_time=?, notes=? WHERE id=?",
        (task_name, category_id, start_time, end_time, notes, entry_id)
    )
    conn.commit()
    conn.close()

def delete_entry(entry_id):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_entry_by_id(entry_id):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM time_entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    conn.close()
    return entry

def get_entries_by_date_range(start_date, end_date):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    query = """
        SELECT te.id, te.task_name, c.name, te.start_time, te.end_time, te.notes
        FROM time_entries te
        LEFT JOIN categories c ON te.category_id = c.id
        WHERE date(te.start_time) >= ? AND date(te.start_time) <= ?
        ORDER BY te.start_time DESC
    """
    cursor.execute(query, (start_date, end_date))
    entries = cursor.fetchall()
    conn.close()
    return entries

def search_entries_by_keyword(keyword):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    search_term = f'%{keyword}%'
    query = """
        SELECT te.id, te.task_name, c.name, te.start_time, te.end_time, te.notes
        FROM time_entries te
        LEFT JOIN categories c ON te.category_id = c.id
        WHERE te.task_name LIKE ? OR c.name LIKE ?
        ORDER BY te.start_time DESC
    """
    cursor.execute(query, (search_term, search_term))
    entries = cursor.fetchall()
    conn.close()
    return entries

def get_category_id_by_name(name):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def is_category_used(category_id):
    conn = sqlite3.connect('timetracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM time_entries WHERE category_id = ?", (category_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0