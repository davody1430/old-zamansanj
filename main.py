from app import TimeTrackerApp
import styles

if __name__ == "__main__":
    # اجرای برنامه با تم پیش‌فرض روشن که در فایل استایل مشخص شده است
    app = TimeTrackerApp(themename=styles.LIGHT_THEME)
    app.mainloop()