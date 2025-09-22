#  styles.py  – نسخه‌ی یک‌پارچه و قابل نگهداری
#  تمام استایل‌ها و مقادیر ثابت ظاهری برنامه فقط از این‌جا خوانده شود
#  چنان‌چه نیاز به رنگ یا فونت سازمانی جدید دارید، فقط همین فایل را تغییر دهید


# ------------------------------------------------------------------------------
# 1) تم‌های اصلی برنامه
# ------------------------------------------------------------------------------
LIGHT_THEME: str = "litera"
DARK_THEME: str  = "superhero"


# ------------------------------------------------------------------------------
# 2) خانواده فونت‌ها (برای یک‌دستی در سراسر UI)
# ------------------------------------------------------------------------------
TIMER_FONT   = ("Vazirmatn", 20, "bold")
DEFAULT_FONT = ("Vazirmatn", 11)          # اندازه‌ی خواناتر نسبت به 10
SMALL_FONT   = ("Vazirmatn", 9)


# ------------------------------------------------------------------------------
# 3) استایل کلی ویجت‌ها (Button, Frame, LabelFrame, ...)
#    از این پس فقط این ثابت‌ها استفاده شود تا هیچ‌گاه «ناموجود» خطا ندهید
# ------------------------------------------------------------------------------
FRAME_STYLE       = "info"

BTN_PRIMARY       = "primary-outline"
BTN_SECONDARY     = "secondary-outline"
BTN_SUCCESS       = "success-outline"
BTN_DANGER        = "danger-outline"
BTN_WARNING       = "warning-outline"
BTN_INFO          = "info-outline"

# اگر خواستید حالت «پر» استفاده کنید، همین زیر مجموعه را تعریف کنید:
BTN_SOLID_PRIMARY   = "primary"
BTN_SOLID_SUCCESS   = "success"
BTN_SOLID_DANGER    = "danger"
BTN_SOLID_WARNING   = "warning"
BTN_SOLID_INFO      = "info"


# ------------------------------------------------------------------------------
# 4) استایل اختصاصی Treeview (جدول اصلی برنامه)
# ------------------------------------------------------------------------------
TREEVIEW_STYLE            = "primary"
TREEVIEW_SCROLLBAR_STYLE  = "round-primary"

# ترتیب ستون‌ها در Treeview اصلی
TREEVIEW_COLUMN_ORDER = (
    "task_name", "category", "duration",
    "end_time", "start_time", "day_of_week", "date"
)

# سرنویس فارسی هر ستون
TREEVIEW_HEADINGS = {
    "date": "تاریخ",
    "day_of_week": "روز هفته",
    "start_time": "ساعت شروع",
    "end_time": "ساعت پایان",
    "duration": "مدت زمان",
    "category": "دسته",
    "task_name": "عنوان فعالیت",
}

# پهنا و چینش هر ستون
TREEVIEW_COLUMNS_CONFIG = {
    "date": {"width": 100, "anchor": "center"},
    "day_of_week": {"width": 100, "anchor": "center"},
    "start_time": {"width": 100, "anchor": "center"},
    "end_time": {"width": 100, "anchor": "center"},
    "duration": {"width": 100, "anchor": "center"},
    "category": {"width": 150, "anchor": "e"},
    "task_name": {"width": 400, "anchor": "e"},
}


# ------------------------------------------------------------------------------
# 5) متن‌های ترجمه‌شده (روزهای هفته، عنوان پنجره‌ها و ...)
# ------------------------------------------------------------------------------
PERSIAN_WEEKDAYS = {
    "Saturday":  "شنبه",
    "Sunday":    "یکشنبه",
    "Monday":    "دوشنبه",
    "Tuesday":   "سه‌شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday":  "پنج‌شنبه",
    "Friday":    "جمعه",
}

# اگر در آینده عنوان دیگری خواستید اضافه کنید، این‌جا بنویسید:
PERSIAN_MONTHS = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
    4: "تیر", 5: "مرداد", 6: "شهریور",
    7: "مهر", 8: "آبان", 9: "آذر",
    10: "دی", 11: "بهمن", 12: "اسفند",
}