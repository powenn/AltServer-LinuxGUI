# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
from platform import release
import subprocess
import os

cwd = os.getcwd()
release_path = cwd+"/AltServerGUI.zip"
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')

GetReleaseCMD='curl -L https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServerGUI.zip > %s' %(LatestVersion,release_path)
subprocess.run(GetReleaseCMD,shell=True)