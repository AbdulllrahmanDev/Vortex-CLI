import os
import sys
import shutil

def install_vortex_globally():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    project_cmd = os.path.join(project_dir, "vortex.cmd")
    cli_py = os.path.join(project_dir, "downloader_cli.py")
    py_exe = sys.executable

    # Content of .cmd / .bat file
    cmd_content = f'@echo off\nchcp 65001 >nul\n"{py_exe}" "{cli_py}" %*\n'
    with open(project_cmd, "w", encoding="utf-8") as f:
        f.write(cmd_content)

    # PowerShell runner (.ps1)
    ps1_content = f'& "{py_exe}" "{cli_py}" $args\n'

    # Shell script for Git Bash / WSL / MSYS
    sh_content = f'#!/bin/sh\nexec "{py_exe}" "{cli_py}" "$@"\n'

    user_profile = os.environ.get("USERPROFILE", "")
    target_dirs = [
        os.path.join(user_profile, "AppData", "Roaming", "npm"),
        os.path.join(user_profile, ".local", "bin"),
        os.path.join(user_profile, "AppData", "Local", "Microsoft", "WindowsApps"),
        os.path.join(user_profile, "AppData", "Local", "Programs", "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Scripts"),
        os.path.join(user_profile, ".gemini", "antigravity-ide", "bin"),
    ]

    # Also inspect current PATH for any user-writable directory
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for p in path_dirs:
        p_clean = p.strip()
        if p_clean and user_profile.lower() in p_clean.lower() and p_clean not in target_dirs:
            target_dirs.append(p_clean)

    installed_locations = []
    for d in target_dirs:
        try:
            if os.path.exists(d):
                cmd_dest = os.path.join(d, "vortex.cmd")
                bat_dest = os.path.join(d, "vortex.bat")
                ps_dest = os.path.join(d, "vortex.ps1")
                sh_dest = os.path.join(d, "vortex")
                
                with open(cmd_dest, "w", encoding="utf-8") as f:
                    f.write(cmd_content)
                with open(bat_dest, "w", encoding="utf-8") as f:
                    f.write(cmd_content)
                with open(ps_dest, "w", encoding="utf-8") as f:
                    f.write(ps1_content)
                with open(sh_dest, "w", encoding="utf-8") as f:
                    f.write(sh_content)
                    
                installed_locations.append(d)
        except Exception as e:
            print(f"Skipped {d}: {e}")

    print("[OK] VORTEX command registered successfully in:")
    for loc in installed_locations:
        print(f"  - {loc}")

if __name__ == "__main__":
    install_vortex_globally()
