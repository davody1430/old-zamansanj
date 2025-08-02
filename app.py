import ttkbootstrap as ttkb
from tkinter import messagebox, Menu, BooleanVar, StringVar, Toplevel
from ttkbootstrap.scrolled import ScrolledText
import database as db
from datetime import datetime, timedelta
import jdatetime
import ui_windows 
import styles
import time
from tkextrafont import Font

class TimeTrackerApp(ttkb.Window):
    def __init__(self, themename='litera'):
        super().__init__(themename=themename)
        
        # --- بخش اصلاح شده برای هماهنگی با styles.py ---
        try:
            # فونت را مستقیما بارگذاری می‌کنیم تا نام "Vazirmatn" در دسترس باشد
            Font(file="Vazirmatn-Regular.ttf")
            print("Font 'Vazirmatn-Regular.ttf' loaded successfully.")
        except Exception as e:
            print(f"Error loading font: {e}\nFalling back to default fonts.")
        # --- پایان بخش اصلاح شده ---

        self.title("ZamanSanj 1.0")
        self.geometry("1000x600")
        
        # Center the window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        jdatetime.set_locale('fa_IR')
        db.setup_database()

        self.current_entry = None
        self.is_running = False
        self.start_time = None
        self.elapsed_time = StringVar(value="00:00.00")
        
        self.is_dark_mode = BooleanVar(value=(themename == styles.DARK_THEME))
        self.create_widgets()
        self.populate_categories()
        self.reset_filters() 
        self.update_timer()

    def create_widgets(self):
        main_frame = ttkb.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = ttkb.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        # استفاده از استایل هماهنگ با styles.py
        ttkb.Button(top_frame, text="راهنما", command=self.show_help_window, bootstyle=styles.BUTTON_SECONDARY).pack(side="right")
        
        ttkb.Checkbutton(top_frame, text="حالت تاریک", bootstyle="round-toggle", 
                         variable=self.is_dark_mode, command=self.toggle_theme).pack(side="left")

        input_frame = ttkb.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        task_frame = ttkb.Frame(input_frame)
        task_frame.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Label(task_frame, text="عنوان فعالیت", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.task_name_entry = ttkb.Entry(task_frame, justify='right', font=styles.DEFAULT_FONT)
        self.task_name_entry.pack(side="right", fill="x", expand=True)

        category_frame = ttkb.Frame(input_frame)
        category_frame.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Label(category_frame, text="دسته‌بندی", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.category_combo = ttkb.Combobox(category_frame, state="readonly", justify='right', font=styles.DEFAULT_FONT)
        self.category_combo.pack(side="right", fill="x", expand=True, padx=5)
        ttkb.Button(category_frame, text="مدیریت دسته‌ها", 
                   command=lambda: ui_windows.CategoryManagerWindow(self),
                   bootstyle=styles.BUTTON_INFO).pack(side="right", padx=5)

        notes_frame = ttkb.Frame(main_frame)
        notes_frame.grid(row=2, column=0, sticky="ew", pady=5)
        ttkb.Label(notes_frame, text="توضیحات", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.notes_entry = ttkb.Entry(notes_frame, justify='right', font=styles.DEFAULT_FONT)
        self.notes_entry.pack(side="right", fill="x", expand=True, padx=5)

        control_frame = ttkb.Frame(main_frame)
        control_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        button_frame = ttkb.Frame(control_frame)
        button_frame.pack(side="right", padx=10)
        self.start_button = ttkb.Button(button_frame, text="شروع کار", 
                                       command=self.start_new_task, bootstyle=styles.BUTTON_SUCCESS)
        self.start_button.pack(side="right", padx=5)
        self.stop_button = ttkb.Button(button_frame, text="توقف کار", 
                                     command=self.stop_current_task, state="disabled",
                                     bootstyle=styles.BUTTON_DANGER)
        self.stop_button.pack(side="right", padx=5)

        timer_frame = ttkb.Frame(control_frame)
        timer_frame.pack(side="right", padx=10)
        ttkb.Label(timer_frame, text="زمان سپری شده", font=styles.DEFAULT_FONT).pack(side="right", padx=5)
        self.timer_label = ttkb.Label(timer_frame, textvariable=self.elapsed_time, 
                                     font=styles.TIMER_FONT)
        self.timer_label.pack(side="right")

        filter_frame = ttkb.LabelFrame(main_frame, text="فیلترها", bootstyle=styles.FRAME_STYLE_INFO)
        filter_frame.grid(row=4, column=0, sticky="ew", pady=(10, 5), padx=5)

        ttkb.Label(filter_frame, text="تا تاریخ:", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 5))
        self.end_date_filter = ttkb.Entry(filter_frame, width=12, justify='center', font=styles.DEFAULT_FONT)
        self.end_date_filter.pack(side="right", padx=5)
        ttkb.Label(filter_frame, text="از تاریخ:", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.start_date_filter = ttkb.Entry(filter_frame, width=12, justify='center', font=styles.DEFAULT_FONT)
        self.start_date_filter.pack(side="right", padx=5)

        ttkb.Label(filter_frame, text="دسته‌بندی:", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.category_filter_combo = ttkb.Combobox(filter_frame, state="readonly", justify='right', width=15, font=styles.DEFAULT_FONT)
        self.category_filter_combo.pack(side="right", padx=5)

        ttkb.Label(filter_frame, text="روز هفته:", font=styles.DEFAULT_FONT).pack(side="right", padx=(0, 10))
        self.day_filter_combo = ttkb.Combobox(filter_frame, state="readonly", justify='right', width=12, font=styles.DEFAULT_FONT)
        self.day_filter_combo['values'] = ["همه"] + list(styles.PERSIAN_WEEKDAYS.values())
        self.day_filter_combo.pack(side="right", padx=5)

        self.reset_filter_button = ttkb.Button(filter_frame, text="ریست فیلتر", command=self.reset_filters)
        self.reset_filter_button.pack(side="left", padx=5)
        self.apply_filter_button = ttkb.Button(filter_frame, text="اعمال فیلتر", command=self.apply_filters, bootstyle=styles.BUTTON_PRIMARY)
        self.apply_filter_button.pack(side="left", padx=5)

        log_frame = ttkb.LabelFrame(main_frame, text="تاریخچه فعالیت‌ها", bootstyle=styles.FRAME_STYLE_INFO)
        log_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 5))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.main_log_tree = ttkb.Treeview(log_frame, columns=styles.TREEVIEW_COLUMN_ORDER, 
                                         show="headings", bootstyle=styles.TREEVIEW_STYLE)
        
        for col_id in styles.TREEVIEW_COLUMN_ORDER:
            self.main_log_tree.heading(col_id, text=styles.TREEVIEW_HEADINGS.get(col_id, ""))
            config = styles.TREEVIEW_COLUMNS_CONFIG.get(col_id, {})
            self.main_log_tree.column(col_id, width=config.get("width", 100), 
                                    anchor=config.get("anchor", "e"))
        
        self.main_log_tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", 
                                   command=self.main_log_tree.yview, 
                                   bootstyle=styles.TREEVIEW_SCROLLBAR_STYLE)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.main_log_tree.configure(yscrollcommand=scrollbar.set)
        
        self.treeview_menu = Menu(self, tearoff=0)
        self.treeview_menu.add_command(label="ویرایش فعالیت", command=self.edit_selected_entry)
        self.treeview_menu.add_command(label="حذف فعالیت", command=self.delete_selected_entry)
        self.treeview_menu.add_command(label="ادامه فعالیت", command=self.resume_selected_entry)
        self.main_log_tree.bind("<Button-3>", self.show_treeview_menu)

        action_frame = ttkb.Frame(main_frame)
        action_frame.grid(row=6, column=0, sticky="s", pady=(5, 10))
        
        center_frame = ttkb.Frame(action_frame)
        center_frame.pack(expand=True)
        
        ttkb.Button(center_frame, text="افزودن دستی", 
                   command=lambda: ui_windows.AddManualEntryWindow(self),
                   bootstyle=styles.BUTTON_INFO).pack(side="left", padx=10)
        ttkb.Button(center_frame, text="گزارش", 
                    command=lambda: ui_windows.ReportGeneratorWindow(self),
                   bootstyle=styles.BUTTON_PRIMARY).pack(side="left", padx=10)

    def show_help_window(self):
        help_win = Toplevel(self)
        help_win.title("راهنمای نرم‌افزار زمان‌سنج")
        help_win.geometry("800x600")
        help_win.transient(self)
        help_win.grab_set()

        help_text_content = """
## راهنمای نرم‌افزار زمان‌سنج (ZamanSanj)

این نرم‌افزار برای ثبت و مدیریت زمان فعالیت‌های روزانه شما طراحی شده است.

### ۱. بخش اصلی: ثبت زمان
- **عنوان فعالیت**: نام یا موضوع اصلی کاری که می‌خواهید انجام دهید را اینجا وارد کنید (مثلاً: پروژه پایتون).
- **دسته‌بندی**: یک دسته برای فعالیت خود انتخاب کنید. این کار به گزارش‌گیری بهتر کمک می‌کند.
- **توضیحات**: جزئیات بیشتر یا یادداشت‌های مربوط به فعالیت را در این بخش بنویسید.
- **دکمه شروع کار**: با کلیک روی این دکمه، زمان‌سنج شروع به کار می‌کند.
- **دکمه توقف کار**: برای پایان دادن به فعالیت فعلی، این دکمه را فشار دهید. اطلاعات در جدول تاریخچه ثبت می‌شود.

### ۲. مدیریت دسته‌بندی‌ها
- با کلیک روی دکمه **«مدیریت دسته‌ها»**، پنجره‌ای باز می‌شود.
- در این پنجره می‌توانید با دکمه **«افزودن»**، دسته‌بندی جدیدی (مانند: مطالعه، ورزش) تعریف کنید.
- برای حذف یک دسته‌بندی، آن را از لیست انتخاب و دکمه **«حذف»** را بزنید. (توجه: دسته‌بندی‌هایی که در فعالیت‌ها استفاده شده‌اند قابل حذف نیستند).

### ۳. تاریخچه فعالیت‌ها و فیلترها
- جدول بزرگ در پایین صفحه، تمام فعالیت‌های ثبت‌شده شما را نمایش می‌دهد.
- **فیلترها**: بالای جدول، ابزارهایی برای فیلتر کردن تاریخچه وجود دارد:
    - **فیلتر تاریخ**: بازه زمانی مورد نظر خود را با فرمت (YYYY-MM-DD) وارد کنید.
    - **فیلتر دسته‌بندی**: فقط فعالیت‌های یک دسته خاص را مشاهده کنید.
    - **فیلتر روز هفته**: فعالیت‌های یک روز خاص از هفته (مثلاً فقط شنبه‌ها) را ببینید.
- **اعمال فیلتر**: پس از انتخاب فیلترها، این دکمه را بزنید تا نتایج نمایش داده شوند.
- **ریست فیلتر**: این دکمه تمام فیلترها را پاک کرده و نمایش را به حالت پیش‌فرض (۳۰ روز اخیر) برمی‌گرداند.

### ۴. عملیات روی فعالیت‌ها (منوی راست کلیک)
- با **راست کلیک** روی هر فعالیت در جدول تاریخچه، منویی با گزینه‌های زیر باز می‌شود:
    - **ویرایش فعالیت**: تمام جزئیات یک فعالیت ثبت‌شده (عنوان، دسته، زمان شروع و پایان) را تغییر دهید.
    - **حذف فعالیت**: یک فعالیت را برای همیشه از تاریخچه پاک می‌کند (این عمل غیرقابل بازگشت است).
    - **ادامه فعالیت**: یک زمان‌سنج جدید با همان عنوان و دسته‌بندیِ فعالیت انتخاب‌شده شروع می‌کند.

### ۵. افزودن دستی و گزارش‌گیری
- **افزودن دستی**: اگر فراموش کردید زمان‌سنج را فعال کنید، با این دکمه می‌توانید یک فعالیت را به صورت دستی و با تعیین زمان شروع و پایان دقیق، به تاریخچه اضافه کنید.
- **گزارش**: با کلیک روی این دکمه، پنجره گزارش‌گیری باز می‌شود.
    - **گزارش HTML**: یک فایل HTML کامل شامل نمودار دایره‌ای (بر اساس دسته‌بندی) و جزئیات کامل فعالیت‌ها در بازه زمانی انتخابی شما می‌سازد و آن را در مرورگر باز می‌کند. این فایل‌ها در پوشه‌ای به نام `reports_output` در کنار برنامه ذخیره می‌شوند.
    - **خروجی CSV**: یک فایل CSV از داده‌های خام تهیه می‌کند که برای استفاده در نرم‌افزارهایی مانند Excel مناسب است.

### ۶. تنظیمات ظاهری
- **حالت تاریک**: با فعال/غیرفعال کردن این گزینه در بالای صفحه، می‌توانید تم برنامه را بین روشن و تاریک تغییر دهید.
"""
        # استفاده از فونت هماهنگ با styles.py
        help_font = styles.DEFAULT_FONT
        text_widget = ScrolledText(help_win, wrap="word", font=help_font, padding=15)
        text_widget.insert("1.0", help_text_content)
        
        text_widget.text.tag_configure("rtl", justify="right")
        text_widget.text.tag_add("rtl", "1.0", "end")

        text_widget.text.config(state="disabled") 
        text_widget.pack(fill="both", expand=True)
        
    def apply_filters(self):
        self.refresh_main_log()

    def reset_filters(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        self.start_date_filter.delete(0, 'end')
        self.start_date_filter.insert(0, start_date.strftime('%Y-%m-%d'))
        self.end_date_filter.delete(0, 'end')
        self.end_date_filter.insert(0, end_date.strftime('%Y-%m-%d'))
        
        self.day_filter_combo.set("همه")
        self.category_filter_combo.set("همه")
        
        self.refresh_main_log()

    def refresh_main_log(self):
        for row in self.main_log_tree.get_children():
            self.main_log_tree.delete(row)
        
        start_date_str = self.start_date_filter.get()
        end_date_str = self.end_date_filter.get()
        selected_day = self.day_filter_combo.get()
        selected_category = self.category_filter_combo.get()

        try:
            entries_data = db.get_entries_by_date_range(start_date_str, end_date_str)
        except Exception as e:
            messagebox.showerror("خطای تاریخ", f"فرمت تاریخ صحیح نیست. (YYYY-MM-DD)\n{e}")
            return
        
        for entry in entries_data:
            entry_id, task, cat, start_str, end_str, notes = entry
            cat_name = cat if cat else 'بدون دسته'
            
            try:
                start_dt = datetime.strptime(start_str.replace("T", " ").split('.')[0], '%Y-%m-%d %H:%M:%S')
                
                english_day_name = start_dt.strftime('%A')
                persian_day_name = styles.PERSIAN_WEEKDAYS.get(english_day_name, english_day_name)
                
                day_matches = (selected_day == "همه") or (selected_day == persian_day_name)
                category_matches = (selected_category == "همه") or (selected_category == cat_name)

                if not (day_matches and category_matches):
                    continue 

                jalali_date = jdatetime.date.fromgregorian(date=start_dt.date())
                
                values = {
                    "date": jalali_date.strftime('%y/%m/%d'),
                    "day_of_week": persian_day_name,
                    "start_time": start_dt.strftime('%H:%M'),
                    "task_name": task,
                    "category": cat_name
                }
                
                if end_str:
                    end_dt = datetime.strptime(end_str.replace("T", " ").split('.')[0], '%Y-%m-%d %H:%M:%S')
                    duration = end_dt - start_dt
                    total_seconds = duration.total_seconds()
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    values["end_time"] = end_dt.strftime('%H:%M')
                    values["duration"] = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
                else:
                    values["end_time"] = "در حال اجرا"
                    values["duration"] = "--:--:--"
                
                ordered_values = [values.get(col_id, "") for col_id in styles.TREEVIEW_COLUMN_ORDER]
                self.main_log_tree.insert("", "end", iid=entry_id, values=ordered_values)

            except (ValueError, TypeError) as e:
                print(f"Error processing entry ID {entry_id}: {start_str} - {e}")

    def populate_categories(self):
        categories = db.get_categories()
        cat_names = [name for _, name in categories]
        self.category_combo['values'] = cat_names
        self.category_filter_combo['values'] = ["همه"] + cat_names
        self.category_map = {name: cat_id for cat_id, name in categories}
        self.id_to_category_map = {cat_id: name for cat_id, name in categories}

    def update_timer(self):
        if self.is_running and self.start_time:
            elapsed = datetime.now() - self.start_time
            total_seconds = elapsed.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            hundredths = int((total_seconds - int(total_seconds)) * 100)
            self.elapsed_time.set(f"{minutes:02}:{seconds:02}.{hundredths:02}")
        self.after(10, self.update_timer)

    def start_new_task(self):
        task_name = self.task_name_entry.get().strip()
        if not task_name:
            messagebox.showerror("خطا", "لطفاً یک عنوان برای کار وارد کنید.")
            return
        
        category_name = self.category_combo.get()
        category_id = None
        if category_name:
            category_id = db.get_category_id_by_name(category_name)
        
        notes = self.notes_entry.get().strip()
        
        entry_id = db.start_tracking(task_name, category_id, notes)
        self.current_entry = {
            'id': entry_id,
            'name': task_name,
            'category': category_name,
            'notes': notes
        }
        
        self.is_running = True
        self.start_time = datetime.now()
        self.update_ui_state()
        self.refresh_main_log()

    def stop_current_task(self):
        if not self.current_entry:
            return
            
        notes = self.notes_entry.get().strip()
        db.stop_tracking(self.current_entry['id'], self.current_entry['name'], notes)
        
        self.current_entry = None
        self.is_running = False
        self.start_time = None
        self.elapsed_time.set("00:00.00")
        
        self.update_ui_state()
        self.refresh_main_log()

    def update_ui_state(self):
        if self.is_running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def toggle_theme(self):
        self.style.theme_use(styles.DARK_THEME if self.is_dark_mode.get() else styles.LIGHT_THEME)

    def show_treeview_menu(self, event):
        item = self.main_log_tree.identify_row(event.y)
        if item:
            self.main_log_tree.selection_set(item)
            self.selected_entry_id = item
            self.treeview_menu.post(event.x_root, event.y_root)

    def edit_selected_entry(self):
        selected_item = self.main_log_tree.selection()
        if not selected_item:
            return
            
        entry_id = selected_item[0]
        ui_windows.EditEntryWindow(self, entry_id)

    def delete_selected_entry(self):
        selected_item = self.main_log_tree.selection()
        if not selected_item:
            return
            
        entry_id = selected_item[0]
        if messagebox.askyesno("تایید حذف", "آیا مطمئن هستید می‌خواهید این فعالیت را حذف کنید؟"):
            db.delete_entry(entry_id)
            self.refresh_main_log()

    def resume_selected_entry(self):
        if not hasattr(self, 'selected_entry_id') or not self.selected_entry_id:
            return
        
        entry_data = db.get_entry_by_id(self.selected_entry_id)
        if not entry_data:
            return
        
        if self.current_entry:
            self.stop_current_task()
        
        entry_id, task_name, category_id, start_time, end_time, notes = entry_data
        new_entry_id = db.start_tracking(task_name, category_id, notes)
        self.current_entry = {
            'id': new_entry_id,
            'name': task_name,
            'category': self.id_to_category_map.get(category_id, ''),
            'notes': notes
        }
        
        self.is_running = True
        self.start_time = datetime.now()
        self.update_ui_state()
        self.refresh_main_log()