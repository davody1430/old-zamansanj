import jdatetime
from datetime import datetime
import csv
import json

# قالب اصلی گزارش شامل استایل، کدهای جاوااسکریپت برای نمودار و بخش‌های مختلف
# نسخه اصلاح شده با آکولادهای صحیح برای جاوا اسکریپت
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>گزارش زمانی</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Tahoma', sans-serif;
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
        .summary, .details {{
            margin-bottom: 30px;
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
            <h2>خلاصه فعالیت‌ها</h2>
            <ul>
                {summary_section}
            </ul>
        </div>

        <div class="details">
            <h2>جزئیات زمانی</h2>
            {details_section}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = {{
            labels: {chart_labels},
            datasets: [{{
                label: 'ساعت',
                data: {chart_data},
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(199, 199, 199, 0.7)'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }}]
        }};

        new Chart(ctx, {{
            type: 'pie',
            data: categoryData,
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{
                           font: {{
                                family: 'Tahoma'
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

def generate_html_report(entries):
    """
    گزارش کامل HTML شامل نمودار و جزئیات را با پایتون خالص تولید می‌کند.
    """
    if not entries:
        return HTML_TEMPLATE.format(
            summary_section="<li>هیچ فعالیتی برای گزارش وجود ندارد.</li>",
            details_section="<p>داده‌ای یافت نشد.</p>",
            chart_labels="[]",
            chart_data="[]"
        )

    # --- پردازش داده‌ها ---
    summary_tasks = {}
    summary_categories = {}
    details_by_date = {}

    for entry in entries:
        _, task_name, category, start_str, end_str, notes = entry
        category = category if category else 'بدون دسته'
        
        if not start_str or not end_str:
            continue

        start_dt = datetime.strptime(start_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(end_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        duration_seconds = (end_dt - start_dt).total_seconds()
        
        # برای خلاصه وظایف
        summary_tasks[task_name] = summary_tasks.get(task_name, 0) + duration_seconds
        
        # برای نمودار دسته‌بندی
        summary_categories[category] = summary_categories.get(category, 0) + duration_seconds
        
        # برای جزئیات روزانه
        date_key = start_dt.date()
        if date_key not in details_by_date:
            details_by_date[date_key] = []
        
        details_by_date[date_key].append({
            'start_time': start_dt.strftime('%H:%M'),
            'end_time': end_dt.strftime('%H:%M'),
            'duration_seconds': duration_seconds, # --- اصلاح شده: ذخیره ثانیه کل ---
            'task_name': task_name,
            'notes': notes if notes and notes.strip() else None
        })

    # --- ساخت بخش‌های HTML ---

    # 1. خلاصه وظایف (بخش اصلاح شده)
    summary_html = ""
    if summary_tasks:
        for task, total_seconds in summary_tasks.items():
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            summary_html += f"<li>مجموع '{task}': {int(hours)} ساعت و {int(minutes)} دقیقه و {int(seconds)} ثانیه</li>"
    else:
        summary_html = "<li>هیچ فعالیتی یافت نشد.</li>"

    # 2. جزئیات روزانه (بخش اصلاح شده)
    details_html = ""
    sorted_dates = sorted(details_by_date.keys(), reverse=True)
    for date_obj in sorted_dates:
        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        date_str = jalali_date.strftime('%Y/%m/%d')
        details_html += f'<div class="date-group"><p class="date-header">🗓️ {date_str}</p><ul>'
        
        sorted_entries = sorted(details_by_date[date_obj], key=lambda x: x['start_time'])
        for item in sorted_entries:
            # محاسبه دقیقه و ثانیه از کل ثانیه‌ها
            item_minutes, item_seconds = divmod(item['duration_seconds'], 60)
            duration_text = f"{int(item_minutes)} دقیقه و {int(item_seconds)} ثانیه"
            
            details_html += (
                f"<li>{item['task_name']} ({duration_text}) | "
                f"از {item['start_time']} تا {item['end_time']}</li>"
            )
            if item['notes']:
                details_html += f"<li class='notes'>یادداشت: {item['notes']}</li>"
        details_html += "</ul></div>"

    # 3. داده‌های نمودار
    chart_labels = list(summary_categories.keys())
    chart_data = [round(v / 3600, 2) for v in summary_categories.values()] # تبدیل به ساعت

    # --- تزریق داده‌ها به قالب اصلی ---
    return HTML_TEMPLATE.format(
        summary_section=summary_html,
        details_section=details_html,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data)
    )

def export_to_csv(entries, file_path):
    """
    داده‌ها را با استفاده از ماژول استاندارد csv به فایل CSV منتقل می‌کند.
    """
    headers = ['id', 'task_name', 'category', 'start_time', 'end_time', 'notes']
    
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(entries)
        
    return f"گزارش با موفقیت در {file_path} ذخیره شد."