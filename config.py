import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === OpenAI / API Configuration ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # can adjust later

# === Data Paths ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

FILES = {
    "REFERENCE_1": os.path.join(DATA_DIR, "_new_ Core National Scope and Sequence.xlsx"),
    "STUDENT_GUIDE": os.path.join(DATA_DIR, "Student Guide Grade 8, Unit 1, Module 2_ “I Am the Greatest” by James Bird.pdf"),
    "SAMPLE_FORMAT": os.path.join(DATA_DIR, "Sample spreadsheet.xlsx"),
}

# === Filtering Constants ===
TARGET_GRADE = "Grade 8"
TARGET_UNIT = "Unit 1"
TARGET_MODULE = "Module 2"

# === Output ===
OUTPUT_FILE = os.path.join(DATA_DIR, "Grade8_Unit1_Module2_Mapped_Standards.xlsx")
