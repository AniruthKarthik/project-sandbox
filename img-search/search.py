import os
import json
import cv2
from core.hash_util import compute_image_hash
from core.vision import detect_objects, classify_image_type
from core.json_store import save_metadata, load_existing_hashes

IMAGE_FOLDER = "input_photos"
OUTPUT_JSON = "image_metadata.json"

def load_metadata(output_path=OUTPUT_JSON):
    if not os.path.exists(output_path):
        return []
    with open(output_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def open_image(filepath):
    image = cv2.imread(filepath)
    if image is not None:
        cv2.imshow("Match Found", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"[Error] Could not open: {filepath}")

def main():
    # Step 1: Get search input
    query_object = input("Enter object to search (e.g., 'car', 'ice cream'): ").strip().lower()

    # Step 2: Load known hashes
    existing_hashes = load_existing_hashes()

    # Step 3: Process unprocessed photos
    for filename in os.listdir(IMAGE_FOLDER):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        filepath = os.path.join(IMAGE_FOLDER, filename)
        img_hash = compute_image_hash(filepath)

        if img_hash in existing_hashes:
            continue  # Already processed

        print(f"[Processing] {filename}")
        objects = detect_objects(filepath)
        category = classify_image_type(filepath)

        metadata = {
            "filename": filename,
            "hash": img_hash,
            "objects": objects,
            "category": category
        }

        save_metadata(metadata, OUTPUT_JSON)
        existing_hashes.add(img_hash)

    # Step 4: Search in metadata
    metadata = load_metadata()

    found = False
    for entry in metadata:
        if query_object in [obj.lower() for obj in entry["objects"]]:
            found = True
            filepath = os.path.join(IMAGE_FOLDER, entry["filename"])
            print(f"[Found] {entry['filename']}, Category: {entry['category']}")
            open_image(filepath)

    if not found:
        print(f"[Not Found] No image contains object: {query_object}")

if __name__ == "__main__":
    main()

