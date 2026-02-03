import os
import json

# CONFIGURATION: Scan both your plugin and your library
PROJECT_PATHS = [
    "/Users/avishaylidani/DEV/GitHubRepo/AnalyzerPro",
    "/Users/avishaylidani/DEV/GitHubRepo/MelechDSP/melechdsp-hq"
]
OUTPUT_FILE = "project_structure.json"

def detect_role(filename):
    if "Processor" in filename: return "Processor"
    if "Editor" in filename: return "Editor"
    if "CMake" in filename: return "Config"
    return "Service"

def scan_projects():
    database = []
    
    for project_root in PROJECT_PATHS:
        if not os.path.exists(project_root):
            print(f"Skipping missing path: {project_root}")
            continue
            
        project_name = os.path.basename(project_root)
        print(f"Scanning {project_name}...")

        for root, dirs, files in os.walk(project_root):
            # Skip build folders and hidden git folders to save time
            if "build" in root.lower() or ".git" in root:
                continue

            for file in files:
                if file.endswith((".h", ".cpp", ".mm", "CMakeLists.txt")):
                    entry = {
                        "project_name": project_name,
                        "file_role": detect_role(file),
                        "file_path": os.path.join(root, file),
                        "dependencies": []
                    }
                    database.append(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(database, f, indent=2)
    print(f"Mapped {len(database)} project files.")

if __name__ == "__main__":
    scan_projects()