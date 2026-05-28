import json
import os
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MCP_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = MCP_ROOT / "config" / "local_paths.json"
OUTPUT_FILE = SCRIPT_DIR / "juce_docs.json"

# Regex to find class definitions and inheritance
# Captures: 1=Class Name, 2=Inheritance content (optional)
CLASS_PATTERN = re.compile(
    r"^\s*class\s+(?:JUCE_API\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*([^\{]+))?\s*\{",
    re.MULTILINE,
)


def resolve_juce_modules_path():
    env_path = os.getenv("JUCE_MODULES_DIR") or os.getenv("JUCE_MODULES_PATH")
    if env_path:
        return Path(env_path).expanduser()

    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)

        configured_path = config.get("juce_modules_dir")
        if configured_path:
            return Path(configured_path).expanduser()

    return Path("~/JUCE/modules").expanduser()


def get_module_name(filepath):
    # Extracts 'juce_audio_processors' from path
    parts = Path(filepath).parts
    for part in parts:
        if part.startswith("juce_"):
            return part
    return "unknown_module"


def scan_juce():
    juce_modules_path = resolve_juce_modules_path()
    if not juce_modules_path.exists():
        raise SystemExit(f"JUCE modules path not found: {juce_modules_path}")

    database = []
    print(f"Scanning {juce_modules_path}...")

    for root, _, files in os.walk(juce_modules_path):
        for file in files:
            if file.endswith(".h"):
                filepath = Path(root) / file
                module_name = get_module_name(filepath)

                # Skip internal/private headers if desired
                if "native" in filepath.parts or "detail" in filepath.parts:
                    continue

                with filepath.open("r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Find all classes in this file
                matches = CLASS_PATTERN.finditer(content)
                for match in matches:
                    class_name, inheritance = match.groups()

                    # Clean up inheritance string
                    inheritance_clean = inheritance.strip().replace("\n", " ") if inheritance else "None"

                    # Extract a rough snippet (first 500 chars of context usually contains comments/enums)
                    # A real parser would be better, but this is fast and effective.
                    snippet = content[match.start():match.start() + 2500]

                    entry = {
                        "class_name": f"juce::{class_name}",
                        "module": module_name,
                        "file_path": str(filepath),
                        "inheritance": inheritance_clean,
                        "api_signature": snippet,
                    }
                    database.append(entry)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(database, f, indent=2)

    print(f"Success. Indexed {len(database)} JUCE classes to {OUTPUT_FILE}")


if __name__ == "__main__":
    scan_juce()
