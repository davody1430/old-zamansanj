# ==========================================================
#  File: reports.py  (بازنویسی کامل + تطابق با استایل‌های جدید)
# ==========================================================
import jdatetime
from datetime import datetime
import json
import csv
import os
import styles


# ------------------------------------------------------------------
# 1) دیکشنری‌های ترجمه‌ی روز و ماه (دریافت از styles)
# ------------------------------------------------------------------
PERSIAN_WEEKDAYS = styles.PERSIAN_WEEKDAYS
PERSIAN_MONTHS   = styles.PERSIAN_MONTHS


# ------------------------------------------------------------------
# 2) قالب HTML گزارش با استایل‌های یک‌پارچه
# ------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>گزارش زمانی</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {{
            font-family: 'Vazirmatn', sans-serif;
            background-color: #f4f7f6;
            color: #333;
            margin: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1, h2 {{
            color: #0056b3;
            border-bottom: 2px solid #0056b3;
            padding-bottom: 10px;
        }}
        .summary ul {{
            list-style-type: none;
            padding: 0;
        }}
        .summary li {{
            background: #e9ecef;
            margin-bottom: 8px;
            padding: 10px;
            border-radius: 4px;
        }}
        .details .date-group {{
            margin-bottom: 20px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
        }}
        .details .date-header {{
            font-size: 1.2em;
            font-weight: bold;
            color: #28a745;
        }}
        .daily-summary {{
            font-weight: bold;
            color: #5a6268;
            padding: 5px 0 10px 0;
            margin-right: 5px;
        }}
        .details ul {{
            padding-right: 20px;
        }}
        .details li {{
            margin-bottom: 5px;
        }}
        .notes {{
            color: #6c757d;
            font-size: 0.9em;
            padding-right: 15px;
        }}
        .chart-container {{
            width: 60%;
            margin: 40px auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 گزارش زمانی فعالیت‌ها</h1>

        <div class="chart-container">
            <h2>تخصیص زمان بر اساس دسته‌بندی</h2>
            <canvas id="categoryChart"></canvas>
        </div>

        <div class="summary">
            <h2>خلاصه روزانه</h2>
            <ul>{daily_summary_section}</ul>
        </div>

        <div class="summary">
            <h2>خلاصه فعالیت‌ها (بر اساس عنوان)</h2>
            <ul>{summary_section}</ul>
        </div>

        <div class="details">
            <h2>جزئیات زمانی</h2>
            {details_section}
        </div>
    </div>

    <script>
        Chart.defaults.font.family = 'Vazirmatn';
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = {{
            labels: {chart_labels},
            datasets: [{{
                label: 'ساعت',
                data: {chart_data},
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)', 'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }}]
        }};
        new Chart(ctx, {{
            type: 'pie',
            data: categoryData,
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }} }}
        }});
    </script>
</body>
</html>
"""


# ------------------------------------------------------------------
# 3) فرمت زمان به فارسی
# ------------------------------------------------------------------
def _format_duration(total_seconds: float, show_seconds: bool = True) -> str:
    """تبدیل ثانیه به رشتی مثل '۲ ساعت و ۱۵ دقیقه'"""
    if total_seconds < 0:
        total_seconds = 0

    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    parts = []
    if int(hours) > 0:
        parts.append(f"{int(hours)} ساعت")
    if int(minutes) > 0:
        parts.append(f"{int(minutes)} دقیقه")
    if show_seconds and int(seconds) > 0:
        parts.append(f"{int(seconds)} ثانیه")

    if not parts:
        return "۰ دقیقه" if not show_seconds else "۰ ثانیه"

    return " و ".join(parts)


# ------------------------------------------------------------------
# 4) تولید خروجی HTML
# ------------------------------------------------------------------
def generate_html_report(entries: list) -> str:
    """دریافت لیست رکوردها و بازگرداندن رشته‌ی HTML کامل"""
    if not entries:
        return HTML_TEMPLATE.format(
            daily_summary_section="<li>هیچ فعالیتی یافت نشد.</li>",
            summary_section="<li>هیچ فعالیتی یافت نشد.</li>",
            details_section="<p>داده‌ای یافت نشد.</p>",
            chart_labels="[]",
            chart_data="[]"
        )

    summary_tasks: dict[str, float] = {}
    summary_categories: dict[str, float] = {}
    details_by_date: dict[datetime.date, list[dict]] = {}

    for entry in entries:
        _, task_name, category, start_str, end_str, notes = entry
        category = category or "بدون دسته"
        if not (start_str and end_str):
            continue

        start_dt = datetime.strptime(start_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        duration_sec = (end_dt - start_dt).total_seconds()

        summary_tasks[task_name] = summary_tasks.get(task_name, 0.0) + duration_sec
        summary_categories[category] = summary_categories.get(category, 0.0) + duration_sec

        date_key = start_dt.date()
        details_by_date.setdefault(date_key, []).append({
            "start_time": start_dt.strftime("%H:%M"),
            "end_time": end_dt.strftime("%H:%M"),
            "duration_seconds": duration_sec,
            "task_name": task_name,
            "notes": notes.strip() if notes else None
        })

    # ----------------------------------------------------------
    # ساخت بخش خلاصه‌ی فعالیت‌ها (بر اساس عنوان)
    # ----------------------------------------------------------
    summary_html = ""
    for task, sec in sorted(summary_tasks.items()):
        summary_html += f"<li>مجموع '{task}': {_format_duration(sec, show_seconds=False)}</li>\n"

    # ----------------------------------------------------------
    # ساخت بخش خلاصه‌ی روزانه
    # ----------------------------------------------------------
    daily_summary_html = ""
    for date_obj in sorted(details_by_date.keys()):
        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        persian_day = PERSIAN_WEEKDAYS.get(date_obj.strftime("%A"), date_obj.strftime("%A"))
        total_day_sec = sum(item["duration_seconds"] for item in details_by_date[date_obj])
        daily_summary_html += (
            f"<li>🗓️ {jalali_date.strftime('%Y/%m/%d')} {persian_day}: "
            f"{_format_duration(total_day_sec)}</li>\n"
        )

    # ----------------------------------------------------------
    # ساخت بخش جزئیات
    # ----------------------------------------------------------
    details_html = ""
    for date_obj in sorted(details_by_date.keys()):
        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        persian_day = PERSIAN_WEEKDAYS.get(date_obj.strftime("%A"), date_obj.strftime("%A"))
        total_day_sec = sum(item["duration_seconds"] for item in details_by_date[date_obj])

        details_html += (
            f'<div class="date-group">\n'
            f'<p class="date-header">🗓️ {jalali_date.strftime("%Y/%m/%d")} {persian_day}</p>\n'
            f'<p class="daily-summary">مجموع فعالیت‌های روز: {_format_duration(total_day_sec, show_seconds=False)}</p>\n<ul>'
        )

        for item in sorted(details_by_date[date_obj], key=lambda x: x["start_time"]):
            dur_txt = _format_duration(item["duration_seconds"], show_seconds=True)
            details_html += (
                f"<li>{item['task_name']} ({dur_txt}) | "
                f"از {item['start_time']} تا {item['end_time']}</li>\n"
            )
            if item["notes"]:
                details_html += f"<li class='notes'>یادداشت: {item['notes']}</li>\n"

        details_html += "</ul>\n</div>\n"

    # ----------------------------------------------------------
    # داده‌های نمودار
    # ----------------------------------------------------------
    chart_labels = list(summary_categories.keys())
    chart_data = [round(sec / 3600, 2) for sec in summary_categories.values()]

    # ----------------------------------------------------------
    # پر کردن قالب و بازگرداندن HTML نهایی
    # ----------------------------------------------------------
    return HTML_TEMPLATE.format(
        daily_summary_section=daily_summary_html,
        summary_section=summary_html,
        details_section=details_html,
        chart_labels=json.dumps(chart_labels, ensure_ascii=False),
        chart_data=json.dumps(chart_data)
    )


# ------------------------------------------------------------------
# 5) خروجی CSV
# ------------------------------------------------------------------
def export_to_csv(entries: list, file_path: str) -> str:
    """ذخیره‌ی رکوردها در فایل CSV"""
    headers = ["id", "task_name", "category", "start_time", "end_time", "notes"]

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(entries)

    return f"گزارش با موفقیت در {file_path} ذخیره شد."