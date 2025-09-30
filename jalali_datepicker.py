import tkinter as tk
import ttkbootstrap as ttkb
from jdatetime import date as JalaliDate
import jdatetime

class JalaliDatepicker(tk.Toplevel):
    """A Toplevel window for selecting a Jalali date."""
    def __init__(self, master, target_entry, **kwargs):
        super().__init__(master, **kwargs)
        self.target_entry = target_entry
        self.title("انتخاب تاریخ")
        self.geometry("350x320")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Try to parse the existing date from the entry, otherwise use today
        try:
            current_date_str = self.target_entry.get()
            parts = current_date_str.split('/')
            self.selected_date = JalaliDate(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            self.selected_date = JalaliDate.today()

        self.min_year = 1300
        self.max_year = 1500

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        """Creates the widgets for the datepicker."""
        # Frame for month and year selection
        month_year_frame = ttkb.Frame(self)
        month_year_frame.pack(pady=10)

        # Month dropdown
        self.month_var = tk.StringVar(self)
        month_values = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        self.month_dropdown = ttkb.Combobox(
            month_year_frame, textvariable=self.month_var, values=month_values,
            state="readonly", justify="center", width=10
        )
        self.month_dropdown.bind("<<ComboboxSelected>>", self.update_month)
        self.month_dropdown.pack(side="right", padx=5)

        # Year dropdown
        self.year_var = tk.StringVar(self)
        self.year_dropdown = ttkb.Combobox(
            month_year_frame, textvariable=self.year_var,
            values=list(range(self.min_year, self.max_year + 1)),
            state="readonly", justify="center", width=6
        )
        self.year_dropdown.bind("<<ComboboxSelected>>", self.update_year)
        self.year_dropdown.pack(side="left", padx=5)

        # Frame for the calendar days
        self.calendar_frame = ttkb.Frame(self)
        self.calendar_frame.pack(pady=5)

    def create_calendar(self):
        """Creates or recreates the calendar grid."""
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Day names header
        day_names = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        for i, day_name in enumerate(day_names):
            label = ttkb.Label(self.calendar_frame, text=day_name, width=4, anchor="center")
            label.grid(row=0, column=i, padx=2, pady=2)

        year = self.selected_date.year
        month = self.selected_date.month

        # Get number of days in the selected month
        num_days = jdatetime.j_days_in_month[month-1]
        if month == 12 and self.selected_date.isleap():
            num_days = 30

        # Determine the weekday of the first day of the month
        first_day_weekday = JalaliDate(year, month, 1).weekday()
        # Adjust for jdatetime: Saturday is 0, but we want it at index 0.
        # jdatetime: شنبه (0), یکشنبه (1), ... جمعه (6)
        # Our grid: شنبه (0), ... جمعه (6)
        # No adjustment needed.

        # Create day buttons
        for day in range(1, num_days + 1):
            row = (first_day_weekday + day -1) // 7 + 1
            col = (first_day_weekday + day-1) % 7
            button = ttkb.Button(
                self.calendar_frame,
                text=str(day),
                width=3,
                bootstyle="outline",
                command=lambda d=day: self.select_date(d)
            )
            button.grid(row=row, column=col, padx=2, pady=2)
            if day == self.selected_date.day:
                 button.config(bootstyle="success") # Highlight selected day

    def update_display(self):
        """Updates the dropdowns and calendar to reflect the selected_date."""
        self.month_dropdown.set(self.selected_date.strftime("%B"))
        self.year_dropdown.set(self.selected_date.year)
        self.create_calendar()

    def update_month(self, event=None):
        """Handles month dropdown selection change."""
        selected_month_name = self.month_var.get()
        month_index = self.month_dropdown['values'].index(selected_month_name) + 1

        # Prevent day from being out of range (e.g., 31st of a 30-day month)
        last_day_of_new_month = jdatetime.j_days_in_month[month_index-1]
        if month_index == 12 and JalaliDate(self.selected_date.year, 1, 1).isleap():
             last_day_of_new_month = 30

        current_day = self.selected_date.day
        day = min(current_day, last_day_of_new_month)

        self.selected_date = JalaliDate(self.selected_date.year, month_index, day)
        self.update_display()

    def update_year(self, event=None):
        """Handles year dropdown selection change."""
        selected_year = int(self.year_var.get())

        # Handle leap year day change for Esfand
        day = self.selected_date.day
        if self.selected_date.month == 12 and day == 30 and not JalaliDate(selected_year, 1, 1).isleap():
            day = 29

        self.selected_date = JalaliDate(selected_year, self.selected_date.month, day)
        self.update_display()

    def select_date(self, day: int):
        """Sets the target entry's value and closes the window."""
        self.selected_date = JalaliDate(self.selected_date.year, self.selected_date.month, day)
        self.target_entry.set(self.selected_date.strftime("%Y/%m/%d"))
        self.destroy()