import csv

FILE = "attendance/attendance.csv"

with open(FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Student", "Subject", "DetectedBy", "Date", "Time", "Status"])

print("✅ Attendance reset successfully")
