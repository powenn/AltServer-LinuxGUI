# AltServer-Linux GUI wrote in PyQT
# This is the Main part for functions
# Author of the GUI : powen

# import
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PySide2 import QtCore
from subprocess import *
import subprocess
import os
import sys

# set path
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

AltServer = resource_path("AltServer")
AltServerDaemon = resource_path("AltServerDaemon")

# Version 
LocalVersion=subprocess.check_output("sed -n 1p %s" %resource_path("version"),shell=True).decode('utf-8').replace("\n", "")
LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')

# Function part
@QtCore.Slot()
def about_message():
    msg_box = QMessageBox()
    msg_box.setIconPixmap(QPixmap(resource_path("Icon@128.png")))
    msg_box.setWindowTitle('AltServer-Linux')
    msg_box.setInformativeText('GUI by powenn on Github\n\nAltServer-Linux by NyaMisty on Github\n\nNot offical AltServer from Riley Testut')
    msg_box.setDetailedText('Source code :\nhttps://github.com/powenn/AltServer-LinuxGUI\n\nFor questions about this GUI, you can contact @powen00hsiao on Twitter')
    msg_box.exec()

@QtCore.Slot()
def Installation():
    DeviceCheck=subprocess.run('idevicepair pair',shell=True)
    if DeviceCheck.returncode == 1 :
        errmsg_box = QMessageBox()
        errmsg_box.setText('Please make sure connected to your device\n\nAnd accept the trust dialog on the screen of the device, then attempt to pair again.')
        errmsg_box.exec()
    if DeviceCheck.returncode == 0 :
        PATH=resource_path("AltStore.ipa")
        UDID=subprocess.check_output("lsusb -v 2> /dev/null | grep -e 'Apple Inc' -A 2 | grep iSerial | awk '{print $3}'",shell=True).decode('utf-8').replace("\n", "")
        AccountArea=QDialog()
        Layout = QVBoxLayout()
        Privacy_msg = QLabel("Your Apple ID and password are not saved\nand are only sent to Apple for authentication.")
        Privacy_msg.setFont(QFont('Arial', 10))
        label = QLabel("Please Enter your Apple ID and password")
        IDInputArea = QLineEdit(placeholderText="Apple ID")
        PasswordInputArea = QLineEdit(placeholderText="Password")
        btn = QPushButton()
        Success_msg = QSystemTrayIcon()  

        def ButtonClicked():
            AccountArea.close()
            AppleID=IDInputArea.text()
            Password=PasswordInputArea.text()
            print(AppleID+','+Password)
            InsAltStoreCMD='%s -u %s -a %s -p %s %s > %s' % (resource_path("AltServer"),UDID,AppleID,Password,PATH,resource_path("log.txt"))
            print(InsAltStoreCMD)
            Installing = True
            WarnTime=0
            InsAltStore=subprocess.Popen(InsAltStoreCMD, stdin=PIPE, stdout=PIPE, shell=True)
            while Installing :   
                CheckIns=subprocess.run('grep "Installation Failed" %s' %resource_path("log.txt"),shell=True)
                CheckWarn=subprocess.run('grep "Are you sure you want to continue?" %s' %resource_path("log.txt"),shell=True)
                CheckSuccess=subprocess.run('grep "Installation Succeeded" %s' %resource_path("log.txt"),shell=True)

                if CheckIns.returncode == 0 :
                    Installing = False
                    InsAltStore.terminate()
                    Failmsg=subprocess.check_output("tail -6 %s" %resource_path("log.txt"),shell=True).decode('utf-8')
                    Failmsg_box = QMessageBox()
                    Failmsg_box.setText(Failmsg)
                    Failmsg_box.exec()
                if CheckWarn.returncode == 0 and WarnTime == 0 :
                    Warnmsg=subprocess.check_output("tail -8 %s" %resource_path("log.txt"),shell=True).decode('utf-8')
                    Warnmsg_box = QMessageBox()
                    buttonReply = QMessageBox.warning(Warnmsg_box, 'Alert', Warnmsg, QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
                    if buttonReply == QMessageBox.Yes:
                        InsAltStore.communicate(input=b'\n')
                    
                    if buttonReply == QMessageBox.No :
                        Installing = False
                        os.system('pkill -TERM -P {pid}'.format(pid=InsAltStore.pid)) 
                        Cancelmsg_box = QMessageBox()
                        Cancelmsg_box.setText("Installation Canceled")
                        Cancelmsg_box.exec()
                    WarnTime = 1
                if CheckSuccess.returncode == 0 :
                    Installing = False
                    Success_msg.setVisible(True)
                    Success_msg.showMessage("Installation Succeded","AltStore was successfully installed",QSystemTrayIcon.Information,200)

        btn.setText("Install")
        btn.clicked.connect(ButtonClicked)
        Layout.addWidget(label)
        Layout.addWidget(Privacy_msg)
        Layout.addWidget(IDInputArea)
        Layout.addWidget(PasswordInputArea)
        Layout.addWidget(btn)
        AccountArea.setLayout(Layout)
        AccountArea.exec()

@QtCore.Slot()
def pair():
    subprocess.run('idevicepair pair',shell=True)

@QtCore.Slot()
def restart_daemon():
    subprocess.run('killall %s' %AltServerDaemon,shell=True)
    subprocess.run('idevicepair pair',shell=True)
    subprocess.run('%s &> /dev/null &' %AltServerDaemon,shell=True)

@QtCore.Slot()
def check_update():
    subprocess.run("curl -Lsk 'https://github.com/powenn/AltServer-LinuxGUI/raw/main/update.py' | python3",shell=True)

# Show update avaliable message
@QtCore.Slot()
def UpdateNotification() :
    if LatestVersion != LocalVersion :
        Update_Avaliable_box = QMessageBox()
        Update_Avaliable_box.setText('UPDATE AVALIABLE')
        Update_Avaliable_box.exec()