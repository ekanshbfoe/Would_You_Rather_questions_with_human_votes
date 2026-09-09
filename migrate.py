#!/usr/bin/env python3
import json
import os
import glob
from pathlib import Path

def normalize_text(text):
    if not text:
        return ""
    return str(text).strip().lower()

def main():
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / "Scraper" / "data"
    prod_dir = base_dir / "data"

    if not raw_dir.exists():
        print(f"Directory not found: {raw_dir}")
        return

    prod_dir.mkdir(exist_ok=True)

    raw_files = list(raw_dir.glob("raw_*.json"))
    if not raw_files:
        print("No raw files found to migrate.")
        return

    for raw_file in raw_files:
        category = raw_file.stem.replace("raw_", "")
        prod_file = prod_dir / f"questions_{category}.json"
        
        # 1. Load raw data
        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error parsing JSON from {raw_file.name}. Skipping.")
            continue

        # 2. Filter raw data (0/0 and empty text)
        filtered_raw = []
        zero_count = 0
        empty_count = 0
        for item in raw_data:
            gb = item.get("global_votes_blue", 0)
            gr = item.get("global_votes_red", 0)
            if gb == 0 and gr == 0:
                zero_count += 1
                continue
            
            q_text = item.get("question", "")
            if not normalize_text(q_text) or not normalize_text(item.get("option_blue", "")) or not normalize_text(item.get("option_red", "")):
                empty_count += 1
                continue
                
            filtered_raw.append(item)

        # 3. Load existing prod data (for deduplication and max ID)
        prod_data = []
        existing_questions = set()
        max_idx = 0
        
        if prod_file.exists():
            try:
                with open(prod_file, "r", encoding="utf-8") as f:
                    prod_data = json.load(f)
                
                for item in prod_data:
                    existing_questions.add(normalize_text(item.get("question", "")))
                    
                    # Extract numeric ID to find max
                    item_id = str(item.get("id", ""))
                    if item_id.startswith(f"{category}_"):
                        try:
                            idx = int(item_id.split("_")[-1])
                            if idx > max_idx:
                                max_idx = idx
                        except ValueError:
                            pass
            except json.JSONDecodeError:
                print(f"Warning: Existing prod file {prod_file.name} is corrupt. Proceeding as empty.")
                prod_data = []

        # 4. Dedup raw data
        new_items = []
        dup_count = 0
        for item in filtered_raw:
            norm_q = normalize_text(item.get("question", ""))
            if norm_q in existing_questions:
                dup_count += 1
            else:
                existing_questions.add(norm_q) # Add to set to catch intra-raw duplicates
                new_items.append(item)

        # 5. Re-index and Merge
        for item in new_items:
            max_idx += 1
            item["id"] = f"{category}_{max_idx:04d}"
            prod_data.append(item)

        # 6. Save and Cleanup
        if new_items or (not prod_file.exists() and prod_data):
            with open(prod_file, "w", encoding="utf-8") as f:
                json.dump(prod_data, f, indent=2, ensure_ascii=False)
        
        try:
            os.remove(raw_file)
        except Exception as e:
            print(f"Warning: Failed to delete {raw_file.name}: {e}")

        # 7. Summary
        print(f"{category.capitalize()}: Merged {len(new_items)} new questions. Filtered {zero_count} zeroes (and {empty_count} empties). Dropped {dup_count} duplicates. New total: {len(prod_data)}.")

if __name__ == "__main__":
    main()
