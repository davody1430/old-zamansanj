# ==========================================================
#  File: database.py  (بازنویسی کامل + بهبودهای عملیاتی)
# ==========================================================
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional


# ------------------------------------------------------------------
# 1) آدرس پایگاه‌داده (در صورت نیاز می‌توان از متغیر محیطی خواند)
# ------------------------------------------------------------------
DB_FILE = "timetracker.db"


# ------------------------------------------------------------------
# 2) Context-Manager برای اتصال‌های پایگاه‌داده
# ------------------------------------------------------------------
class Connection:
    """Context-Manager جهت باز/بسته کردن خودکار اتصال SQLite"""
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")  # فعال‌سازی کلید خارجی
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()


# ------------------------------------------------------------------
# 3) ساخت جداول (در صورت عدم وجود)
# ------------------------------------------------------------------
def setup_database() -> None:
    """ساخت جداول categories و time_entries در صورت عدم وجود"""
    with Connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name   TEXT NOT NULL,
                category_id INTEGER,
                start_time  TEXT NOT NULL,
                end_time    TEXT,
                notes       TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
            )
        """)


# ------------------------------------------------------------------
# 4) عملیات مربوط به جدول categories
# ------------------------------------------------------------------
def add_category(name: str) -> bool:
    """افزودن دسته‌ی جدید. در صورت موفقیت True، در صورت تکراری بودن False"""
    try:
        with Connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
            return True
    except sqlite3.IntegrityError:
        # نام تکراری
        return False


def get_categories() -> List[Tuple[int, str]]:
    """دریافت لیست تمام دسته‌ها به صورت (id, name)"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name COLLATE NOCASE")
        return cursor.fetchall()


def delete_category(category_id: int) -> bool:
    """حذف دسته بر اساس شناسه. در صورت موفقیت True"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return cursor.rowcount > 0


def update_category_name(category_id: int, new_name: str) -> bool:
    """به‌روزرسانی نام دسته. در صورت موفقیت True، در صورت تکراری بودن False"""
    try:
        with Connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (new_name.strip(), category_id)
            )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False


def get_category_id_by_name(name: str) -> Optional[int]:
    """دریافت شناسه دسته بر اساس نام. اگر نباشد None برمی‌گرداند"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else None


def is_category_used(category_id: int) -> bool:
    """آیا دسته‌ای در جدول time_entries استفاده شده؟"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM time_entries WHERE category_id = ?",
            (category_id,)
        )
        return cursor.fetchone()[0] > 0


# ------------------------------------------------------------------
# 5) عملیات مربوط به جدول time_entries
# ------------------------------------------------------------------
def start_tracking(task_name: str, category_id: Optional[int], notes: str) -> int:
    """شروع رکورد جدید و بازگرداندن شناسه‌ی آن"""
    with Connection() as conn:
        cursor = conn.cursor()
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO time_entries (task_name, category_id, start_time, notes)
            VALUES (?, ?, ?, ?)
            """,
            (task_name.strip(), category_id, start_time, notes.strip())
        )
        return cursor.lastrowid  # type: ignore


def stop_tracking(entry_id: int, task_name: str, notes: str) -> None:
    """توقف رکورد جاری و ثبت زمان پایان"""
    with Connection() as conn:
        cursor = conn.cursor()
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            UPDATE time_entries
            SET end_time = ?, task_name = ?, notes = ?
            WHERE id = ?
            """,
            (end_time, task_name.strip(), notes.strip(), entry_id)
        )


def add_manual_entry(
    task_name: str,
    category_id: Optional[int],
    start_time: str,
    end_time: str,
    notes: str
) -> None:
    """درج یک رکورد کامل به صورت دستی"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO time_entries (task_name, category_id, start_time, end_time, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_name.strip(), category_id, start_time, end_time, notes.strip())
        )


def update_entry(
    entry_id: int,
    task_name: str,
    category_id: Optional[int],
    start_time: str,
    end_time: Optional[str],
    notes: str
) -> None:
    """به‌روزرسانی یک رکورد موجود"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE time_entries
            SET task_name   = ?,
                category_id = ?,
                start_time  = ?,
                end_time    = ?,
                notes       = ?
            WHERE id = ?
            """,
            (task_name.strip(), category_id, start_time, end_time, notes.strip(), entry_id)
        )


def delete_entry(entry_id: int) -> bool:
    """حذف یک رکورد بر اساس شناسه. در صورت موفقیت True"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
        return cursor.rowcount > 0


def get_entry_by_id(entry_id: int) -> Optional[tuple]:
    """دریافت یک رکورد خاص بر اساس شناسه"""
    with Connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM time_entries WHERE id = ?", (entry_id,))
        return cursor.fetchone()


def get_entries_by_date_range(start_date: str, end_date: str) -> List[tuple]:
    """
    دریافت رکوردها در بازه‌ی تاریخی مشخص
    :param start_date: رشته‌ی تاریخ شروع (YYYY-MM-DD)
    :param end_date: رشته‌ی تاریخ پایان (YYYY-MM-DD)
    :return: لیست tupleها
    """
    with Connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT te.id,
                   te.task_name,
                   c.name,
                   te.start_time,
                   te.end_time,
                   te.notes
            FROM time_entries te
            LEFT JOIN categories c ON te.category_id = c.id
            WHERE te.start_time >= ? AND te.start_time < ?
            ORDER BY te.start_time DESC
        """
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()


def search_entries_by_keyword(keyword: str) -> List[tuple]:
    """جست‌وجو در عنوان کار و نام دسته"""
    with Connection() as conn:
        cursor = conn.cursor()
        search_term = f"%{keyword}%"
        query = """
            SELECT te.id,
                   te.task_name,
                   c.name,
                   te.start_time,
                   te.end_time,
                   te.notes
            FROM time_entries te
            LEFT JOIN categories c ON te.category_id = c.id
            WHERE te.task_name LIKE ? OR c.name LIKE ?
            ORDER BY te.start_time DESC
        """
        cursor.execute(query, (search_term, search_term))
        return cursor.fetchall()