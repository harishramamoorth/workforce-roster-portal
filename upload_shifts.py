import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

# Configuration
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
CREDS_FILE = "credentials.json"
EXCEL_FILE = sys.argv[1] if len(sys.argv) > 1 else "Roster New.xlsx"
SPREADSHEET_NAME = "Shift Schedule"
WORKSHEET_NAME = "Schedule"

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)

    df = pd.read_excel(EXCEL_FILE)
    print(f"✅ Excel file loaded: {EXCEL_FILE}")

    if "Active" in df.columns:
        df = df[df["Active"].str.lower() == "yes"]

    required = ["Day_of_Week", "Employee_Name", "Start_Time", "End_Time", "Role"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise Exception(f"❌ Missing required columns: {missing}")

    df = df[required]

    sheet = client.open(SPREADSHEET_NAME)
    worksheet = sheet.worksheet(WORKSHEET_NAME)
    worksheet.clear()
    worksheet.update([df.columns.tolist()] + df.values.tolist())
    print("✅ Uploaded to Google Sheets successfully.")

except Exception as e:
    print("❌ Upload failed:", e)
