import os

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------

# Absolute path to the directory you want to dump
ROOT_DIR = r"C:\Users\rdjon\task-management-api"

# Output file
OUTPUT_FILE = os.path.join(ROOT_DIR, "all_code_dump.txt")

# Directory names to skip entirely
EXCLUDE_DIRS = {
    "__pycache__",
    ".pytest_cache",
    "venv",
    "coverage_reports",
    "node_modules",    # Added to exclude node_modules
    "build",           # Added to exclude build directory
    "dist",            # Added to exclude dist directory
    ".git",            # Added to exclude .git
    ".idea",           # Added to exclude .idea
}

# File extensions to dump (only text–based). Added frontend file extensions.
INCLUDE_EXTS = {
    # Backend
    ".py", ".txt", ".md", ".cfg", ".ini", ".yml", ".yaml", ".json",
    ".env",
    # Frontend
    ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss", ".sass",
    ".vue", ".svelte", ".less"
}

# -------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------

def is_binary_file(filepath):
    """
    Heuristic check for binary files: looks for null bytes
    in the first 1 KB. If any are found, treat as binary.
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
        return b'\0' in chunk
    except Exception:
        # if we can't even read it in binary mode, skip it
        return True

def should_include_file(filepath):
    """
    Decide whether to include this file.
    - Must have one of the allowed extensions.
    - Must not look binary.
    """
    _, ext = os.path.splitext(filepath)
    if ext.lower() not in INCLUDE_EXTS:
        return False
    return not is_binary_file(filepath)

def dump_code(root_dir, output_filepath):
    """
    Walk root_dir, skip any directories in EXCLUDE_DIRS,
    and append each file's contents (with headers) to output_filepath.
    """
    with open(output_filepath, 'w', encoding='utf-8') as out:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # remove excluded directories in-place so os.walk will skip them
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                if not should_include_file(fpath):
                    continue

                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        out.write(f"### File: {fpath}\n")
                        out.write(f.read())
                        out.write("\n\n")
                except Exception as e:
                    print(f"⚠️ Could not read {fpath!r}: {e}")

if __name__ == "__main__":
    dump_code(ROOT_DIR, OUTPUT_FILE)
    print(f"✅ All code dumped to {OUTPUT_FILE!r}")