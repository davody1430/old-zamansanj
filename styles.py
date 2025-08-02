# تنظیمات اصلی تم
LIGHT_THEME = "litera"
DARK_THEME = "superhero"

# فونت‌ها
TIMER_FONT = ("Vazirmatn", 20, "bold")
DEFAULT_FONT = ("Vazirmatn", 10)

# استایل ویجت‌ها
FRAME_STYLE_INFO = "info"
BUTTON_PRIMARY = "primary"
BUTTON_SECONDARY = "secondary"
BUTTON_SUCCESS = "success"
BUTTON_DANGER = "danger"
BUTTON_INFO = "info"

# تنظیمات جدول اصلی
TREEVIEW_STYLE = "primary"
TREEVIEW_SCROLLBAR_STYLE = "round-primary"
TREEVIEW_COLUMN_ORDER = ("task_name", "category", "duration", "end_time", "start_time", "day_of_week", "date")
TREEVIEW_HEADINGS = {
    "date": "تاریخ", 
    "day_of_week": "روز هفته", 
    "start_time": "ساعت شروع",
    "end_time": "ساعت پایان", 
    "duration": "مدت زمان", 
    "category": "دسته",
    "task_name": "عنوان فعالیت",
}
TREEVIEW_COLUMNS_CONFIG = {
    "date": {"width": 100, "anchor": "center"}, 
    "day_of_week": {"width": 100, "anchor": "center"},
    "start_time": {"width": 100, "anchor": "center"}, 
    "end_time": {"width": 100, "anchor": "center"},
    "duration": {"width": 100, "anchor": "center"}, 
    "category": {"width": 150, "anchor": "e"},
    "task_name": {"width": 400, "anchor": "e"},
}

# ترجمه روزهای هفته
PERSIAN_WEEKDAYS = {
    "Saturday": "شنبه", 
    "Sunday": "یکشنبه", 
    "Monday": "دوشنبه", 
    "Tuesday": "سه‌شنبه",
    "Wednesday": "چهارشنبه", 
    "Thursday": "پنج‌شنبه", 
    "Friday": "جمعه"
}