import cv2
import json
import numpy as np
import os
import django

# -----------------------------
# Setup Django so we can use ORM here
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yolo_parking_django.settings")
django.setup()
from app.models import DetectionResult
from django.utils import timezone

# -----------------------------
# Configuration
# -----------------------------
VIDEO_PATH = "parking1.mp4"
YOLO_MODEL_PATH = "yolo11s.pt"
JSON_FILE = "bounding_boxes.json"
TARGET_CLASSES = [2]  # car class in COCO
WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 600

# YOLO
from ultralytics import YOLO
model = YOLO(YOLO_MODEL_PATH)

# -----------------------------
# Load polygons
# -----------------------------
with open(JSON_FILE) as f:
    parking_polygons = json.load(f)

# -----------------------------
# Helper
# -----------------------------
def check_occupancy(boxes, polygons):
    occupancy = []
    for poly in polygons:
        pts = np.array(poly["points"], dtype=np.int32).reshape((-1, 1, 2))
        occupied = False
        for box in boxes:
            xc = int((box[0] + box[2]) / 2)
            yc = int((box[1] + box[3]) / 2)
            if cv2.pointPolygonTest(pts, (xc, yc), False) >= 0:
                occupied = True
                break
        occupancy.append(occupied)
    return occupancy

# -----------------------------
# Run video
# -----------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f" Could not open {VIDEO_PATH}")
    exit()

paused = False
last_frame = None

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            print(" Video ended")
            break

        frame_resized = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))

        results = model(frame_resized)[0]

        boxes = []
        for box, cls in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy()):
            if int(cls) in TARGET_CLASSES:
                boxes.append(box)

        occupied_flags = check_occupancy(boxes, parking_polygons)
        occupied_count = sum(occupied_flags)
        available_count = len(occupied_flags) - occupied_count

        # Draw polygons
        for poly, occupied in zip(parking_polygons, occupied_flags):
            pts = np.array(poly["points"], dtype=np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if occupied else (0, 255, 0)
            cv2.polylines(frame_resized, [pts], isClosed=True, color=color, thickness=2)

        # Draw centroids
        for box in boxes:
            xc = int((box[0] + box[2]) / 2)
            yc = int((box[1] + box[3]) / 2)
            cv2.circle(frame_resized, (xc, yc), 5, (255, 0, 189), -1)

        # Overlay text
        cv2.putText(
            frame_resized,
            f"Occupied: {occupied_count} | Available: {available_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
        )

        last_frame = frame_resized.copy()

        # -----------------------------
        # Save result to database
        # -----------------------------
        DetectionResult.objects.create(
            timestamp=timezone.now(),
            occupied=occupied_count,
            available=available_count
        )

    else:
        frame_resized = last_frame

    cv2.imshow("Parking Lot Dashboard", frame_resized)
    key = cv2.waitKey(30) & 0xFF
    if key == ord("q"):
        print("👋 Exiting")
        break
    elif key == 32:  # spacebar
        paused = not paused

cap.release()
cv2.destroyAllWindows()
print(" Done")
