# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
import subprocess
import os
import zipfile
from Main import *
# Version 
LocalVersion=subprocess.check_output("sed -n 1p %s" %resource_path("version"),shell=True).decode('utf-8').replace("\n", "")
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')

UpdateLog="""
What updated in version %s ?
Nothing yet

<< PLease rerun the App to apply the new version >>
""" %LatestVersion

if LatestVersion != LocalVersion :
    GetReleaseCMD='wget https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServerGUI.zip' %LatestVersion
    ReleaseFileName='AltServerGUI.zip'
    subprocess.run(GetReleaseCMD,shell=True)
    zipfile.ZipFile((ReleaseFileName),'r').extractall(resource_path("."))
    os.remove(ReleaseFileName)
    Updated_msg_box = QMessageBox()
    Updated_msg_box.setText(UpdateLog)
    Updated_msg_box.exec()
if LatestVersion == LocalVersion :
    Already_latest_msg_box = QMessageBox()
    Already_latest_msg_box.setText("you are using the latest release")
    Already_latest_msg_box.exec()