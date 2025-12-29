# 🎓 Facial Recognition Attendance Tracking System

## 📌 Overview
The Facial Recognition Attendance Tracking System is a Python-based application that automates attendance marking using real-time face recognition. The system uses OpenCV and the LBPH (Local Binary Patterns Histogram) algorithm to identify authorized individuals, prevent proxy attendance, and record attendance with timestamps.

This project is designed as a local web-based application using Flask, enabling real-time camera access and seamless user interaction through a browser interface.

---

## ✨ Key Features
- Real-time face detection and recognition
- Attendance marking with date and time
- Proxy attendance prevention (single-face validation)
- Local web interface using Flask
- CSV-based attendance storage
- Modular and easy-to-extend code structure

---

## 🛠️ Tech Stack
- Programming Language: Python
- Computer Vision: OpenCV (LBPH Face Recognizer)
- Web Framework: Flask
- Data Storage: CSV
- Face Detection: Haar Cascade Classifier

---

## 📂 Project Structure
attendance-tracking-system/
│
├── app.py
├── capture_faces.py
├── train_model.py
├── recognize_attendance.py
├── reset_attendance.py
├── labels.pkl
├── status.txt
├── attendance/
│ └── attendance.csv
├── templates/
│ └── index.html
└── README.md


---

## ▶️ How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/attendance-tracking-system.git
cd attendance-tracking-system

2️⃣ Install Dependencies
pip install opencv-python opencv-contrib-python flask numpy

3️⃣ Capture Face Data
python capture_faces.py

4️⃣ Train the Model
python train_model.py


⚠️ The trained model (lbph_model.yml) is generated locally and is not included in the repository due to GitHub file size limitations.

5️⃣ Run the Web Application
python app.py


Open your browser and navigate to:
http://127.0.0.1:5000

🔒 Proxy Attendance Prevention

The system ensures integrity by allowing attendance only when exactly one face is detected. Frames with multiple or no faces are ignored to prevent proxy attendance.

🚫 Model & Dataset Notice

Trained model files and face datasets are intentionally excluded from the repository to comply with GitHub file size limits and maintain repository cleanliness.

To reproduce results:

Capture face data locally

Train the model using the provided script

Run the recognition module
