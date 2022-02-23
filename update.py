# AltServer-Linux GUI wrote in PyQT
# This is the update part 
# Author of the script : powen

# import 
import subprocess
import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PySide2 import QtCore
from subprocess import *

# set path
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Version 
LocalVersion=subprocess.check_output("sed -n 1p %s" %resource_path("version"),shell=True).decode('utf-8').replace("\n", "")
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')

UpdateLog="""
What updated in version %s ?
Nothing yet

""" %LatestVersion

if LatestVersion != LocalVersion :
    GetReleaseCMD='curl -O https://github.com/powenn/AltServer-LinuxGUI/releases/download/%s/AltServerGUI' %LatestVersion
    Updatemsg_box = QMessageBox()
    buttonReply = QMessageBox.information(Updatemsg_box, 'Update now ?', UpdateLog, QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
    if buttonReply == QMessageBox.Yes:
        Updating_msg_box = QMessageBox()
        Updating_msg_box.setText("Updating")
        Updating_msg_box.exec()
        Updating = subprocess.run(GetReleaseCMD,shell=True)
        if Updating.returncode == 0 :
            Update_done_msg_box = QMessageBox()
            Update_done_msg_box.setText("Update done\nPlease restart the app to apply the new version")
            Update_done_msg_box.exec()
        if Updating.returncode == 1 :
            Update_err_msg_box = QMessageBox()
            Update_err_msg_box.setText("Error occurred")
            Update_err_msg_box.exec()

    if buttonReply == QMessageBox.No:
        pass

if LatestVersion == LocalVersion :
    Already_latest_msg_box = QMessageBox()
    Already_latest_msg_box.setText("you are using the latest release")
    Already_latest_msg_box.exec()