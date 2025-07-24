import os
from core.hash_util import compute_image_hash
from core.vision import detect_objects, classify_image_type
from core.json_store import save_metadata, load_existing_hashes

IMAGE_FOLDER = "input_photos"
OUTPUT_JSON = "image_metadata.json"

def main():
    # Load existing image hashes to skip duplicates
    existing_hashes = load_existing_hashes(OUTPUT_JSON)

    for filename in os.listdir(IMAGE_FOLDER):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        filepath = os.path.join(IMAGE_FOLDER, filename)
        img_hash = compute_image_hash(filepath)

        if img_hash in existing_hashes:
            print(f"[Skipped] Duplicate image: {filename}")
            continue

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

if __name__ == "__main__":
    main()

