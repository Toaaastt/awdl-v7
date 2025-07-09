import subprocess
import platform
import re
import os
import time


def run_command_and_capture_percentage(file: str, url: str, file_name: str):
    DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
    CURRENT_DIR = os.path.join(DOWNLOAD_DIR, 'current')
    SCRIPT_PATH = os.path.join(os.getcwd(), 'downloader', file)

    os.makedirs(CURRENT_DIR, exist_ok=True)    
    
    command_args = [
        'python3' if platform.system() == 'Darwin' else 'python',
        SCRIPT_PATH,
        '-u',
        url
    ]

    try:
        with subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            cwd=CURRENT_DIR
        ) as proc:
            for line in proc.stdout:
                match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if match:
                    percent = float(match.group(1))
                    with open('download_progress.txt', 'w') as f:
                        f.write(str(percent))
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(2)
    
    
    
    


if __name__ == '__main__':
    run_command_and_capture_percentage('vidmoly.py', 'https://aniworld.to/redirect/3010838')