# ✦ VORTEX CLI — Next-Gen Media Engine & Stream Grabber ✦

**VORTEX CLI** is a high-performance, interactive command-line interface engineered for lightning-fast media extraction, smart keyword searching, format transcoding, and batch stream processing across 1000+ online video & audio platforms.

Built with a unified, dark-mode cyberpunk terminal aesthetic, interactive arrow-key menus, real-time download telemetry (`MB/s`, ETA, transfer graphs), and persistent configuration.

---

## ◈ Key Capabilities & Features

- ◈ **Interactive Terminal Dashboard**: Arrow-key driven menus powered by `Rich` and `Questionary` with real-time transfer telemetry and stream previews.
- ◈ **Smart Keyword Search Engine**: Download media without copying links—simply type search terms and select from top matched candidate streams.
- ◈ **Universal Stream Compatibility**: Full extraction support for YouTube, TikTok, Twitter/X, Instagram, Facebook, SoundCloud, Pinterest, Vimeo, and direct MP4/MP3 URLs.
- ◈ **Multi-Tier Quality Profiles**:
  - **▶ Video Stream (MP4)**:
    - `◆ Ultra Profile`: 4K / 1080p 60fps (Highest available definition with embedded audio).
    - `◇ Balanced Profile`: 720p / 480p (Optimized bandwidth & storage balance).
    - `○ Compact Profile`: 360p / 240p (Lightweight & low-footprint).
  - **♬ Audio Stream (MP3)**:
    - `◆ Studio Master`: 320 kbps MP3 with embedded album artwork & ID3 metadata.
    - `◇ Standard Fidelity`: 192 kbps MP3 (CD-quality).
    - `○ Bandwidth Saver`: 128 kbps MP3 (Rapid, compact transfer).
- ◈ **Multi-Stream Batch Pipeline**: Queue multiple URLs via interactive paste or load directly from `.txt` batch files.
- ◈ **Persistent Preferences & Directory Storage**: Seamlessly customize your default storage path (`downloads/`, Desktop, System Downloads, or custom absolute path) with auto-persistence in `config.json`.
- ◈ **Unicode & Arabic Filename Integrity**: Native Unicode preservation ensuring full compatibility without character corruption.

---

## ⚡ Global Installation & Setup Guide

### 1. Prerequisites (All Operating Systems)
Make sure you have **Python 3.8+** and **pip** installed on your system.

Clone or navigate to the project directory:
```bash
git clone https://github.com/your-username/vortex-cli.git
cd "Download all by one"
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

---

### 2. Windows Installation (CMD & PowerShell)

#### Quick 1-Step Setup:
Run the automatic global registration script:
```powershell
python install_global.py
```
This registers `vortex` across your local user `PATH` directories (`%USERPROFILE%\.local\bin`, `%APPDATA%\Roaming\npm`, etc.).

#### Manual Windows PATH Registration (Optional):
1. Open PowerShell and run:
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pwd", "User")
```
2. Or launch directly anytime by double-clicking:
```bat
start_cli.bat
```

Now you can open any **Command Prompt**, **PowerShell**, or **Windows Terminal** window and type:
```powershell
vortex
```

---

### 3. macOS & Linux Installation (Terminal, zsh, bash)

To run `vortex` globally from any terminal window on **macOS (Terminal / iTerm2 / Warp)** or **Linux**:

#### Method A: Create a Global Symbolic Link (Recommended)
Make the runner executable and link it to `/usr/local/bin`:
```bash
# Make CLI executable
chmod +x downloader_cli.py

# Create a global symlink in /usr/local/bin (or ~/.local/bin)
sudo ln -sf "$(pwd)/downloader_cli.py" /usr/local/bin/vortex
```

#### Method B: Add Alias to Shell Configuration (`.zshrc` or `.bashrc`)
1. Open your shell configuration file:
   - For **macOS (zsh - default)**:
     ```bash
     echo "alias vortex='python3 \"$(pwd)/downloader_cli.py\"'" >> ~/.zshrc
     source ~/.zshrc
     ```
   - For **Linux / macOS (bash)**:
     ```bash
     echo "alias vortex='python3 \"$(pwd)/downloader_cli.py\"'" >> ~/.bashrc
     source ~/.bashrc
     ```

Now you can invoke the CLI from any terminal directory:
```bash
vortex
```

---

## ◈ Usage & Command Reference

### 1. Interactive Wizard Mode (Recommended)
Simply type `vortex` without arguments to launch the full interactive interface:
```bash
vortex
```

### 2. Headless CLI Automation Mode
Pass arguments directly for instant automated downloads:

```bash
# Download video in highest quality (4K / 1080p)
vortex "https://www.youtube.com/watch?v=..." --type video --quality high

# Search and download audio in Studio Master MP3 (320 kbps)
vortex -s "lofi hip hop beats" --type audio --quality high

# Download balanced video to a custom output directory
vortex "https://tiktok.com/@user/video/..." --type video --quality medium -o "/path/to/my_folder"

# Batch download all URLs listed in a text file
vortex --batch urls.txt --type video --quality medium
```

### 3. Command-Line Arguments Reference

| Flag | Argument | Description | Default |
| :--- | :--- | :--- | :--- |
| `target` | `[URL or query]` | Direct stream URL or search keyword | None |
| `-s, --search` | `<query>` | Search keywords and download top match | None |
| `-t, --type` | `video` \| `audio` | Media encoding format | `video` |
| `-q, --quality`| `high` \| `medium` \| `low` | Quality resolution/bitrate profile | `high` |
| `-o, --output` | `<directory>` | Output folder destination | Configured default |
| `-b, --batch` | `<file.txt>` | Path to `.txt` list of URLs | None |
| `-h, --help` | | Show help manual & exit | |

---

## 📂 Project Architecture

```
├── downloader_cli.py      # Core interactive CLI interface & rich terminal rendering
├── downloader_engine.py   # High-speed yt-dlp + embedded FFmpeg transcoding engine
├── config.py              # Persistent settings manager (directories, profiles)
├── config.json            # User-saved preferences and storage path
├── install_global.py      # Global PATH registration installer
├── start_cli.bat          # 1-Click Windows execution launcher
├── vortex.cmd             # Windows Command Prompt global runner
├── requirements.txt       # Python dependency specifications
├── README.md              # Documentation & quickstart guide
└── downloads/             # Default destination directory for downloaded media
```

---

## 📄 License
This project is open-source and available under the **MIT License**.
