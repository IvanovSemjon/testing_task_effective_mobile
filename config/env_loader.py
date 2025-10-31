import os
from pathlib import Path
from dotenv import load_dotenv


def detect_environment() -> str:
    """Определяет текущее окружение"""
    env = os.getenv("ENV")
    if env:
        return env.lower()
    if Path("/.dockerenv").exists():
        return "docker"
    if os.getenv("CI") or Path("GITHUB_ACTIONS").exists():
        return "production"
    return "local"


ENV = detect_environment()

env_files = {
    "local": ".env.local",
    "docker": ".env.docker",
    "production": ".env.prod",
}

env_file = env_files.get(ENV, ".env.local")

load_dotenv(dotenv_path=Path(env_file))
print(f"[config] Django environment detected: {ENV} ({env_file})")