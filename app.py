from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import os
import pandas as pd
import subprocess
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'shifty-secret'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    excel_path = "Roster New.xlsx"
    if os.path.exists("current_excel.txt"):
        with open("current_excel.txt") as f:
            excel_path = f.read().strip()

    if os.path.exists(excel_path):
        try:
            subprocess.run(['python', 'export_shifts.py', excel_path], check=True)
            print(f"✅ Processed {excel_path}")
        except Exception as e:
            print("⚠️ Error processing default file:", e)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_excel():
    try:
        file = request.files.get('file')
        if not file:
            return "❌ No file uploaded."
        if not file.filename.lower().endswith('.xlsx'):
            return "❌ Only .xlsx files allowed."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename.replace(".xlsx", f"_{timestamp}.xlsx"))
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        print(f"✅ Uploaded as: {save_path}")

        with open("current_excel.txt", "w") as f:
            f.write(save_path)

        subprocess.run(['python', 'upload_shifts.py', save_path], check=True)
        subprocess.run(['python', 'export_shifts.py', save_path], check=True)

        return redirect(url_for('index'))

    except Exception as e:
        return f"❌ Upload error: {e}"

@app.route('/shifts')
def shifts():
    try:
        with open("static/shifts.json") as f:
            data = json.load(f)
        response = make_response(jsonify(data))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    except Exception as e:
        print(f"⚠️ Failed to load shifts.json: {e}")
        return jsonify([])

@app.route('/full-roster')
def full_roster():
    excel_path = "Roster New.xlsx"
    if os.path.exists("current_excel.txt"):
        with open("current_excel.txt") as f:
            excel_path = f.read().strip()

    if not os.path.exists(excel_path):
        return "❌ No roster file found. Please upload one."
    df = pd.read_excel(excel_path)
    return render_template("roster.html", table=df.to_html(classes="table table-striped", index=False))

@app.route('/update-shifts')
def update_shifts():
    try:
        excel_path = "Roster New.xlsx"
        if os.path.exists("current_excel.txt"):
            with open("current_excel.txt") as f:
                excel_path = f.read().strip()

        if os.path.exists(excel_path):
            subprocess.run(['python', 'export_shifts.py', excel_path], check=True)
            print("✅ Shift data refreshed successfully")
    except Exception as e:
        print(f"⚠️ Error in update-shifts route: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
