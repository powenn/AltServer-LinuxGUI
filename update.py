# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
import subprocess
import os

cwd = os.getcwd()
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')
GetReleaseCMD='curl -L https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServer.deb > AltServer.deb' %LatestVersion

subprocess.run(GetReleaseCMD,shell=True)
