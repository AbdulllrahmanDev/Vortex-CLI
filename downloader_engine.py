import os
import re
import sys
import shutil
import urllib.parse
from typing import Callable, Dict, List, Optional, Any
import imageio_ffmpeg
import yt_dlp

# Discover and prepare bundled ffmpeg
def get_ffmpeg_directory() -> Optional[str]:
    try:
        raw_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if raw_exe and os.path.exists(raw_exe):
            bin_dir = os.path.dirname(raw_exe)
            standard_ffmpeg = os.path.join(bin_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
            if not os.path.exists(standard_ffmpeg):
                try:
                    shutil.copyfile(raw_exe, standard_ffmpeg)
                except Exception:
                    pass
            return bin_dir
    except Exception:
        pass
    return None

FFMPEG_DIR = get_ffmpeg_directory()

def sanitize_filename(filename: str) -> str:
    """Sanitize title or filename for Windows filesystem while preserving Arabic and Unicode text."""
    decoded = urllib.parse.unquote(filename).strip()
    clean_name = decoded.split("?")[0].split("#")[0]
    clean_name = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", clean_name)
    clean_name = re.sub(r'\s+', " ", clean_name)
    clean_name = re.sub(r'_+', "_", clean_name).strip(" ._")
    return clean_name if clean_name else "media_download"

def format_duration(seconds: Optional[float]) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    if not seconds:
        return "N/A"
    seconds = int(seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def format_size(bytes_val: Optional[float]) -> str:
    """Format bytes into human-readable string (MB, GB, etc.)."""
    if not bytes_val or bytes_val <= 0:
        return "N/A"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def search_media(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search YouTube for queries and return top results."""
    search_term = f"ytsearch{max_results}:{query}"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }
    if FFMPEG_DIR:
        ydl_opts["ffmpeg_location"] = FFMPEG_DIR

    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_term, download=False)
            if info and "entries" in info:
                for entry in info["entries"]:
                    if not entry:
                        continue
                    results.append({
                        "id": entry.get("id"),
                        "title": entry.get("title", "Unknown Title"),
                        "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "duration": entry.get("duration"),
                        "duration_str": format_duration(entry.get("duration")),
                        "uploader": entry.get("uploader") or entry.get("channel", "Unknown Channel"),
                        "view_count": entry.get("view_count", 0),
                    })
        except Exception as e:
            raise RuntimeError(f"Failed to search: {e}")
            
    return results

def get_media_info(url_or_query: str) -> Dict[str, Any]:
    """Extract metadata for a specific media URL."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }
    if FFMPEG_DIR:
        ydl_opts["ffmpeg_location"] = FFMPEG_DIR

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_or_query, download=False)
        if "entries" in info and len(info["entries"]) > 0:
            info = info["entries"][0]
        return {
            "title": info.get("title", "Media"),
            "uploader": info.get("uploader", "Unknown"),
            "duration": info.get("duration"),
            "duration_str": format_duration(info.get("duration")),
            "thumbnail": info.get("thumbnail"),
            "webpage_url": info.get("webpage_url") or url_or_query,
            "ext": info.get("ext", "mp4"),
            "view_count": info.get("view_count", 0),
        }

from config import get_download_dir

class MediaDownloader:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = os.path.abspath(output_dir) if output_dir else get_download_dir()
        os.makedirs(self.output_dir, exist_ok=True)
        self.last_downloaded_file: Optional[str] = None
        self.download_stats: Dict[str, Any] = {}

    def download(
        self,
        url_or_query: str,
        media_type: str = "video",      # "video" or "audio"
        quality: str = "high",          # "high", "medium", "low"
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download media by URL or search query with designated format and quality.
        """
        is_audio = media_type.lower() in ["audio", "mp3", "sound", "صوت"]
        quality_key = quality.lower()
        
        # Configure output template
        outtmpl = os.path.join(
            self.output_dir, 
            custom_filename or "%(title)s [%(id)s].%(ext)s"
        )

        # Build yt-dlp options
        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,
            "restrictfilenames": False,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            }
        }

        # Set FFmpeg location
        if FFMPEG_DIR:
            ydl_opts["ffmpeg_location"] = FFMPEG_DIR

        # Setup Progress Hook
        def ydl_progress_hook(d: Dict[str, Any]):
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                speed = d.get("speed") or 0
                eta = d.get("eta") or 0
                percent = (downloaded / total * 100) if total > 0 else 0
                
                stats = {
                    "status": "downloading",
                    "filename": d.get("filename"),
                    "percent": percent,
                    "downloaded": downloaded,
                    "total": total,
                    "speed": speed,
                    "eta": eta,
                    "eta_str": format_duration(eta),
                    "speed_str": f"{format_size(speed)}/s" if speed else "N/A",
                }
                self.download_stats = stats
                if progress_callback:
                    progress_callback(stats)

            elif d.get("status") == "finished":
                self.last_downloaded_file = d.get("filename")
                stats = {
                    "status": "finished",
                    "filename": d.get("filename"),
                    "total": d.get("total_bytes") or 0,
                }
                self.download_stats = stats
                if progress_callback:
                    progress_callback(stats)

        ydl_opts["progress_hooks"] = [ydl_progress_hook]

        # Configure Quality & Formats
        if is_audio:
            bitrate_map = {
                "high": "320",
                "medium": "192",
                "low": "128",
                "320k": "320",
                "192k": "192",
                "128k": "128",
                "عالية": "320",
                "متوسطة": "192",
                "منخفضة": "128"
            }
            target_bitrate = bitrate_map.get(quality_key, "320")
            
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": target_bitrate,
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    }
                ],
            })
        else:
            # Video Format & Resolution configurations
            if quality_key in ["high", "ultra", "best", "4k", "1080p", "عالية"]:
                ydl_opts["format"] = (
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo+bestaudio/"
                    "best[ext=mp4]/"
                    "best"
                )
            elif quality_key in ["medium", "standard", "720p", "480p", "متوسطة"]:
                ydl_opts["format"] = (
                    "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo[height<=720]+bestaudio/"
                    "best[height<=720]/"
                    "best"
                )
            else:  # low / 360p / saver
                ydl_opts["format"] = (
                    "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo[height<=360]+bestaudio/"
                    "best[height<=360]/"
                    "best"
                )
            
            ydl_opts["merge_output_format"] = "mp4"

        # Resolve search targets vs direct link
        targets = []
        if not url_or_query.startswith("http://") and not url_or_query.startswith("https://"):
            try:
                candidates = search_media(url_or_query, max_results=5)
                if candidates:
                    targets = [c["url"] for c in candidates]
                else:
                    targets = [f"ytsearch1:{url_or_query}"]
            except Exception:
                targets = [f"ytsearch1:{url_or_query}"]
        else:
            targets = [url_or_query]

        last_err = None
        for extract_target in targets:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(extract_target, download=True)
                    if info and "entries" in info and len(info["entries"]) > 0:
                        info = info["entries"][0]
                    if not info:
                        continue
                        
                    final_filepath = ydl.prepare_filename(info)
                    
                    # Locate actual created file (mp3 or mp4)
                    if is_audio:
                        base, _ = os.path.splitext(final_filepath)
                        if os.path.exists(f"{base}.mp3"):
                            final_filepath = f"{base}.mp3"
                    else:
                        base, _ = os.path.splitext(final_filepath)
                        if os.path.exists(f"{base}.mp4"):
                            final_filepath = f"{base}.mp4"

                    file_size = os.path.getsize(final_filepath) if os.path.exists(final_filepath) else 0

                    return {
                        "success": True,
                        "title": info.get("title", "Media"),
                        "filepath": final_filepath,
                        "filename": os.path.basename(final_filepath),
                        "filesize": file_size,
                        "filesize_str": format_size(file_size),
                        "duration": info.get("duration"),
                        "duration_str": format_duration(info.get("duration")),
                        "uploader": info.get("uploader", "Unknown"),
                        "resolution": f"{info.get('width', 'N/A')}x{info.get('height', 'N/A')}" if not is_audio else f"{target_bitrate} kbps",
                        "type": "audio" if is_audio else "video",
                        "quality": quality,
                    }
            except Exception as e:
                last_err = e
                continue

        if last_err:
            raise last_err
        raise RuntimeError("No downloadable media found.")
