import os
import sys
import argparse
import time
from typing import Optional, List

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from rich.align import Align
from rich.text import Text
from rich import box
import questionary
from questionary import Choice, Style

from downloader_engine import (
    MediaDownloader,
    search_media,
    get_media_info,
    format_duration,
    format_size,
    sanitize_filename
)
from config import (
    load_config,
    save_config,
    get_download_dir,
    set_download_dir,
    reset_config,
    DEFAULT_DOWNLOADS_DIR
)

console = Console()

# Custom Questionary styling matching unified Cyan / Monochrome aesthetic
custom_style = Style([
    ('qmark', 'fg:#00ffff bold'),                   # question mark style
    ('question', 'fg:#ffffff bold'),                # question text
    ('answer', 'fg:#00ffff bold'),                  # submitted answer text
    ('pointer', 'fg:#00ffff bold'),                 # pointer used in select
    ('highlighted', 'fg:#000000 bg:#00ffff bold'),   # selected item
    ('selected', 'fg:#00ffff bold'),                # selected items in checkbox
    ('separator', 'fg:#444444'),                    # separator line
    ('instruction', 'fg:#666666 italic'),           # user instructions
    ('text', 'fg:#e0e0e0'),
    ('disabled', 'fg:#444444 italic')
])

BANNER = """[bold cyan]
██╗   ██╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗
██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝
██║   ██║██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝ 
╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗ 
 ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗
  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝[/bold cyan]
      [dim cyan]✦ NEXT-GEN ULTRA MEDIA ENGINE & STREAM GRABBER ✦[/dim cyan]
"""

def print_header():
    console.clear()
    console.print(Align.center(BANNER))
    current_dir = get_download_dir()
    console.print(
        Align.center(
            f"[dim cyan]Storage Target:[/dim cyan] [bold cyan]{current_dir}[/bold cyan]\n"
            "[dim]Protocol Compatibility: YouTube • TikTok • Twitter/X • Facebook • Instagram • SoundCloud • Direct Streams[/dim]\n"
        )
    )

def show_media_card(info: dict):
    """Render a rich preview card for media information."""
    table = Table(box=box.ROUNDED, show_header=False, expand=True, border_style="cyan")
    table.add_column("Property", style="bold cyan", width=16)
    table.add_column("Value", style="bold white")

    table.add_row("● Title", info.get("title", "N/A"))
    table.add_row("● Creator / Author", info.get("uploader", "N/A"))
    table.add_row("● Stream Duration", info.get("duration_str", "N/A"))
    if info.get("view_count"):
        table.add_row("● Total Views", f"{info.get('view_count'):,}")
    table.add_row("● Direct Source", info.get("webpage_url", "N/A"))

    console.print(Panel(table, title="[bold cyan]◈ MEDIA STREAM METADATA ◈[/bold cyan]", border_style="cyan"))

def download_with_progress(downloader: MediaDownloader, target: str, media_type: str, quality: str) -> Optional[dict]:
    """Execute download displaying a modern animated rich progress bar."""
    
    with Progress(
        SpinnerColumn("dots", style="bold cyan"),
        TextColumn("[bold cyan]{task.fields[status]}[/bold cyan]"),
        BarColumn(bar_width=35, style="dim cyan", complete_style="bold cyan"),
        TextColumn("[bold cyan]{task.percentage:>3.1f}%[/bold cyan]"),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    ) as progress:
        
        task_id = progress.add_task(
            "download",
            total=100,
            status="Establishing Secure Stream Connection...",
            start=False
        )

        def on_progress(stats: dict):
            status = stats.get("status")
            if status == "downloading":
                total = stats.get("total", 0)
                downloaded = stats.get("downloaded", 0)
                percent = stats.get("percent", 0.0)
                speed_str = stats.get("speed_str", "N/A")
                eta_str = stats.get("eta_str", "N/A")

                progress.update(
                    task_id,
                    total=total if total > 0 else 100,
                    completed=downloaded if total > 0 else percent,
                    status=f"Transmitting Data [{speed_str} | ETA: {eta_str}]"
                )
            elif status == "finished":
                progress.update(
                    task_id,
                    completed=stats.get("total", 100),
                    status="Muxing & Encoding Stream Data..."
                )

        try:
            result = downloader.download(
                url_or_query=target,
                media_type=media_type,
                quality=quality,
                progress_callback=on_progress
            )
            return result
        except Exception as e:
            console.print(f"\n[bold red]✖ Transmission Error:[/bold red] {e}")
            return None

def show_success_summary(result: dict):
    """Show attractive completion summary card."""
    summary_table = Table(box=box.ROUNDED, border_style="cyan", show_header=False, expand=True)
    summary_table.add_column("Key", style="bold cyan", width=18)
    summary_table.add_column("Val", style="bold white")

    summary_table.add_row("✔ Execution Status", "[bold cyan]Process Complete — Asset Saved[/bold cyan]")
    summary_table.add_row("● Target Filename", result.get("filename", "N/A"))
    summary_table.add_row("● Encoded File Size", result.get("filesize_str", "N/A"))
    summary_table.add_row("● Format Standard", f"{result.get('type', '').upper()} ({result.get('quality', '')})")
    summary_table.add_row("● Resolution / Bitrate", result.get("resolution", "N/A"))
    summary_table.add_row("● Asset Duration", result.get("duration_str", "N/A"))
    summary_table.add_row("● Storage Path", f"[dim underline]{result.get('filepath', '')}[/dim underline]")

    console.print()
    console.print(Panel(summary_table, title="[bold cyan]◈ TRANSMISSION SUCCESSFUL ◈[/bold cyan]", border_style="cyan"))

def settings_menu():
    """Interactive Settings and Customization menu."""
    while True:
        cfg = load_config()
        current_dir = cfg.get("download_dir", DEFAULT_DOWNLOADS_DIR)
        
        console.clear()
        console.print(Align.center(BANNER))
        
        table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
        table.add_column("Setting", style="bold cyan")
        table.add_column("Value", style="bold white")
        table.add_row("● Storage Directory", current_dir)
        table.add_row("● Default Video Preset", cfg.get("default_video_quality", "high").upper())
        table.add_row("● Default Audio Preset", cfg.get("default_audio_quality", "high").upper())
        console.print(Panel(table, title="[bold cyan]◈ SYSTEM CONFIGURATION & PREFERENCES ◈[/bold cyan]", border_style="cyan"))

        choice = questionary.select(
            "› Select Preference to Configure:",
            choices=[
                Choice("◈ Modify Storage Target Directory", value="change_dir"),
                Choice("◈ Set Default Video Quality Profile", value="change_v_quality"),
                Choice("◈ Set Default Audio Bitrate Profile", value="change_a_quality"),
                Choice("◈ Restore Default Factory Configurations", value="reset"),
                Choice("‹ Return to Main Menu", value="back"),
            ],
            style=custom_style
        ).ask()

        if not choice or choice == "back":
            break

        if choice == "change_dir":
            desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
            win_downloads_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
            
            dir_choice = questionary.select(
                "› Select Destination Standard:",
                choices=[
                    Choice(f"◈ Project Storage: {DEFAULT_DOWNLOADS_DIR}", value=DEFAULT_DOWNLOADS_DIR),
                    Choice(f"◈ Desktop: {desktop_dir}", value=desktop_dir),
                    Choice(f"◈ User Downloads: {win_downloads_dir}", value=win_downloads_dir),
                    Choice("◈ Specify Custom Absolute/Relative Path...", value="custom"),
                    Choice("‹ Cancel", value="cancel"),
                ],
                style=custom_style
            ).ask()

            if dir_choice and dir_choice != "cancel":
                if dir_choice == "custom":
                    custom_path = questionary.text(
                        "› Enter Target Folder Path:",
                        validate=lambda val: True if len(val.strip()) > 0 else "Path cannot be empty",
                        style=custom_style
                    ).ask()
                    if custom_path:
                        set_download_dir(custom_path)
                        console.print(f"[bold cyan]✔ Storage destination registered:[/bold cyan] {get_download_dir()}")
                        time.sleep(1.2)
                else:
                    set_download_dir(dir_choice)
                    console.print(f"[bold cyan]✔ Storage destination registered:[/bold cyan] {get_download_dir()}")
                    time.sleep(1.2)

        elif choice == "change_v_quality":
            vq = questionary.select(
                "› Choose Default Video Quality Profile:",
                choices=[
                    Choice("◆ Maximum Fidelity [4K / 1080p 60fps]", value="high"),
                    Choice("◇ Balanced Resolution [720p / 480p]", value="medium"),
                    Choice("○ Storage-Optimized [360p / 240p]", value="low"),
                ],
                style=custom_style
            ).ask()
            if vq:
                cfg["default_video_quality"] = vq
                save_config(cfg)
                console.print(f"[bold cyan]✔ Default video profile updated to:[/bold cyan] {vq.upper()}")
                time.sleep(1.2)

        elif choice == "change_a_quality":
            aq = questionary.select(
                "› Choose Default Audio Bitrate Profile:",
                choices=[
                    Choice("◆ Studio Master [320 kbps MP3]", value="high"),
                    Choice("◇ Standard Fidelity [192 kbps MP3]", value="medium"),
                    Choice("○ Bandwidth Saver [128 kbps MP3]", value="low"),
                ],
                style=custom_style
            ).ask()
            if aq:
                cfg["default_audio_quality"] = aq
                save_config(cfg)
                console.print(f"[bold cyan]✔ Default audio profile updated to:[/bold cyan] {aq.upper()}")
                time.sleep(1.2)

        elif choice == "reset":
            if questionary.confirm("› Confirm reset of all preferences to default values?", style=custom_style).ask():
                reset_config()
                console.print("[bold cyan]✔ System configurations restored to defaults.[/bold cyan]")
                time.sleep(1.2)

def interactive_mode():
    while True:
        current_save_dir = get_download_dir()
        downloader = MediaDownloader(output_dir=current_save_dir)
        print_header()
        
        main_choice = questionary.select(
            "› Select Operational Mode:",
            choices=[
                Choice("[ 01 ] ◈ Direct URL Stream Ingestion", value="url"),
                Choice("[ 02 ] ◈ Search Engine & Metadata Query", value="search"),
                Choice("[ 03 ] ◈ Multi-Stream Batch Pipeline", value="batch"),
                Choice("[ 04 ] ◈ Browse Local Storage Directory", value="open_folder"),
                Choice("[ 05 ] ◈ System Preferences & Settings", value="settings"),
                Choice("[ 00 ] ◈ Exit", value="exit"),
            ],
            style=custom_style
        ).ask()

        if not main_choice or main_choice == "exit":
            console.print("\n[bold cyan]✦ Session Terminated. Thank you for using VORTEX Media Engine. ✦[/bold cyan]\n")
            break

        if main_choice == "settings":
            settings_menu()
            continue

        if main_choice == "open_folder":
            target_folder = get_download_dir()
            os.makedirs(target_folder, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(target_folder)
            time.sleep(0.8)
            continue

        target_url = None

        if main_choice == "url":
            target_url = questionary.text(
                "› Enter Target Media URL:",
                validate=lambda val: True if len(val.strip()) > 0 else "Please provide a valid stream link",
                style=custom_style
            ).ask()

            if not target_url:
                continue

            with console.status("[bold cyan]Analyzing remote media headers...[/bold cyan]", spinner="dots"):
                try:
                    info = get_media_info(target_url.strip())
                    show_media_card(info)
                except Exception:
                    console.print("[dim cyan]Note: Direct stream extraction will proceed during transmission.[/dim cyan]")

        elif main_choice == "search":
            query = questionary.text(
                "› Enter Search Query Keywords:",
                validate=lambda val: True if len(val.strip()) > 0 else "Query cannot be blank",
                style=custom_style
            ).ask()

            if not query:
                continue

            with console.status(f"[bold cyan]Querying stream repositories for '[white]{query}[/white]'...[/bold cyan]", spinner="dots"):
                try:
                    results = search_media(query, max_results=6)
                except Exception as e:
                    console.print(f"[bold red]Query failure:[/bold red] {e}")
                    time.sleep(1.8)
                    continue

            if not results:
                console.print("[bold red]No candidate streams found matching query.[/bold red]")
                time.sleep(1.8)
                continue

            search_choices = []
            for r in results:
                display_label = f"[{r['duration_str']}] {r['title']}  • {r['uploader']}"
                search_choices.append(Choice(display_label, value=r['url']))
            search_choices.append(Choice("‹ Return to Main Menu", value="back"))

            chosen_result = questionary.select(
                "› Select Candidate Media Stream:",
                choices=search_choices,
                style=custom_style
            ).ask()

            if not chosen_result or chosen_result == "back":
                continue

            target_url = chosen_result

        elif main_choice == "batch":
            batch_choice = questionary.select(
                "› Select Batch Processing Mode:",
                choices=[
                    Choice("◈ Multi-URL Text Injection", value="paste"),
                    Choice("◈ Load Queue from File (.txt)", value="file"),
                    Choice("‹ Return", value="back")
                ],
                style=custom_style
            ).ask()

            if not batch_choice or batch_choice == "back":
                continue

            url_list = []
            if batch_choice == "paste":
                raw_input = questionary.text(
                    "› Paste Target URLs (comma or line separated):",
                    style=custom_style
                ).ask()
                if raw_input:
                    url_list = [u.strip() for u in raw_input.replace("\n", ",").split(",") if u.strip()]
            elif batch_choice == "file":
                filepath = questionary.text(
                    "› Enter File Path (.txt):",
                    default="urls.txt",
                    style=custom_style
                ).ask()
                if filepath and os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        url_list = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                else:
                    console.print(f"[bold red]Source file not found:[/bold red] {filepath}")
                    time.sleep(1.8)
                    continue

            if not url_list:
                console.print("[bold yellow]Queue contains no valid items.[/bold yellow]")
                time.sleep(1.5)
                continue

            # Batch Format & Quality
            format_type = questionary.select(
                "› Select Master Format for Batch Queue:",
                choices=[
                    Choice("▶ Video Stream (MP4)", value="video"),
                    Choice("♬ Audio Stream (MP3)", value="audio"),
                ],
                style=custom_style
            ).ask()

            if not format_type:
                continue

            quality = questionary.select(
                "› Select Transmission Quality Profile:",
                choices=[
                    Choice("◆ High Profile (4K / 1080p / 320k)", value="high"),
                    Choice("◇ Balanced Profile (720p / 192k)", value="medium"),
                    Choice("○ Compressed Profile (360p / 128k)", value="low"),
                ],
                style=custom_style
            ).ask()

            console.print(f"\n[bold cyan]Initiating Batch Pipeline ({len(url_list)} entries)...[/bold cyan]\n")
            success_count = 0
            for idx, item_url in enumerate(url_list, 1):
                console.print(f"\n[bold cyan]─── Processing Entry [{idx}/{len(url_list)}]: {item_url} ───[/bold cyan]")
                res = download_with_progress(downloader, item_url, format_type, quality)
                if res:
                    show_success_summary(res)
                    success_count += 1

            console.print(f"\n[bold cyan]✔ Batch Pipeline Completed: {success_count}/{len(url_list)} assets processed successfully.[/bold cyan]")
            questionary.press_any_key_to_continue().ask()
            continue

        # Format Selection for single download
        format_choice = questionary.select(
            "› Select Target Encoding Standard:",
            choices=[
                Choice("▶ Video Stream (MP4) — Full High Definition Video & Audio", value="video"),
                Choice("♬ Audio Stream (MP3) — Pure Audio Extraction with ID3 Metadata", value="audio"),
            ],
            style=custom_style
        ).ask()

        if not format_choice:
            continue

        # Quality Selection
        if format_choice == "video":
            quality_choice = questionary.select(
                "› Select Video Resolution Profile:",
                choices=[
                    Choice("◆ Ultra / High Fidelity (4K / 1080p 60fps — Maximum Definition)", value="high"),
                    Choice("◇ Balanced Resolution (720p / 480p — Optimal Speed & Size)", value="medium"),
                    Choice("○ Bandwidth Optimized (360p / 240p — Compact Footprint)", value="low"),
                ],
                style=custom_style
            ).ask()
        else:
            quality_choice = questionary.select(
                "› Select Audio Bitrate Quality Profile:",
                choices=[
                    Choice("◆ Studio Master (320 kbps MP3 — Pure Sound Quality)", value="high"),
                    Choice("◇ Standard Fidelity (192 kbps MP3 — High Quality Audio)", value="medium"),
                    Choice("○ Compact Encoding (128 kbps MP3 — Rapid Transmission)", value="low"),
                ],
                style=custom_style
            ).ask()

        if not quality_choice:
            continue

        console.print(f"\n[bold cyan]Initiating stream extraction to [white]{current_save_dir}[/white]...[/bold cyan]\n")
        result = download_with_progress(downloader, target_url, format_choice, quality_choice)

        if result:
            show_success_summary(result)
            
            # Post Action
            next_action = questionary.select(
                "› Operational Follow-Up:",
                choices=[
                    Choice("◈ Process Another Media Stream", value="again"),
                    Choice("◈ Reveal Asset in File Explorer", value="open"),
                    Choice("◈ Exit", value="exit"),
                ],
                style=custom_style
            ).ask()

            if next_action == "open":
                if sys.platform == "win32" and os.path.exists(result.get("filepath", "")):
                    os.system(f'explorer /select,"{result["filepath"]}"')
                elif sys.platform == "win32":
                    os.startfile(get_download_dir())
            elif next_action == "exit":
                console.print("\n[bold cyan]✦ Session Terminated. Thank you for using VORTEX. ✦[/bold cyan]\n")
                break

def main():
    parser = argparse.ArgumentParser(
        description="VORTEX Media Engine - High-speed search and downloader for video and audio."
    )
    parser.add_argument("target", nargs="?", help="URL or search query to download directly.")
    parser.add_argument("-s", "--search", help="Search keywords and download top result directly.")
    parser.add_argument("-t", "--type", choices=["video", "audio"], default="video", help="Media format (video or audio).")
    parser.add_argument("-q", "--quality", choices=["high", "medium", "low"], default="high", help="Quality level (high, medium, low).")
    parser.add_argument("-o", "--output", default=None, help="Output directory folder (defaults to configured settings).")
    parser.add_argument("-b", "--batch", help="Path to text file containing URLs for batch download.")

    args = parser.parse_args()

    # If no arguments given, launch the interactive VORTEX experience
    if not args.target and not args.search and not args.batch:
        interactive_mode()
        return

    output_directory = args.output if args.output else get_download_dir()
    downloader = MediaDownloader(output_dir=output_directory)
    
    # Batch file mode
    if args.batch:
        if not os.path.exists(args.batch):
            console.print(f"[bold red]Batch file not found:[/bold red] {args.batch}")
            sys.exit(1)
        with open(args.batch, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        console.print(f"[bold cyan]Processing {len(urls)} items from {args.batch}...[/bold cyan]")
        for u in urls:
            res = download_with_progress(downloader, u, args.type, args.quality)
            if res:
                show_success_summary(res)
        return

    # Direct target or search query
    target = args.search if args.search else args.target
    console.print(f"[bold cyan]Downloading:[/bold cyan] {target} | [bold cyan]Type:[/bold cyan] {args.type} | [bold cyan]Quality:[/bold cyan] {args.quality} | [bold cyan]Output:[/bold cyan] {output_directory}")
    res = download_with_progress(downloader, target, args.type, args.quality)
    if res:
        show_success_summary(res)

if __name__ == "__main__":
    main()
