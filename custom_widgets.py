# ==========================================================
#  File: custom_widgets.py  (بازنویسی کامل + تطابق با استایل‌های جدید)
# ==========================================================
import ttkbootstrap as ttkb
import styles
from jalali_datepicker import JalaliDatepicker


class DateEntry(ttkb.Frame):
    """
    A custom widget combining a ttk.Entry for date input (YYYY/MM/DD)
    and a button to open a Jalali calendar popup.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master)

        # The actual Entry widget
        self.entry = ttkb.Entry(self, **kwargs)
        self.entry.pack(side="right", fill="x", expand=True)

        # Button to open the datepicker
        self.calendar_button = ttkb.Button(
            self, text="📅", command=self.open_datepicker,
            bootstyle="secondary", width=2
        )
        self.calendar_button.pack(side="left", padx=(5, 0))

        # --- Validation and Formatting Logic (adapted for self.entry) ---
        vcmd = (self.register(self._validate_input), "%P", "%d", "%i", "%s")
        self.entry.config(validate="key", validatecommand=vcmd)
        self.entry.bind("<FocusOut>", self._format_date_on_focus_out)
        self.entry.bind("<Return>", self._format_date_on_focus_out)

    def open_datepicker(self):
        """Opens the Jalali datepicker to select a date."""
        JalaliDatepicker(self, self)

    def get(self) -> str:
        """Returns the current value of the date entry."""
        return self.entry.get()

    def set(self, date_str: str):
        """Sets the value of the date entry."""
        self.entry.delete(0, "end")
        self.entry.insert(0, date_str)
        self._format_date_on_focus_out()

    def _validate_input(self, proposed_text: str, action_type: str, index_str: str, current_text: str) -> bool:
        """Validation logic for character-by-character input."""
        if action_type == "0":  # Deletion
            index = int(index_str)
            if index in (4, 7):
                return False  # Prevent deleting slashes
            return True

        if len(proposed_text) > 10:
            return False

        index = int(index_str)
        char_to_insert = proposed_text[index] if index < len(proposed_text) else ""

        if index in (4, 7):
            return False  # Don't allow typing over slashes

        return char_to_insert.isdigit()

    def _format_date_on_focus_out(self, event=None):
        """Auto-formats the month and day to be two digits."""
        current_text = self.entry.get().strip()
        if not current_text or "Y" in current_text:
            return

        parts = current_text.split("/")
        if len(parts) != 3:
            return

        year, month, day = parts
        month = month.zfill(2)
        day = day.zfill(2)

        formatted = f"{year}/{month}/{day}"
        if len(year) == 4 and len(month) == 2 and len(day) == 2:
            self.entry.delete(0, "end")
            self.entry.insert(0, formatted)