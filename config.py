import os
import json
from typing import Dict, Any

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOWNLOADS_DIR = os.path.join(PROJECT_DIR, "downloads")
CONFIG_FILE = os.path.join(PROJECT_DIR, "config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "download_dir": DEFAULT_DOWNLOADS_DIR,
    "default_type": "video",
    "default_video_quality": "high",
    "default_audio_quality": "high",
}

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or create default if not existing."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save config: {e}")

def get_download_dir() -> str:
    """Get the currently configured downloads directory."""
    config = load_config()
    target_dir = config.get("download_dir", DEFAULT_DOWNLOADS_DIR)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def set_download_dir(path: str) -> str:
    """Update and persist new download directory."""
    abs_path = os.path.abspath(path.strip().strip('"').strip("'"))
    os.makedirs(abs_path, exist_ok=True)
    config = load_config()
    config["download_dir"] = abs_path
    save_config(config)
    return abs_path

def reset_config() -> Dict[str, Any]:
    """Reset configuration to default values."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()
