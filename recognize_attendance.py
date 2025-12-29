import cv2
import pickle
import os
from datetime import datetime

STATUS_FILE = "status.txt"
ATTENDANCE_FILE = "attendance/attendance.csv"
PROXY_DIR = "proxy_faces"

os.makedirs(PROXY_DIR, exist_ok=True)

# 🔹 Read inputs from Flask
authorized_student = input().strip()
subject = input().strip()

# 🔹 Load model
model = cv2.face.LBPHFaceRecognizer_create()
model.read("lbph_model.yml")

with open("labels.pkl", "rb") as f:
    label_map = pickle.load(f)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)
print("📷 Camera started...")

detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Allow ONLY one face
    if len(faces) != 1:
        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    (x, y, w, h) = faces[0]
    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, (200, 200))

    label, confidence = model.predict(face)
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # 🔴 UNKNOWN FACE
    if confidence > 75:
        img_name = f"{authorized_student}_unknown_{date}_{time}.jpg"
        cv2.imwrite(os.path.join(PROXY_DIR, img_name), frame)

        with open(ATTENDANCE_FILE, "a") as f:
            f.write(f"{authorized_student},{subject},Unknown,{date},{time},Proxy_Detected\n")

        with open(STATUS_FILE, "w") as s:
            s.write("PROXY")

        detected = True

    else:
        detected_name = label_map[label]

        # 🔴 PROXY (Known student)
        if detected_name != authorized_student:
            img_name = f"{authorized_student}_{detected_name}_{date}_{time}.jpg"
            cv2.imwrite(os.path.join(PROXY_DIR, img_name), frame)

            with open(ATTENDANCE_FILE, "a") as f:
                f.write(f"{authorized_student},{subject},{detected_name},{date},{time},Proxy_Detected\n")

            with open(STATUS_FILE, "w") as s:
                s.write("PROXY")

            detected = True

        # 🟢 AUTHORIZED
        else:
            with open(ATTENDANCE_FILE, "a") as f:
                f.write(f"{authorized_student},{subject},{authorized_student},{date},{time},Present\n")

            with open(STATUS_FILE, "w") as s:
                s.write("PRESENT")

            detected = True

    if detected:
        break

    cv2.imshow("Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
