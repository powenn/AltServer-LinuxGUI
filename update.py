# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
import subprocess

LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')

GetReleaseCMD='curl -O https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServerGUI' %LatestVersion
subprocess.run(GetReleaseCMD,shell=True)