import cv2
import os
import numpy as np
import pickle

dataset_path = "dataset"

faces = []
labels = []
label_map = {}
current_label = 0

print("Reading dataset...")

for person_name in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person_name)
    if not os.path.isdir(person_path):
        continue

    print(f"Processing folder: {person_name}")
    label_map[current_label] = person_name

    for image_name in os.listdir(person_path):
        img_path = os.path.join(person_path, image_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        faces.append(img)
        labels.append(current_label)

    current_label += 1

print(f"Total faces found: {len(faces)}")

if len(faces) == 0:
    print("❌ No face images found. Training aborted.")
    exit()

faces = np.array(faces)
labels = np.array(labels)

model = cv2.face.LBPHFaceRecognizer_create()
model.train(faces, labels)

model.save("lbph_model.yml")

with open("labels.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("✅ Model trained and files saved")