import sys
import subprocess
import os

if not '-u' in sys.argv:
    raise Exception

if len(sys.argv) != sys.argv.index('-u') + 2:
    raise Exception

url = sys.argv[sys.argv.index('-u') + 1]

subprocess.run(['yt-dlp', url])