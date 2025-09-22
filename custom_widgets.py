# ==========================================================
#  File: custom_widgets.py  (بازنویسی کامل + تطابق با استایل‌های جدید)
# ==========================================================
import ttkbootstrap as ttkb
import styles


class DateEntry(ttkb.Entry):
    """
    ویجت ورودی تاریخ شمسی با فرمت YYYY/MM/DD
    - فقط اعداد پذیرفته می‌شود
    - اسلش‌ها ثابت باقی می‌مانند
    - ماه و روز تک‌رقمی به صورت خودکار دو رقمی می‌شوند
    """

    # ----------------------------------------------------------
    def __init__(self, master, placeholder: str = "YYYY/MM/DD", **kwargs):
        """
        :param master: والد tkinter
        :param placeholder: متن راهنما (پیش‌فرض: YYYY/MM/DD)
        :param kwargs: سایر ویژگی‌های استاندارد Entry
        """
        # حذف justify و font از kwargs تا خودمان مدیریت کنیم
        kwargs.setdefault("justify", "center")
        kwargs.setdefault("font", styles.DEFAULT_FONT)
        super().__init__(master, **kwargs)

        # ثبت تابع اعتبارسنجی
        vcmd = (self.register(self._validate_input), "%P", "%d", "%i", "%s")
        self.config(validate="key", validatecommand=vcmd)

        # رویدادهای فرمت‌دهی خودکار
        self.bind("<FocusOut>", self._format_date_on_focus_out)
        self.bind("<Return>", self._format_date_on_focus_out)

        # درج متن راهنما
        self.insert(0, placeholder)

    # ----------------------------------------------------------
    def _validate_input(self, proposed_text: str, action_type: str, index_str: str, current_text: str) -> bool:
        """
        اعتبارسنجی کاراکتر به کاراکتر هنگام تایپ.
        action_type = '0' → حذف
        action_type = '1' → افزودن
        """
        if action_type == "0":  # حذف
            index = int(index_str)
            # جلوگیری از حذف اسلش‌ها
            if index in (4, 7):
                return False
            return True

        # جلوگیری از طول بیش از ۱۰ کاراکتر
        if len(proposed_text) > 10:
            return False

        index = int(index_str)
        char_to_insert = proposed_text[index] if index < len(proposed_text) else ""

        # اگر موقعیت اسلش است، تایپ را رد کن
        if index in (4, 7):
            return False

        # فقط عدد مجاز است
        return char_to_insert.isdigit()

    # ----------------------------------------------------------
    def _format_date_on_focus_out(self, event=None) -> None:
        """
        دو رقمی کردن ماه و روز هنگام ترک فیلد یا زدن Enter.
        """
        current_text = self.get().strip()
        if current_text == "":
            return

        parts = current_text.split("/")
        if len(parts) != 3:
            return

        year, month, day = parts

        # دو رقمی کردن ماه و روز
        month = month.zfill(2)
        day = day.zfill(2)

        formatted = f"{year}/{month}/{day}"

        # اگر سال ۴ رقمی و ماه/روز ۲ رقمی بود، جایگزین کن
        if len(year) == 4 and len(month) == 2 and len(day) == 2:
            self.delete(0, "end")
            self.insert(0, formatted)

    # ----------------------------------------------------------
    def set(self, date_str: str) -> None:
        """
        تنظیم سریع تاریخ (با فرمت YYYY/MM/DD)
        """
        self.delete(0, "end")
        self.insert(0, date_str)
        self._format_date_on_focus_out()