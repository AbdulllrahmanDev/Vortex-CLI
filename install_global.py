import os
import shutil

def install_vortex_globally():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    project_cmd = os.path.join(project_dir, "vortex.cmd")
    cli_py = os.path.join(project_dir, "downloader_cli.py")

    # Content of .cmd file
    cmd_content = f'@echo off\nchcp 65001 >nul\npython "{cli_py}" %*\n'
    with open(project_cmd, "w", encoding="utf-8") as f:
        f.write(cmd_content)

    # PowerShell runner
    ps1_content = f'& python "{cli_py}" $args\n'

    user_profile = os.environ.get("USERPROFILE", "")
    target_dirs = [
        os.path.join(user_profile, ".local", "bin"),
        os.path.join(user_profile, "AppData", "Roaming", "npm"),
        os.path.join(user_profile, "AppData", "Local", "Microsoft", "WindowsApps"),
        os.path.join(user_profile, "AppData", "Local", "agy", "bin"),
    ]

    installed_locations = []
    for d in target_dirs:
        try:
            if os.path.exists(d):
                cmd_dest = os.path.join(d, "vortex.cmd")
                bat_dest = os.path.join(d, "vortex.bat")
                ps_dest = os.path.join(d, "vortex.ps1")
                
                with open(cmd_dest, "w", encoding="utf-8") as f:
                    f.write(cmd_content)
                with open(bat_dest, "w", encoding="utf-8") as f:
                    f.write(cmd_content)
                with open(ps_dest, "w", encoding="utf-8") as f:
                    f.write(ps1_content)
                    
                installed_locations.append(d)
        except Exception as e:
            print(f"Skipped {d}: {e}")

    print("[OK] VORTEX command registered successfully in PATH folders:")
    for loc in installed_locations:
        print(f"  - {loc}")

if __name__ == "__main__":
    install_vortex_globally()
