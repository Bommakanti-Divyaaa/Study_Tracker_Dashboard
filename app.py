from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_session(subject, time, session_date):
    data = load_data()

    session = {
        "subject": subject,
        "time": time,
        "date": session_date
    }

    data.append(session)
    save_data(data)


def get_day_data(selected_date):
    data = load_data()
    return [entry for entry in data if entry["date"] == selected_date]


def calc_totals(day_data):
    totals = {}

    for entry in day_data:
        subject = entry["subject"]
        totals[subject] = totals.get(subject, 0) + entry["time"]

    return totals


def get_most_studied(totals):
    return max(totals, key=totals.get) if totals else None


def get_week_progress():
    data = load_data()

    today = datetime.today().date()
    week_dates = []
    week_hours = []

    for i in range(6, -1, -1):
        current_day = today - timedelta(days=i)
        current_day_str = str(current_day)

        total = 0
        for entry in data:
            if entry["date"] == current_day_str:
                total += entry["time"]

        week_dates.append(current_day_str)
        week_hours.append(total)

    return week_dates, week_hours


@app.route("/", methods=["GET", "POST"])
def index():
    selected_date = request.args.get("date", str(datetime.today().date()))

    if request.method == "POST":
        subject = request.form["subject"]
        time = float(request.form["time"])
        session_date = request.form["session_date"]

        add_session(subject, time, session_date)

        return redirect(url_for("index", date=session_date))

    day_data = get_day_data(selected_date)
    totals = calc_totals(day_data)
    most = get_most_studied(totals)

    week_dates, week_hours = get_week_progress()

    return render_template(
        "index.html",
        totals=totals,
        most=most,
        selected_date=selected_date,
        week_dates=week_dates,
        week_hours=week_hours
    )


@app.route("/reset", methods=["POST"])
def reset():
    save_data([])
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)