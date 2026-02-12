import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
MODULES_DIR = BASE_DIR / "src" / "modules"

RULES_FILE = DATA_DIR / "rules.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = LOGS_DIR / "compliance_agent.log"

COMPLIANCE_LEVELS = {
    "critical": {"score": 100, "action": "立即下架整改"},
    "high": {"score": 75, "action": "限期修改"},
    "medium": {"score": 50, "action": "建议优化"},
    "low": {"score": 25, "action": "通过审核"}
}

NLP_CONFIG = {
    "model_type": "local",
    "model_name": "bert-base-chinese",
    "use_gpu": False,
    "max_length": 512
}

WHISPER_CONFIG = {
    "model_size": "base",
    "language": "zh",
    "task": "transcribe"
}

REPORT_CONFIG = {
    "output_format": "json",
    "include_details": True,
    "include_suggestions": True,
    "save_to_file": True
}

DATABASE_CONFIG = {
    "type": "sqlite",
    "path": DATA_DIR / "compliance.db"
}

AI_CONFIG = {
    "provider": "local",
    "model": "bert-base-chinese",
    "temperature": 0.7,
    "max_tokens": 1000,
    "timeout": 30
}
