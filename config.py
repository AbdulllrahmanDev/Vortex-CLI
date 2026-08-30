import os
import json
from typing import Dict, Any, List, Tuple

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOWNLOADS_DIR = os.path.join(PROJECT_DIR, "downloads")
CONFIG_FILE = os.path.join(PROJECT_DIR, "config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "download_dir": DEFAULT_DOWNLOADS_DIR,
    "default_type": "video",
    "default_video_quality": "high",
    "default_audio_quality": "high",
}

def is_android() -> bool:
    """Check if the current runtime environment is Android / Termux."""
    return (
        os.path.exists("/storage/emulated/0")
        or os.path.exists("/sdcard")
        or "ANDROID_ROOT" in os.environ
        or "TERMUX_VERSION" in os.environ
    )

import posixpath

def get_android_paths() -> List[Tuple[str, str]]:
    """
    Return standard Android media directories where videos, audios, and media
    are automatically indexed and displayed in Android gallery and player apps.
    """
    termux_storage = os.path.expanduser("~/storage")
    
    if os.path.exists("/storage/emulated/0"):
        base = "/storage/emulated/0"
    elif os.path.exists("/sdcard"):
        base = "/sdcard"
    elif os.path.exists(termux_storage):
        base = termux_storage
    else:
        base = "/storage/emulated/0"

    return [
        ("◈ Android Movies (Auto-indexed by Video Players & Gallery)", posixpath.join(base, "Movies")),
        ("◈ Android Music (Auto-indexed by Music & Audio Players)", posixpath.join(base, "Music")),
        ("◈ Android Download (System Default Shared Downloads)", posixpath.join(base, "Download")),
        ("◈ Android DCIM (Camera & Media Gallery)", posixpath.join(base, "DCIM")),
        ("◈ Android Podcasts (Podcasts & Voice Media)", posixpath.join(base, "Podcasts")),
    ]

def get_suggested_download_dirs() -> List[Tuple[str, str]]:
    """
    Return a comprehensive list of suggested storage paths based on the host OS.
    Includes Android media paths, user standard directories, and project defaults.
    """
    suggestions: List[Tuple[str, str]] = []
    
    # 1. Project local storage
    suggestions.append(("◈ Project Workspace Storage", DEFAULT_DOWNLOADS_DIR))
    
    android_env = is_android()
    android_paths = get_android_paths()
    
    # 2. If running on Android, prioritize Android media paths
    if android_env:
        suggestions.extend(android_paths)
    
    # 3. Standard Desktop / PC folders
    home_dir = os.path.expanduser("~")
    userprofile = os.environ.get("USERPROFILE", home_dir)
    
    desktop_dir = os.path.join(userprofile, "Desktop")
    if os.path.exists(desktop_dir) or not android_env:
        suggestions.append(("◈ Desktop Directory", desktop_dir))
        
    downloads_dir = os.path.join(userprofile, "Downloads")
    if os.path.exists(downloads_dir) or not android_env:
        suggestions.append(("◈ User Downloads Directory", downloads_dir))
        
    videos_dir = os.path.join(userprofile, "Videos")
    if os.path.exists(videos_dir):
        suggestions.append(("◈ Videos Library", videos_dir))
        
    music_dir = os.path.join(userprofile, "Music")
    if os.path.exists(music_dir):
        suggestions.append(("◈ Music Library", music_dir))
        
    # 4. If not on Android, append Android presets as options for multi-device/remote setups
    if not android_env:
        suggestions.extend(android_paths)
        
    return suggestions

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
    expanded = os.path.expanduser(target_dir)
    try:
        os.makedirs(expanded, exist_ok=True)
        return expanded
    except Exception:
        if expanded.startswith(("/storage/", "/sdcard/")):
            return expanded
        os.makedirs(DEFAULT_DOWNLOADS_DIR, exist_ok=True)
        config["download_dir"] = DEFAULT_DOWNLOADS_DIR
        save_config(config)
        return DEFAULT_DOWNLOADS_DIR

def set_download_dir(path: str) -> str:
    """Update and persist new download directory."""
    raw_path = path.strip().strip('"').strip("'")
    try:
        expanded_path = os.path.expanduser(raw_path)
        if not os.path.isabs(expanded_path) and not expanded_path.startswith(("/storage/", "/sdcard/")):
            abs_path = os.path.abspath(expanded_path)
        else:
            abs_path = expanded_path
        os.makedirs(abs_path, exist_ok=True)
    except Exception:
        abs_path = raw_path

    config = load_config()
    config["download_dir"] = abs_path
    save_config(config)
    return abs_path

def reset_config() -> Dict[str, Any]:
    """Reset configuration to default values."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

