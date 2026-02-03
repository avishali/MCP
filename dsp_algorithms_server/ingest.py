import os
import json

# CONFIGURATION: Updated to your specific path
# We assume your shared library 'melechdsp-hq' is inside GitHubRepo
SOURCE_DIR = "/Users/avishaylidani/DEV/GitHubRepo/MelechDSP/melechdsp-hq"
OUTPUT_FILE = "dsp_index.json"

def detect_domain(content):
    if "FFT" in content or "Spectral" in content:
        return "FrequencyDomain"
    if "processBlock" in content:
        return "TimeDomain"
    return "ControlRate"

def scan_files():
    database = []
    
    if not os.path.exists(SOURCE_DIR):
        print(f"ERROR: Path not found: {SOURCE_DIR}")
        print("Check if 'melechdsp-hq' folder exists inside GitHubRepo.")
        return

    print(f"Scanning {SOURCE_DIR}...")
    
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith((".h", ".cpp", ".hpp")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    entry = {
                        "algorithm_name": file.split(".")[0],
                        "processing_domain": detect_domain(content),
                        "latency_samples": 0,
                        "simd_optimized": "__m128" in content or "vDSP" in content,
                        "code_snippet": content[:2000]
                    }
                    database.append(entry)
                except Exception as e:
                    print(f"Skipping {file}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(database, f, indent=2)
    
    print(f"Indexed {len(database)} DSP files to {OUTPUT_FILE}")

if __name__ == "__main__":
    scan_files()