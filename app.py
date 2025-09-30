# ==========================================================
#  File: app.py  (کامل و بازنویسی‌شده بر اساس استایل‌های جدید)
# ==========================================================
import ttkbootstrap as ttkb
from tkinter import messagebox, Menu, BooleanVar, StringVar, Toplevel
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
import database as db
from datetime import datetime, timedelta
import jdatetime
import ui_windows
import styles
from tkextrafont import Font
from custom_widgets import DateEntry


class TimeTrackerApp(ttkb.Window):
    """پنجره‌ی اصلی برنامه‌ی زمان‌سنج"""

    def __init__(self, themename: str = styles.LIGHT_THEME):
        super().__init__(themename=themename)

        # بارگذاری فونت سفارشی
        try:
            Font(file="Vazirmatn-Regular.ttf")
            print("Font 'Vazirmatn-Regular.ttf' loaded successfully.")
        except Exception as e:
            print(f"Error loading font: {e}\nFalling back to default fonts.")

        # تنظیمات اولیه پنجره
        self.title("ZamanSanj 1.0")
        self.geometry("1000x600")
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # تنظیمات شبکه‌بندی پنجره اصلی
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # زبان فارسی برای jdatetime
        jdatetime.set_locale("fa_IR")

        # راه‌اندازی پایگاه‌داده
        db.setup_database()

        # متغیرهای وضعیت
        self.current_entry: dict | None = None
        self.is_running: bool = False
        self.start_time: datetime | None = None
        self.elapsed_time = StringVar(value="00:00.00")
        self.is_dark_mode = BooleanVar(value=(themename == styles.DARK_THEME))

        # ساخت و بروزرسانی ابزارک‌ها
        self.create_widgets()
        self.populate_categories()
        self.reset_filters()
        self.update_timer()

    # ------------------------------------------------------------------
    # ساخت تمام ابزارک‌ها (UI)
    # ------------------------------------------------------------------
    def create_widgets(self) -> None:
        main_frame = ttkb.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------
        # نوار بالا (راهنما + تغییر تم)
        # ---------------------------------------------
        top_frame = ttkb.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=5)

        ttkb.Button(
            top_frame,
            text="راهنما",
            command=self.show_help_window,
            bootstyle=styles.BTN_SECONDARY
        ).pack(side="right")

        ttkb.Checkbutton(
            top_frame,
            text="حالت تاریک",
            bootstyle="round-toggle",
            variable=self.is_dark_mode,
            command=self.toggle_theme
        ).pack(side="left")

        # ---------------------------------------------
        # بخش ورودی‌ها (عنوان فعالیت، دسته، توضیحات)
        # ---------------------------------------------
        input_frame = ttkb.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)

        # --- عنوان فعالیت ---
        task_frame = ttkb.Frame(input_frame)
        task_frame.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Label(task_frame, text="عنوان فعالیت", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.task_name_entry = ttkb.Entry(task_frame, justify="right", font=styles.DEFAULT_FONT)
        self.task_name_entry.pack(side="right", fill="x", expand=True)

        # --- دسته‌بندی ---
        category_frame = ttkb.Frame(input_frame)
        category_frame.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Label(category_frame, text="دسته‌بندی", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.category_combo = ttkb.Combobox(category_frame, state="readonly", justify="right", font=styles.DEFAULT_FONT)
        self.category_combo.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Button(
            category_frame,
            text="مدیریت دسته‌ها",
            command=lambda: ui_windows.CategoryManagerWindow(self),
            bootstyle=styles.BTN_INFO
        ).pack(side="right", padx=2)

        # --- توضیحات ---
        notes_frame = ttkb.Frame(main_frame)
        notes_frame.grid(row=2, column=0, sticky="ew", pady=5)
        ttkb.Label(notes_frame, text="توضیحات", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.notes_entry = ttkb.Entry(notes_frame, justify="right", font=styles.DEFAULT_FONT)
        self.notes_entry.pack(side="right", fill="x", expand=True, padx=5)

        # ---------------------------------------------
        # بخش کنترل (شروع/توقف + نمایش زمان)
        # ---------------------------------------------
        control_frame = ttkb.Frame(main_frame)
        control_frame.grid(row=3, column=0, sticky="ew", pady=10)

        button_frame = ttkb.Frame(control_frame)
        button_frame.pack(side="right", padx=10)

        self.start_button = ttkb.Button(
            button_frame,
            text="شروع کار",
            command=self.start_new_task,
            bootstyle=styles.BTN_SUCCESS
        )
        self.start_button.pack(side="right", padx=5)

        self.stop_button = ttkb.Button(
            button_frame,
            text="توقف کار",
            command=self.stop_current_task,
            state="disabled",
            bootstyle=styles.BTN_DANGER
        )
        self.stop_button.pack(side="right", padx=5)

        timer_frame = ttkb.Frame(control_frame)
        timer_frame.pack(side="right", padx=10)
        ttkb.Label(timer_frame, text="زمان سپری شده", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.timer_label = ttkb.Label(timer_frame, textvariable=self.elapsed_time, font=styles.TIMER_FONT)
        self.timer_label.pack(side="right")

        # ---------------------------------------------
        # بخش فیلترها
        # ---------------------------------------------
        filter_frame = ttkb.LabelFrame(main_frame, text="فیلترها", bootstyle=styles.FRAME_STYLE)
        filter_frame.grid(row=4, column=0, sticky="ew", pady=(10, 5), padx=5)

        ttkb.Label(filter_frame, text="از تاریخ", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 5))
        self.start_date_filter = DateEntry(filter_frame, width=12, justify="center", font=styles.DEFAULT_FONT)
        self.start_date_filter.pack(side="right", padx=5)

        ttkb.Label(filter_frame, text="تا تاریخ", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.end_date_filter = DateEntry(filter_frame, width=12, justify="center", font=styles.DEFAULT_FONT)
        self.end_date_filter.pack(side="right", padx=5)

        ttkb.Label(filter_frame, text="دسته‌بندی", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.category_filter_combo = ttkb.Combobox(
            filter_frame,
            state="readonly",
            justify="right",
            width=15,
            font=styles.DEFAULT_FONT
        )
        self.category_filter_combo.pack(side="right", padx=5)

        ttkb.Label(filter_frame, text="روز هفته", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.day_filter_combo = ttkb.Combobox(
            filter_frame,
            state="readonly",
            justify="right",
            width=12,
            font=styles.DEFAULT_FONT
        )
        self.day_filter_combo["values"] = ["همه"] + list(styles.PERSIAN_WEEKDAYS.values())
        self.day_filter_combo.pack(side="right", padx=5)

        # دکمه‌های فیلتر
        self.reset_filter_button = ttkb.Button(
            filter_frame,
            text="ریست فیلتر",
            command=self.reset_filters,
            bootstyle=styles.BTN_SECONDARY
        )
        self.reset_filter_button.pack(side="left", padx=5)

        self.apply_filter_button = ttkb.Button(
            filter_frame,
            text="اعمال فیلتر",
            command=self.apply_filters,
            bootstyle=styles.BTN_PRIMARY
        )
        self.apply_filter_button.pack(side="left", padx=5)

        # ---------------------------------------------
        # بخش تب‌ها (تاریخچه و اهداف)
        # ---------------------------------------------
        notebook = ttkb.Notebook(main_frame, bootstyle="primary")
        notebook.grid(row=5, column=0, sticky="nsew", pady=(0, 5))

        # --- تب تاریخچه ---
        log_frame = ttkb.Frame(notebook, padding=5)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        notebook.add(log_frame, text=" تاریخچه فعالیت‌ها ")

        self.main_log_tree = ttkb.Treeview(
            log_frame,
            columns=styles.TREEVIEW_COLUMN_ORDER,
            show="headings",
            bootstyle=styles.TREEVIEW_STYLE
        )
        for col_id in styles.TREEVIEW_COLUMN_ORDER:
            self.main_log_tree.heading(col_id, text=styles.TREEVIEW_HEADINGS.get(col_id, ""))
            cfg = styles.TREEVIEW_COLUMNS_CONFIG.get(col_id, {})
            self.main_log_tree.column(
                col_id, width=cfg.get("width", 100), anchor=cfg.get("anchor", "e")
            )
        self.main_log_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.main_log_tree.yview, bootstyle=styles.TREEVIEW_SCROLLBAR_STYLE)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.main_log_tree.configure(yscrollcommand=scrollbar.set)
        self.treeview_menu = Menu(self, tearoff=0)
        self.treeview_menu.add_command(label="ویرایش فعالیت", command=self.edit_selected_entry)
        self.treeview_menu.add_command(label="حذف فعالیت", command=self.delete_selected_entry)
        self.treeview_menu.add_command(label="ادامه فعالیت", command=self.resume_selected_entry)
        self.main_log_tree.bind("<Button-3>", self.show_treeview_menu)

        # ---------------------------------------------
        # دکمه‌های پایینی (افزودن دستی / گزارش)
        # ---------------------------------------------
        action_frame = ttkb.Frame(main_frame)
        action_frame.grid(row=6, column=0, sticky="s", pady=(5, 10))

        center_frame = ttkb.Frame(action_frame)
        center_frame.pack(expand=True)

        ttkb.Button(
            center_frame,
            text="افزودن دستی",
            command=lambda: ui_windows.AddManualEntryWindow(self),
            bootstyle=styles.BTN_INFO
        ).pack(side="left", padx=10)

        ttkb.Button(
            center_frame,
            text="گزارش",
            command=lambda: ui_windows.ReportGeneratorWindow(self),
            bootstyle=styles.BTN_PRIMARY
        ).pack(side="left", padx=10)

    # ------------------------------------------------------------------
    # متدهای عملیاتی
    # ------------------------------------------------------------------
    def show_help_window(self) -> None:
        """نمایش پنجره‌ی راهنما"""
        help_win = Toplevel(self)
        help_win.title("راهنمای نرم‌افزار زمان‌سنج")
        help_win.geometry("800x600")
        help_win.transient(self)
        help_win.grab_set()

        help_content = """
## راهنمای نرم‌افزار زمان‌سنج (ZamanSanj)

این نرم‌افزار برای ثبت و مدیریت زمان فعالیت‌های روزانه شما طراحی شده است.

### ۳. تاریخچه فعالیت‌ها و فیلترها
- ...
- **فیلترها**: بالای جدول، ابزارهایی برای فیلتر کردن تاریخچه وجود دارد:
  - **فیلتر تاریخ**: بازه زمانی شمسی را با فرمت (مثال: ۱۴۰۳/۰۶/۲۴) وارد کنید.
  - ...
"""
        text_widget = ScrolledText(help_win, wrap="word", font=styles.DEFAULT_FONT, padding=15)
        text_widget.insert("1.0", help_content)
        text_widget.text.tag_configure("rtl", justify="right")
        text_widget.text.tag_add("rtl", "1.0", "end")
        text_widget.text.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

    def apply_filters(self) -> None:
        self.refresh_main_log()

    def reset_filters(self) -> None:
        """بازنشستن فیلترها به حالت پیش‌فرض ۳۰ روز گذشته"""
        end_jalali = jdatetime.date.today()
        start_jalali = end_jalali - jdatetime.timedelta(days=30)

        self.start_date_filter.set(start_jalali.strftime("%Y/%m/%d"))
        self.end_date_filter.set(end_jalali.strftime("%Y/%m/%d"))
        self.day_filter_combo.set("همه")
        self.category_filter_combo.set("همه")

        self.refresh_main_log()

    def refresh_main_log(self) -> None:
        """خواندن داده‌ها از DB و نمایش در Treeview با توجه به فیلترها"""
        # حذف ردیف‌های قبلی
        for item in self.main_log_tree.get_children():
            self.main_log_tree.delete(item)

        # خواندن مقادیر فیلترها
        start_jalali_str = self.start_date_filter.get()
        end_jalali_str = self.end_date_filter.get()
        selected_day = self.day_filter_combo.get()
        selected_category = self.category_filter_combo.get()

        try:
            # تبدیل شمسی به میلادی برای کوئری
            start_gregorian = jdatetime.datetime.strptime(start_jalali_str, "%Y/%m/%d").togregorian().date()
            end_gregorian = jdatetime.datetime.strptime(end_jalali_str, "%Y/%m/%d").togregorian().date()

            start_db = start_gregorian.strftime("%Y-%m-%d")
            end_db = (end_gregorian + timedelta(days=1)).strftime("%Y-%m-%d")

            rows = db.get_entries_by_date_range(start_db, end_db)
        except (ValueError, AttributeError):
            messagebox.showerror("خطای تاریخ", "فرمت تاریخ شمسی صحیح نیست. لطفاً از فرمت YYYY/MM/DD استفاده کنید.")
            return
        except Exception as e:
            messagebox.showerror("خطا در واکشی داده‌ها", f"خطایی رخ داد: {e}")
            return

        # پردازش هر رکورد
        for entry in rows:
            entry_id, task, cat, start_str, end_str, notes = entry
            cat_name = cat or "بدون دسته"

            try:
                start_dt = datetime.strptime(start_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                english_day = start_dt.strftime("%A")
                persian_day = styles.PERSIAN_WEEKDAYS.get(english_day, english_day)

                # اعمال فیلتر روز و دسته
                day_ok = (selected_day == "همه") or (selected_day == persian_day)
                cat_ok = (selected_category == "همه") or (selected_category == cat_name)
                if not (day_ok and cat_ok):
                    continue

                jalali_date = jdatetime.date.fromgregorian(date=start_dt.date())

                values = {
                    "date": jalali_date.strftime("%y/%m/%d"),
                    "day_of_week": persian_day,
                    "start_time": start_dt.strftime("%H:%M"),
                    "task_name": task,
                    "category": cat_name
                }

                if end_str:
                    end_dt = datetime.strptime(end_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                    duration_sec = (end_dt - start_dt).total_seconds()
                    hours, rem = divmod(duration_sec, 3600)
                    minutes, seconds = divmod(rem, 60)
                    values["end_time"] = end_dt.strftime("%H:%M")
                    values["duration"] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                else:
                    values["end_time"] = "در حال اجرا"
                    values["duration"] = "--:--:--"

                ordered = [values.get(col, "") for col in styles.TREEVIEW_COLUMN_ORDER]
                self.main_log_tree.insert("", "end", iid=entry_id, values=ordered)

            except (ValueError, TypeError) as e:
                print(f"Error processing entry ID {entry_id}: {start_str} - {e}")

    def populate_categories(self) -> None:
        """پر کردن ComboBoxهای دسته‌بندی و ساخت دیکشنری‌های کمکی"""
        categories = db.get_categories()
        cat_names = [name for _, name in categories]

        self.category_combo["values"] = cat_names
        self.category_filter_combo["values"] = ["همه"] + cat_names

        self.category_map = {name: cat_id for cat_id, name in categories}
        self.id_to_category_map = {cat_id: name for cat_id, name in categories}

        if cat_names:
            self.category_combo.current(0)
        self.category_filter_combo.set("همه")

    def update_timer(self) -> None:
        """به‌روزرسانی زمان سپری‌شده (هر ۱۰ میلی‌ثانیه)"""
        if self.is_running and self.start_time:
            elapsed = datetime.now() - self.start_time
            total_seconds = elapsed.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            hundredths = int((total_seconds - int(total_seconds)) * 100)
            self.elapsed_time.set(f"{minutes:02d}:{seconds:02d}.{hundredths:02d}")
        self.after(10, self.update_timer)

    def start_new_task(self) -> None:
        """شروع رکورد جدید"""
        task_name = self.task_name_entry.get().strip()
        if not task_name:
            messagebox.showerror("خطا", "لطفاً یک عنوان برای کار وارد کنید.")
            return

        category_name = self.category_combo.get()
        category_id = self.category_map.get(category_name) if category_name else None
        notes = self.notes_entry.get().strip()

        entry_id = db.start_tracking(task_name, category_id, notes)
        self.current_entry = {
            "id": entry_id,
            "name": task_name,
            "category": category_name,
            "notes": notes
        }

        self.is_running = True
        self.start_time = datetime.now()
        self.update_ui_state()
        self.refresh_main_log()

    def stop_current_task(self) -> None:
        """توقف رکورد جاری"""
        if not self.current_entry:
            return

        notes = self.notes_entry.get().strip()
        db.stop_tracking(
            self.current_entry["id"],
            self.current_entry["name"],
            notes
        )

        self.current_entry = None
        self.is_running = False
        self.start_time = None
        self.elapsed_time.set("00:00.00")
        self.update_ui_state()
        self.refresh_main_log()

    def update_ui_state(self) -> None:
        """فعال/غیرفعال کردن دکمه‌ها بر اساس وضعیت کرونومتر"""
        if self.is_running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def toggle_theme(self) -> None:
        """جابجایی بین تم روشن و تاریک"""
        self.style.theme_use(styles.DARK_THEME if self.is_dark_mode.get() else styles.LIGHT_THEME)

    def show_treeview_menu(self, event) -> None:
        """نمایش منوی راست-کلیک روی ردیف‌های جدول"""
        item = self.main_log_tree.identify_row(event.y)
        if item:
            self.main_log_tree.selection_set(item)
            self.treeview_menu.post(event.x_root, event.y_root)

    def edit_selected_entry(self) -> None:
        """باز کردن پنجره ویرایش رکورد انتخاب‌شده"""
        selected = self.main_log_tree.selection()
        if not selected:
            return
        entry_id = selected[0]
        ui_windows.EditEntryWindow(self, entry_id)

    def delete_selected_entry(self) -> None:
        """حذف رکورد انتخاب‌شده پس از تأیید"""
        selected = self.main_log_tree.selection()
        if not selected:
            return
        entry_id = selected[0]
        if messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید می‌خواهید این فعالیت را حذف کنید?"):
            db.delete_entry(entry_id)
            self.refresh_main_log()

    def resume_selected_entry(self) -> None:
        """ادامه دادن یک فعالیت قبلی (متوقف‌شده)"""
        selected = self.main_log_tree.selection()
        if not selected:
            return

        entry_id = selected[0]
        entry_data = db.get_entry_by_id(entry_id)
        if not entry_data:
            return

        # اگر در حال حاضر فعالیتی فعال است، آن را متوقف کن
        if self.current_entry:
            self.stop_current_task()

        _, task_name, category_id, _, _, notes = entry_data
        new_entry_id = db.start_tracking(task_name, category_id, notes)

        self.current_entry = {
            "id": new_entry_id,
            "name": task_name,
            "category": self.id_to_category_map.get(category_id, ""),
            "notes": notes
        }

        self.is_running = True
        self.start_time = datetime.now()
        self.update_ui_state()
        self.refresh_main_log()


# ----------------------------------------------------------------------
# اجرای برنامه
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # در صورت نیاز می‌توان register_styles() را این‌جا فراخوانی کرد
    # اکنون تمام استایل‌ها از styles خوانده می‌شوند
    app = TimeTrackerApp(themename=styles.LIGHT_THEME)
    app.mainloop()