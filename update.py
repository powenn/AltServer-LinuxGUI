# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
import subprocess
import os

cwd = os.getcwd()
release_path = cwd+"/AltServerGUI"
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')
ReleaseName = cwd+"/AltServerGUI-new"

GetReleaseCMD='curl -L https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServerGUI > %s' %(LatestVersion,ReleaseName)
subprocess.run(GetReleaseCMD,shell=True)
subprocess.run("chmod +x %s" %ReleaseName,shell=True)
