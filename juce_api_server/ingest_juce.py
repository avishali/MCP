import os
import json
import re

# CONFIGURATION: Update this to your actual JUCE modules path
JUCE_MODULES_PATH = os.path.expanduser("~/JUCE/modules")
OUTPUT_FILE = "juce_docs.json"

# Regex to find class definitions and inheritance
# Captures: 1=Class Name, 2=Inheritance content (optional)
CLASS_PATTERN = re.compile(r"class\s+(?:JUCE_API\s+)?([A-Za-z0-9_]+)\s*(?::\s*([^\{]+))?\s*\{")

def get_module_name(filepath):
    # Extracts 'juce_audio_processors' from path
    parts = filepath.split(os.sep)
    for part in parts:
        if part.startswith("juce_"):
            return part
    return "unknown_module"

def scan_juce():
    database = []
    print(f"Scanning {JUCE_MODULES_PATH}...")

    for root, _, files in os.walk(JUCE_MODULES_PATH):
        for file in files:
            if file.endswith(".h"):
                filepath = os.path.join(root, file)
                module_name = get_module_name(filepath)
                
                # Skip internal/private headers if desired
                if "native" in filepath or "detail" in filepath:
                    continue

                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                # Find all classes in this file
                matches = CLASS_PATTERN.findall(content)
                for class_name, inheritance in matches:
                    
                    # Clean up inheritance string
                    inheritance_clean = inheritance.strip().replace("\n", " ") if inheritance else "None"
                    
                    # Extract a rough snippet (first 500 chars of context usually contains comments/enums)
                    # A real parser would be better, but this is fast and effective.
                    idx = content.find(f"class {class_name}")
                    if idx == -1: idx = content.find(f"class JUCE_API {class_name}")
                    snippet = content[idx:idx+1500] if idx != -1 else ""

                    entry = {
                        "class_name": f"juce::{class_name}",
                        "module": module_name,
                        "inheritance": inheritance_clean,
                        "api_signature": snippet
                    }
                    database.append(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(database, f, indent=2)
    
    print(f"Success. Indexed {len(database)} JUCE classes to {OUTPUT_FILE}")

if __name__ == "__main__":
    scan_juce()