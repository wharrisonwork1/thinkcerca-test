import subprocess, os
from thinkcerca_tool.config import OUTPUT_FILE, DATA_DIR

def run_indesign_server():
    jsx_path = os.path.join(DATA_DIR, "../jsx/insert_standards.jsx")
    indesign_path = "/Applications/Adobe InDesign Server 2024/InDesignServer"

    if not os.path.exists(jsx_path):
        raise FileNotFoundError("ExtendScript not found at: " + jsx_path)

    print("🚀 Running InDesign Server automation...")
    cmd = [indesign_path, "-run", jsx_path]
    subprocess.run(cmd, check=True)
    print("✅ InDesign automation complete.")

if __name__ == "__main__":
    run_indesign_server()
