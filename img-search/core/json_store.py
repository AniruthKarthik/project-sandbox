import json
import os

def save_metadata(metadata, output_path="image_metadata.json"):
    data = []

    # Load existing data
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    # Skip if already processed
    if any(entry["hash"] == metadata["hash"] for entry in data):
        print(f"[Skipped] Already processed: {metadata['filename']}")
        return

    data.append(metadata)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"[Processed] {metadata['filename']}")

def load_existing_hashes(output_path="image_metadata.json"):
    if not os.path.exists(output_path):
        return set()
    with open(output_path, "r") as f:
        try:
            data = json.load(f)
            return set(entry["hash"] for entry in data)
        except json.JSONDecodeError:
            return set()

