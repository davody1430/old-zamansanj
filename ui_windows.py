import ttkbootstrap as ttkb
from tkinter import messagebox, simpledialog, Toplevel, filedialog, Text
import database as db
import reports
from datetime import datetime, timedelta
import styles
import webbrowser
import tempfile
import os

class CategoryManagerWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("مدیریت دسته‌ها")
        self.transient(master)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = 300 
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.listbox = ttkb.Treeview(self, columns=("id", "name"), show="headings", height=10)
        self.listbox.heading("id", text="شناسه")
        self.listbox.heading("name", text="نام دسته")
        self.listbox.column("id", width=80, anchor="center")
        self.listbox.column("name", width=200, anchor="e")
        self.listbox.pack(padx=10, pady=10)
        
        self.refresh_listbox()
        
        btn_frame = ttkb.Frame(self)
        btn_frame.pack(pady=5)
        
        ttkb.Button(btn_frame, text="حذف", command=self.delete_selected, bootstyle=styles.BUTTON_DANGER).pack(side="right", padx=5)
        ttkb.Button(btn_frame, text="افزودن", command=self.add_new, bootstyle=styles.BUTTON_SUCCESS).pack(side="right", padx=5)

    def refresh_listbox(self):
        for row in self.listbox.get_children():
            self.listbox.delete(row)
        for cat_id, name in db.get_categories():
            self.listbox.insert("", "end", values=(cat_id, name))

    def add_new(self):
        name = simpledialog.askstring("افزودن دسته", "نام دسته جدید را وارد کنید:", parent=self)
        if name:
            db.add_category(name)
            self.refresh_listbox()
            self.master.populate_categories()

    def delete_selected(self):
        selected_item = self.listbox.selection()
        if not selected_item:
            return
            
        cat_id = self.listbox.item(selected_item[0])['values'][0]
        cat_name = self.listbox.item(selected_item[0])['values'][1]
        
        if db.is_category_used(cat_id):
            messagebox.showerror("خطا", f"دسته '{cat_name}' در فعالیت‌ها استفاده شده و قابل حذف نیست.", parent=self)
            return
            
        if messagebox.askyesno("تایید حذف", f"آیا مطمئن هستید می‌خواهید دسته '{cat_name}' را حذف کنید؟", parent=self):
            db.delete_category(cat_id)
            self.refresh_listbox()
            self.master.populate_categories()

class ReportGeneratorWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("ساخت گزارش")
        self.transient(master)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = 350
        height = 250
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        frame = ttkb.Frame(self, padding=10)
        frame.pack()

        ttkb.Label(frame, text="از تاریخ (YYYY-MM-DD):").pack(pady=5)
        self.start_date_entry = ttkb.Entry(frame, justify='center')
        self.start_date_entry.insert(0, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        self.start_date_entry.pack(pady=5)

        ttkb.Label(frame, text="تا تاریخ (YYYY-MM-DD):").pack(pady=5)
        self.end_date_entry = ttkb.Entry(frame, justify='center')
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.end_date_entry.pack(pady=5)

        btn_frame = ttkb.Frame(self)
        btn_frame.pack(pady=20)
        ttkb.Button(btn_frame, text="ساخت گزارش (HTML)", command=self.generate_and_show_report, bootstyle=styles.BUTTON_PRIMARY).pack(side="right", padx=5)
        ttkb.Button(btn_frame, text="خروجی CSV", command=self.export_csv, bootstyle=styles.BUTTON_SECONDARY).pack(side="right", padx=5)

    def generate_and_show_report(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        entries = db.get_entries_by_date_range(start_date, end_date)

        if not entries:
            messagebox.showinfo("اطلاعات", "داده‌ای برای ساخت گزارش در این بازه زمانی وجود ندارد.", parent=self)
            return

        report_html = reports.generate_html_report(entries)
        
        try:
            # --- بخش اصلاح شده برای ذخیره در پوشه مشخص ---

            # 1. ساخت نام و مسیر پوشه خروجی
            output_dir = "reports_output"
            os.makedirs(output_dir, exist_ok=True) # پوشه را اگر وجود نداشته باشد می‌سازد

            # 2. ساخت یک نام فایل منحصر به فرد با تاریخ و زمان
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"report_{timestamp}.html"
            file_path = os.path.join(output_dir, file_name)

            # 3. نوشتن محتوای گزارش در فایل جدید
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(report_html)
            
            # 4. باز کردن فایل در مرورگر
            webbrowser.open('file://' + os.path.realpath(file_path))

            messagebox.showinfo(
                "گزارش ساخته شد",
                f"گزارش با موفقیت در پوشه 'reports_output' ذخیره شد.",
                parent=self
            )
            # --- پایان بخش اصلاح شده ---

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ساخت یا باز کردن فایل گزارش: {e}", parent=self)
    def export_csv(self):
        entries = db.get_entries_by_date_range(self.start_date_entry.get(), self.end_date_entry.get())
        if not entries:
            messagebox.showinfo("اطلاعات", "داده‌ای برای خروجی در این بازه زمانی وجود ندارد.", parent=self)
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                               filetypes=[("CSV files", "*.csv")])
        if file_path:
            message = reports.export_to_csv(entries, file_path)
            messagebox.showinfo("موفقیت", message, parent=self)

class EditEntryWindow(Toplevel):
    def __init__(self, master, entry_id):
        super().__init__(master)
        self.master = master
        self.entry_id = entry_id
        self.title("ویرایش فعالیت")
        self.transient(master)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = 400
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
        frame.pack()
        
        ttkb.Label(frame, text=":عنوان").grid(row=0, column=1, padx=5, pady=5, sticky='e')
        self.task_entry = ttkb.Entry(frame, width=40, justify='right')
        self.task_entry.insert(0, task_name)
        self.task_entry.grid(row=0, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":دسته").grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.cat_combo = ttkb.Combobox(frame, state="readonly", 
                                     values=[''] + list(self.master.category_map.keys()), 
                                     justify='right')
        self.cat_combo.set(self.master.id_to_category_map.get(category_id, ''))
        self.cat_combo.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text=":زمان شروع").grid(row=2, column=1, padx=5, pady=5, sticky='e')
        self.start_entry = ttkb.Entry(frame, width=40, justify='center')
        self.start_entry.insert(0, start_time_str)
        self.start_entry.grid(row=2, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":زمان پایان").grid(row=3, column=1, padx=5, pady=5, sticky='e')
        self.end_entry = ttkb.Entry(frame, width=40, justify='center')
        if end_time_str:
            self.end_entry.insert(0, end_time_str)
        self.end_entry.grid(row=3, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":یادداشت").grid(row=4, column=1, padx=5, pady=5, sticky='e')
        self.notes_text = Text(frame, width=30, height=4, font=styles.DEFAULT_FONT)
        self.notes_text.grid(row=4, column=0, padx=5, pady=5)
        if notes:
            self.notes_text.insert('1.0', notes)
        
        ttkb.Button(frame, text="ذخیره تغییرات", 
                   command=self.save_changes, 
                   bootstyle=styles.BUTTON_PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)

    def save_changes(self):
        try:
            new_task = self.task_entry.get()
            new_cat_name = self.cat_combo.get()
            new_cat_id = self.master.category_map.get(new_cat_name)
            new_start = datetime.strptime(self.start_entry.get(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            new_end_str = self.end_entry.get()
            new_end = datetime.strptime(new_end_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') if new_end_str else None
            new_notes = self.notes_text.get('1.0', 'end-1c')
            
            if not new_task:
                messagebox.showerror("خطا", "عنوان فعالیت نمی‌تواند خالی باشد.", parent=self)
                return
                
            db.update_entry(self.entry_id, new_task, new_cat_id, new_start, new_end, new_notes)
            self.master.refresh_main_log()
            self.destroy()
            
        except ValueError:
            messagebox.showerror("خطا", "فرمت تاریخ یا زمان صحیح نیست.\nفرمت صحیح: YYYY-MM-DD HH:MM:SS", parent=self)

class AddManualEntryWindow(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("افزودن دستی فعالیت")
        self.transient(master)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = 400
        height = 400
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        frame = ttkb.Frame(self, padding="10")
        frame.pack()
        
        ttkb.Label(frame, text=":عنوان").grid(row=0, column=1, padx=5, pady=5, sticky='e')
        self.task_entry = ttkb.Entry(frame, width=40, justify='right')
        self.task_entry.grid(row=0, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":دسته").grid(row=1, column=1, padx=5, pady=5, sticky='e')
        self.cat_combo = ttkb.Combobox(frame, state="readonly", 
                                     values=[''] + list(self.master.category_map.keys()), 
                                     justify='right')
        self.cat_combo.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        ttkb.Label(frame, text=":زمان شروع").grid(row=2, column=1, padx=5, pady=5, sticky='e')
        self.start_entry = ttkb.Entry(frame, width=40, justify='center')
        self.start_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:00'))
        self.start_entry.grid(row=2, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":زمان پایان").grid(row=3, column=1, padx=5, pady=5, sticky='e')
        self.end_entry = ttkb.Entry(frame, width=40, justify='center')
        self.end_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:00'))
        self.end_entry.grid(row=3, column=0, padx=5, pady=5)
        
        ttkb.Label(frame, text=":یادداشت").grid(row=4, column=1, padx=5, pady=5, sticky='e')
        self.notes_text = Text(frame, width=30, height=4, font=styles.DEFAULT_FONT)
        self.notes_text.grid(row=4, column=0, padx=5, pady=5)
        
        ttkb.Button(frame, text="ذخیره فعالیت", 
                   command=self.save_new_entry, 
                   bootstyle=styles.BUTTON_PRIMARY).grid(row=5, column=0, columnspan=2, pady=10)

    def save_new_entry(self):
        try:
            task = self.task_entry.get()
            cat_name = self.cat_combo.get()
            cat_id = self.master.category_map.get(cat_name)
            start_time = datetime.strptime(self.start_entry.get(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(self.end_entry.get(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            notes = self.notes_text.get('1.0', 'end-1c')
            
            if not task:
                messagebox.showerror("خطا", "عنوان فعالیت نمی‌تواند خالی باشد.", parent=self)
                return
                
            if start_time >= end_time:
                messagebox.showerror("خطا", "زمان پایان باید بعد از زمان شروع باشد.", parent=self)
                return
                
            db.add_manual_entry(task, cat_id, start_time, end_time, notes)
            self.master.refresh_main_log()
            self.destroy()
            
        except ValueError:
            messagebox.showerror("خطا", "فرمت تاریخ یا زمان صحیح نیست.\nفرمت صحیح: YYYY-MM-DD HH:MM:SS", parent=self)