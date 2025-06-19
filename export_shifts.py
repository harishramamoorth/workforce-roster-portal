# export_shifts.py
import pandas as pd
import json
from dateutil import parser
import os
import sys

# Allow dynamic Excel path from command line
EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "Roster New.xlsx"

# Weekday to date mapping
day_to_date = {
    'Monday': '2025-06-16',
    'Tuesday': '2025-06-17',
    'Wednesday': '2025-06-18',
    'Thursday': '2025-06-19',
    'Friday': '2025-06-20',
    'Saturday': '2025-06-21',
    'Sunday': '2025-06-22',
}

try:
    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.str.strip()
    print(f"✅ Excel loaded: {EXCEL_FILE}")

    for col in df.columns:
        if 'active' in col.lower():
            df.rename(columns={col: 'Active'}, inplace=True)

    required = ["Day_of_Week", "Employee_Name", "Role"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    shifts = []
    for idx, row in df.iterrows():
        try:
            day = str(row["Day_of_Week"]).strip()
            if day not in day_to_date:
                continue

            note = str(row.get("Notes", "")).lower().strip()
            active_val = str(row.get("Active", "yes")).lower().strip()
            is_active = active_val == "yes" and note != "off"

            if note == "off" or pd.isna(row.get("Start_Time")) or pd.isna(row.get("End_Time")):
                start = end = parser.parse(f"{day_to_date[day]} 00:00")
                hours = 0.0
                status = "leave"
                is_active = False
            else:
                start_time = str(row['Start_Time']) if not pd.isna(row['Start_Time']) else "09:00"
                end_time = str(row['End_Time']) if not pd.isna(row['End_Time']) else "17:00"
                start = parser.parse(f"{day_to_date[day]} {start_time}")
                end = parser.parse(f"{day_to_date[day]} {end_time}")
                if end <= start:
                    end += pd.Timedelta(days=1)
                hours = round((end - start).total_seconds() / 3600, 2)
                if hours < 4:
                    status = "leave"
                    is_active = False
                    hours = 0.0
                elif hours < 8:
                    status = "half-day"
                else:
                    status = "full-day"

            shifts.append({
                "id": str(idx),
                "name": f"{row['Employee_Name']} - {row['Role']}",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "hours": hours,
                "active": is_active,
                "custom_class": str(row["Role"]).lower().strip(),
                "email": row.get("Email", "N/A"),
                "department": "no" if not is_active else "yes",
                "notes": row.get("Notes", ""),
                "status": status
            })

        except Exception as e:
            print(f"⚠️ Error on row {idx}: {e}")

    os.makedirs("static", exist_ok=True)
    with open("static/shifts.json", "w") as f:
        json.dump(shifts, f, indent=2)

    print(f"✅ Exported {len(shifts)} shifts to static/shifts.json")

except Exception as e:
    print(f"❌ Error: {e}")
