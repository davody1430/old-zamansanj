import ttkbootstrap as ttkb
from tkinter import messagebox, simpledialog, Toplevel, filedialog, Text
import database as db
import reports
from datetime import datetime, timedelta
import jdatetime
import styles
import webbrowser
import os
from custom_widgets import DateEntry


class CategoryManagerWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("مدیریت دسته‌ها")
        self.transient(master)
        self.grab_set()
        self.geometry("330x360")
        self.resizable(False, False)

        # Treeview -------------------------------------------------
        self.tree = ttkb.Treeview(
            self, columns=("id", "name"), show="headings", height=11
        )
        self.tree.heading("id", text="شناسه")
        self.tree.heading("name", text="نام دسته")
        self.tree.column("id", width=70, anchor="center")
        self.tree.column("name", width=240, anchor="e")
        self.tree.pack(padx=10, pady=5)

        # دکمه‌ها --------------------------------------------------
        btn_frame = ttkb.Frame(self)
        btn_frame.pack(pady=7)
        ttkb.Button(
            btn_frame, text="افزودن", command=self.add_new,
            bootstyle="success-outline", width=8
        ).pack(side="right", padx=4)
        ttkb.Button(
            btn_frame, text="ویرایش", command=self.edit_selected,
            bootstyle="warning-outline", width=8
        ).pack(side="right", padx=4)
        ttkb.Button(
            btn_frame, text="حذف", command=self.delete_selected,
            bootstyle="danger-outline", width=8
        ).pack(side="right", padx=4)

        # منوی راست-کلیک ------------------------------------------
        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label="ویرایش", command=self.edit_selected)
        self.popup.add_command(label="حذف", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_popup)

        # پر کردن اولیه
        self.refresh_list()

    # -----------------------------------------------------------
    def show_popup(self, event):
        """نمایش منو در محل اشاره‌گر ماوس"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.popup.tk_popup(event.x_root, event.y_root)

    def refresh_list(self):
        """خالی کردن و دوباره پر کردن Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cat_id, name in db.get_categories():
            self.tree.insert("", "end", values=(cat_id, name))

    def add_new(self):
        name = simpledialog.askstring(
            "افزودن دسته", "نام دسته جدید:", parent=self
        )
        if name and name.strip():
            if db.get_category_id_by_name(name.strip()) is None:
                db.add_category(name.strip())
                self.refresh_list()
                self.master.populate_categories()  # ComboBox اصلی
                messagebox.showinfo("موفقیت", "دسته افزوده شد.", parent=self)
            else:
                messagebox.showerror("خطا", "نام تکراری است.", parent=self)

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("انتخاب نشده", "یک دسته را انتخاب کنید.", parent=self)
            return
        cat_id, old_name = self.tree.item(sel[0])["values"]
        new_name = simpledialog.askstring(
            "ویرایش دسته", f"نام جدید برای '{old_name}':",
            initialvalue=old_name, parent=self
        )
        if new_name and new_name.strip() and new_name != old_name:
            ok = db.update_category_name(cat_id, new_name.strip())
            if ok:
                self.refresh_list()
                self.master.populate_categories()
                messagebox.showinfo("موفقیت", "دسته ویرایش شد.", parent=self)
            else:
                messagebox.showerror("خطا", "نام تکراری است.", parent=self)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("انتخاب نشده", "یک دسته را انتخاب کنید.", parent=self)
            return
        cat_id, cat_name = self.tree.item(sel[0])["values"]
        if db.is_category_used(cat_id):
            messagebox.showerror("خطا", "دسته در فعالیت‌ها استفاده شده و قابل حذف نیست.", parent=self)
            return
        if messagebox.askyesno("تأیید", f"دسته '{cat_name}' حذف شود؟", parent=self):
            db.delete_category(cat_id)
            self.refresh_list()
            self.master.populate_categories()
            messagebox.showinfo("موفقیت", "دسته حذف شد.", parent=self)

class ReportGeneratorWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("ساخت گزارش")
        self.transient(master)
        self.grab_set()

        self.geometry("350x280")
        self.resizable(False, False)

        # ---------------------- فریم اصلی ----------------------
        main_frame = ttkb.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # ---------------------- فیلدهای تاریخ ----------------------
        ttkb.Label(main_frame, text="از تاریخ (مثال: ۱۴۰۴/۰۶/۰۱)").grid(row=0, column=1, sticky="e", padx=5, pady=5)
        self.start_date_entry = DateEntry(main_frame, justify="center", width=14)
        start_default = jdatetime.date.today() - jdatetime.timedelta(days=7)
        self.start_date_entry.set(start_default.strftime("%Y/%m/%d"))
        self.start_date_entry.grid(row=0, column=0, padx=5, pady=5)

        ttkb.Label(main_frame, text="تا تاریخ (مثال: ۱۴۰۴/۰۶/۳۰)").grid(row=1, column=1, sticky="e", padx=5, pady=5)
        self.end_date_entry = DateEntry(main_frame, justify="center", width=14)
        end_default = jdatetime.date.today()
        self.end_date_entry.set(end_default.strftime("%Y/%m/%d"))
        self.end_date_entry.grid(row=1, column=0, padx=5, pady=5)

        # ---------------------- دکمه‌های خروجی ----------------------
        btn_frame = ttkb.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttkb.Button(
            btn_frame,
            text="گزارش HTML",
            command=self.generate_and_show_report,
            bootstyle=styles.BTN_PRIMARY,
            width=12
        ).pack(side="right", padx=5)

        ttkb.Button(
            btn_frame,
            text="خروجی CSV",
            command=self.export_csv,
            bootstyle=styles.BTN_SECONDARY,
            width=12
        ).pack(side="right", padx=5)

    # ------------------------------------------------------------------
    def _get_gregorian_range(self) -> tuple[str, str] | tuple[None, None]:
        """برگرداندن بازه‌ی میلادی برای کوئری یا None در صورت خطا"""
        try:
            start_j = self.start_date_entry.get()
            end_j = self.end_date_entry.get()
            if "Y" in start_j or "Y" in end_j:
                raise ValueError

            start_g = jdatetime.datetime.strptime(start_j, "%Y/%m/%d").togregorian().date()
            end_g = jdatetime.datetime.strptime(end_j, "%Y/%m/%d").togregorian().date()

            start_db = start_g.strftime("%Y-%m-%d")
            end_db = (end_g + timedelta(days=1)).strftime("%Y-%m-%d")
            return start_db, end_db
        except (ValueError, AttributeError):
            messagebox.showerror(
                "خطای فرمت",
                "فرمت تاریخ شمسی صحیح نیست.\nلطفاً از فرمت YYYY/MM/DD استفاده کنید.",
                parent=self
            )
            return None, None

    # ------------------------------------------------------------------
    def generate_and_show_report(self) -> None:
        start_db, end_db = self._get_gregorian_range()
        if not start_db:
            return

        entries = db.get_entries_by_date_range(start_db, end_db)
        if not entries:
            messagebox.showinfo("اطلاعات", "داده‌ای برای ساخت گزارش در این بازه وجود ندارد.", parent=self)
            return

        html = reports.generate_html_report(entries)
        try:
            os.makedirs("reports_output", exist_ok=True)
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = os.path.join("reports_output", f"report_{stamp}.html")

            with open(file_path, "w", encoding="utf-8-sig") as f:
                f.write(html)

            webbrowser.open("file://" + os.path.abspath(file_path))
            messagebox.showinfo("موفق", f"گزارش HTML در پوشه‌ی reports_output ذخیره و باز شد.", parent=self)
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ساخت یا باز کردن فایل گزارش:\n{e}", parent=self)

    # ------------------------------------------------------------------
    def export_csv(self) -> None:
        start_db, end_db = self._get_gregorian_range()
        if not start_db:
            return

        entries = db.get_entries_by_date_range(start_db, end_db)
        if not entries:
            messagebox.showinfo("اطلاعات", "داده‌ای برای خروجی در این بازه وجود ندارد.", parent=self)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="ذخیره‌ی گزارش CSV"
        )
        if file_path:
            msg = reports.export_to_csv(entries, file_path)
            messagebox.showinfo("موفق", msg, parent=self)

class EditEntryWindow(Toplevel):
    def __init__(self, master, entry_id):
        super().__init__(master)
        self.master = master
        self.entry_id = entry_id
        self.title("ویرایش فعالیت")
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        width = 450
        height = 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        entry_data = db.get_entry_by_id(self.entry_id)
        if not entry_data:
            self.destroy()
            return
            
        _, task_name, category_id, start_time_str, end_time_str, notes = entry_data
        
        frame = ttkb.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        
        ttkb.Label(frame, text="عنوان").grid(row=0, column=1, padx=5, pady=5, sticky='e')
        self.task_entry = ttkb.Entry(frame, width=40, justify='right', font=styles.DEFAULT_FONT)
        self.task_entry.insert(0, task_name)
        self.task_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text="دسته").grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.cat_combo = ttkb.Combobox(frame, state="readonly", 
                                      values=[''] + list(self.master.category_map.keys()), 
                                      justify='right', font=styles.DEFAULT_FONT)
        self.cat_combo.set(self.master.id_to_category_map.get(category_id, ''))
        self.cat_combo.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text="زمان شروع (شمسی)").grid(row=2, column=1, padx=5, pady=5, sticky='e')
        self.start_entry = ttkb.Entry(frame, width=40, justify='center', font=styles.DEFAULT_FONT)
        start_gregorian = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        start_jalali = jdatetime.datetime.fromgregorian(datetime=start_gregorian)
        self.start_entry.insert(0, start_jalali.strftime('%Y/%m/%d %H:%M:%S'))
        self.start_entry.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text="زمان پایان (شمسی)").grid(row=3, column=1, padx=5, pady=5, sticky='e')
        self.end_entry = ttkb.Entry(frame, width=40, justify='center', font=styles.DEFAULT_FONT)
        if end_time_str:
            end_gregorian = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
            end_jalali = jdatetime.datetime.fromgregorian(datetime=end_gregorian)
            self.end_entry.insert(0, end_jalali.strftime('%Y/%m/%d %H:%M:%S'))
        self.end_entry.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text="یادداشت").grid(row=4, column=1, padx=5, pady=5, sticky='e')
        self.notes_text = Text(frame, width=30, height=4, font=styles.DEFAULT_FONT)
        self.notes_text.grid(row=4, column=0, padx=5, pady=5, sticky='ew')
        if notes:
            self.notes_text.insert('1.0', notes)
        
        ttkb.Button(frame, text="ذخیره تغییرات", 
                      command=self.save_changes, 
                      bootstyle=styles.BTN_PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)

    def save_changes(self):
        try:
            new_task = self.task_entry.get()
            new_cat_name = self.cat_combo.get()
            new_cat_id = self.master.category_map.get(new_cat_name)
            
            start_jalali_str = self.start_entry.get()
            start_gregorian = jdatetime.datetime.strptime(start_jalali_str, '%Y/%m/%d %H:%M:%S').togregorian()
            new_start = start_gregorian.strftime('%Y-%m-%d %H:%M:%S')

            end_jalali_str = self.end_entry.get()
            new_end = None
            if end_jalali_str.strip():
                end_gregorian = jdatetime.datetime.strptime(end_jalali_str, '%Y/%m/%d %H:%M:%S').togregorian()
                new_end = end_gregorian.strftime('%Y-%m-%d %H:%M:%S')
            
            new_notes = self.notes_text.get('1.0', 'end-1c')
            
            if not new_task:
                messagebox.showerror("خطا", "عنوان فعالیت نمی‌تواند خالی باشد.", parent=self)
                return
                
            db.update_entry(self.entry_id, new_task, new_cat_id, new_start, new_end, new_notes)
            self.master.refresh_main_log()
            self.destroy()
            
        except ValueError:
            messagebox.showerror("خطای فرمت", "فرمت تاریخ یا زمان شمسی صحیح نیست.\nفرمت صحیح: YYYY/MM/DD HH:MM:SS", parent=self)

class AddManualEntryWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("افزودن دستی فعالیت")
        self.transient(master)
        self.grab_set()
        
        self.update_idletasks()
        width = 450
        height = 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        frame = ttkb.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        
        ttkb.Label(frame, text="عنوان").grid(row=0, column=1, padx=5, pady=5, sticky='e')
        self.task_entry = ttkb.Entry(frame, width=40, justify='right', font=styles.DEFAULT_FONT)
        self.task_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text="دسته").grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.cat_combo = ttkb.Combobox(frame, state="readonly", 
                                      values=[''] + list(self.master.category_map.keys()), 
                                      justify='right', font=styles.DEFAULT_FONT)
        self.cat_combo.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        # Separate Date and Time entries
        ttkb.Label(frame, text="تاریخ (شمسی)").grid(row=2, column=1, padx=5, pady=5, sticky='e')
        self.date_entry = DateEntry(frame, width=15, justify='center', font=styles.DEFAULT_FONT)
        self.date_entry.set(jdatetime.date.today().strftime('%Y/%m/%d'))
        self.date_entry.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        time_frame = ttkb.Frame(frame)
        time_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky='ew')

        ttkb.Label(time_frame, text="زمان پایان (HH:MM)").pack(side='right', padx=5)
        self.end_time_entry = ttkb.Entry(time_frame, width=8, justify='center', font=styles.DEFAULT_FONT)
        self.end_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime('%H:%M'))
        self.end_time_entry.pack(side='right', padx=5)

        ttkb.Label(time_frame, text="زمان شروع (HH:MM)").pack(side='right', padx=5)
        self.start_time_entry = ttkb.Entry(time_frame, width=8, justify='center', font=styles.DEFAULT_FONT)
        self.start_time_entry.insert(0, datetime.now().strftime('%H:%M'))
        self.start_time_entry.pack(side='right', padx=5)

        ttkb.Label(frame, text="یادداشت").grid(row=4, column=1, padx=5, pady=5, sticky='e')
        self.notes_text = Text(frame, width=30, height=4, font=styles.DEFAULT_FONT)
        self.notes_text.grid(row=4, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Button(frame, text="تایید",
                      command=self.save_new_entry, 
                      bootstyle=styles.BTN_PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)

    def save_new_entry(self):
        try:
            task = self.task_entry.get()
            cat_name = self.cat_combo.get()
            cat_id = self.master.category_map.get(cat_name)

            date_str = self.date_entry.get()
            start_time_str = self.start_time_entry.get()
            end_time_str = self.end_time_entry.get()

            # Combine date and time and convert to Gregorian
            start_jalali_str = f"{date_str} {start_time_str}:00"
            start_gregorian = jdatetime.datetime.strptime(start_jalali_str, '%Y/%m/%d %H:%M:%S').togregorian()
            start_time_for_db = start_gregorian.strftime('%Y-%m-%d %H:%M:%S')

            end_jalali_str = f"{date_str} {end_time_str}:00"
            end_gregorian = jdatetime.datetime.strptime(end_jalali_str, '%Y/%m/%d %H:%M:%S').togregorian()
            end_time_for_db = end_gregorian.strftime('%Y-%m-%d %H:%M:%S')
            
            notes = self.notes_text.get('1.0', 'end-1c')
            
            if not task:
                messagebox.showerror("خطا", "عنوان فعالیت نمی‌تواند خالی باشد.", parent=self)
                return
                
            if start_gregorian >= end_gregorian:
                messagebox.showerror("خطا", "زمان پایان باید بعد از زمان شروع باشد.", parent=self)
                return

            if messagebox.askyesno("تایید", "آیا از افزودن این فعالیت اطمینان دارید؟", parent=self):
                db.add_manual_entry(task, cat_id, start_time_for_db, end_time_for_db, notes)
                self.master.refresh_main_log()
                self.destroy()

        except ValueError:
            messagebox.showerror("خطای فرمت", "فرمت تاریخ یا زمان شمسی صحیح نیست.\nفرمت تاریخ: YYYY/MM/DD\nفرمت زمان: HH:MM", parent=self)
