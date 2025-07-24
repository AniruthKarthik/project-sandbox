from ultralytics import YOLO
import cv2
import mediapipe as mp

# Load pretrained YOLOv8 model (first time, it downloads the weights)
model = YOLO("yolov8n.pt")

def detect_objects(filepath):
    results = model(filepath)
    labels = results[0].names
    objs = [labels[int(cls)] for cls in results[0].boxes.cls]
    return list(set(objs))  # Unique objects

def classify_image_type(filepath):
    mp_pose = mp.solutions.pose
    mp_face = mp.solutions.face_detection

    image = cv2.imread(filepath)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    num_faces = 0
    with mp_face.FaceDetection(model_selection=1) as face_detection:
        face_result = face_detection.process(image_rgb)
        if face_result.detections:
            num_faces = len(face_result.detections)

    if num_faces == 1:
        return "selfie"
    elif 2 <= num_faces <= 5:
        return "group_photo"
    elif num_faces > 5:
        return "crowd"
    else:
        return "unknown"

