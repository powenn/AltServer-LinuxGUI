# AltServer-Linux GUI wrote in PyQT
# This is the update part
# Author of the script : powen

# import
import subprocess
import requests

LatestVersion = requests.get(
    "https://github.com/powenn/AltServer-LinuxGUI/raw/main/version"
).text
GetReleaseCMD = f"curl -L https://github.com/powenn/AltServer-LinuxGUI/releases/download/{LatestVersion}/AltServer.deb > /tmp/AltServer.deb"

subprocess.run(GetReleaseCMD, shell=True)
