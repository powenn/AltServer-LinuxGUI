# AltServer-Linux GUI wrote in PyQT5
# This is the Main part for functions
# Author of the GUI : powen

# import
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PySide2 import QtCore
from subprocess import *
import subprocess
from shutil import *
import requests
import glob
import os
import sys

# set path
def resource_path(relative_path):
    base_path = os.path.abspath("./resources")
    return os.path.join(base_path, relative_path)

cwd = os.getcwd()
AltServer = resource_path("AltServer")
AutoStart = resource_path("AutoStart.sh")
Exec = cwd+"/altserver"
UserName = subprocess.check_output("whoami",shell=True).decode('utf-8').replace("\n", "")

def internet_stat():
    timeout = 5
    try:
        requests.get("https://github.com", timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
	    return False

# Version 
LocalVersion=subprocess.check_output("sed -n 1p %s" %resource_path("version"),shell=True).decode('utf-8').replace("\n", "")
LatestVersion=""

# Function part
@QtCore.Slot()
def about_message():
    msg_box = QMessageBox()
    msg_box.setIconPixmap(QPixmap(resource_path("Icon@128.png")))
    msg_box.setWindowTitle('AltServer-Linux')
    msg_box.setInformativeText('GUI by powenn on Github\n\nAltServer-Linux by NyaMisty on Github\n\nNot offical AltServer from Riley Testut\nVersion : %s' %LocalVersion)
    msg_box.setDetailedText('Source code :\nhttps://github.com/powenn/AltServer-LinuxGUI\nFor questions about this GUI, you can contact @powen00hsiao on Twitter')
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
            InsAltStoreCMD='%s -u %s -a %s -p %s %s > %s' % (resource_path("AltServer"),UDID,AppleID,Password,PATH,resource_path("log.txt"))
            Installing = True
            WarnTime=0
            InsAltStore=subprocess.Popen(InsAltStoreCMD, stdin=PIPE, stdout=PIPE, shell=True)
            while Installing :   
                CheckIns=subprocess.run('grep "Installation Failed" %s' %resource_path("log.txt"),shell=True)
                CheckWarn=subprocess.run('grep "Are you sure you want to continue?" %s' %resource_path("log.txt"),shell=True)
                CheckSuccess=subprocess.run('grep "Installation Succeeded" %s' %resource_path("log.txt"),shell=True)
                Check2fa=subprocess.run('grep "Requires two factor..." %s' %resource_path("log.txt"),shell=True)

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

                if Check2fa.returncode == 0 and WarnTime == 0 :           
                    msg_2fa_Area=QDialog()
                    msg_2fa_Area.setWindowTitle("Requires two factor")
                    code_2fa_Layout = QVBoxLayout()
                    code_2fa_label = QLabel("Please Enter two factor code")
                    Input_2fa_Area = QLineEdit(placeholderText="two factor code")
                    send_2fa_btn = QPushButton()
                    def Button_2fa_Clicked():
                        msg_2fa_Area.close()
                        code_2fa=Input_2fa_Area.text()
                        code_2fa=code_2fa+"\n"
                        code_2fa_bytes = bytes(code_2fa.encode())
                        InsAltStore.communicate(input=code_2fa_bytes)

                    send_2fa_btn.setText("Send")
                    send_2fa_btn.clicked.connect(Button_2fa_Clicked)
                    code_2fa_Layout.addWidget(code_2fa_label)
                    code_2fa_Layout.addWidget(Input_2fa_Area)
                    code_2fa_Layout.addWidget(send_2fa_btn)
                    msg_2fa_Area.setLayout(code_2fa_Layout)
                    msg_2fa_Area.exec()
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
    subprocess.run('killall %s' %AltServer,shell=True)
    subprocess.run('idevicepair pair',shell=True)
    subprocess.run('%s &> /dev/null &' %AltServer,shell=True)

@QtCore.Slot()
def check_update():
    Passwd_Check_Time = 0
    if (internet_stat()) == True  :
        LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')
        if LatestVersion == LocalVersion :
            Already_latest_msg_box = QMessageBox()
            Already_latest_msg_box.setText("you are using the latest release")
            Already_latest_msg_box.exec()
        if LatestVersion != LocalVersion :
            Updatemsg_box = QMessageBox()
            UpdateLog=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/updatelog.md",shell=True).decode('utf-8')
            Updatemsg_box.setText(UpdateLog)
            buttonReply = QMessageBox.information(Updatemsg_box, 'Update now ?', UpdateLog, QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes and Passwd_Check_Time == 0:
                Passwd_Check_Time = 1
                passwd_Area=QDialog()
                passwd_Area.setWindowTitle("Requires password")
                passwd_Layout = QVBoxLayout()
                passwd_label = QLabel("Please enter password for %s" %UserName)
                Input_passwd_Area = QLineEdit(placeholderText="password")
                send_passwd_btn = QPushButton()

                def Button_passwd_Clicked():
                    passwd_Area.close()
                    sudo_passwd=Input_passwd_Area.text()
                    sudo_passwd=sudo_passwd+"\n"
                    sudo_passwd_bytes = bytes(sudo_passwd.encode())
                    sudo_Check = os.system('echo "%s" | sudo -S %s' % (sudo_passwd, "echo 'check password'"))
                    if sudo_Check == 0 :
                        Updating_msg_box = QSystemTrayIcon()
                        Updating_msg_box.setVisible(True)
                        Updating_msg_box.showMessage("Updating","Please wait a moment",QSystemTrayIcon.Information,200)
                        update_pyfile = cwd+"/update.py"
                        deb_file = cwd+"/AltServer.deb"
                        subprocess.run("curl -L 'https://github.com/powenn/AltServer-LinuxGUI/raw/main/update.py' > %s" %update_pyfile,shell=True)
                        Updating = subprocess.run("python3 %s" %update_pyfile,shell=True)
                        if Updating.returncode == 0:
                            NewRelease_Installation = subprocess.Popen("sudo -S dpkg -i %s" %deb_file, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
                            NewRelease_Installation.communicate(input=sudo_passwd_bytes) 
                            subprocess.run("rm -rf %s" %deb_file,shell=True)
                            subprocess.run("rm -rf %s" %update_pyfile,shell=True)
                            if NewRelease_Installation.returncode == 0 :
                                Update_done_msg_box = QMessageBox()
                                Update_done_msg_box.setText("Update Done\nApp will restart to apply the new version")
                                Update_done_msg_box.exec()
                                os.execl(sys.executable,sys.executable,*sys.argv)
                            else :
                                Update_err_msg_box = QMessageBox()
                                Update_err_msg_box.setText("Error occurred")
                                Update_err_msg_box.exec()
                        if Updating.returncode == 1 :
                            Update_err_msg_box = QMessageBox()
                            Update_err_msg_box.setText("Error occurred")
                            Update_err_msg_box.exec()
                    if sudo_Check != 0 :
                        Wrong_sudo_passwd_box = QMessageBox()
                        Wrong_sudo_passwd_box.setText("Wrong password entered")
                        Wrong_sudo_passwd_box.exec() 
                send_passwd_btn.setText("Send")
                send_passwd_btn.clicked.connect(Button_passwd_Clicked)
                passwd_Layout.addWidget(passwd_label)
                passwd_Layout.addWidget(Input_passwd_Area)
                passwd_Layout.addWidget(send_passwd_btn)
                passwd_Area.setLayout(passwd_Layout)
                passwd_Area.exec()

            if buttonReply == QMessageBox.No:
                pass

    if (internet_stat()) == False:
        No_network_box = QMessageBox()
        No_network_box.setWindowTitle('No network')
        No_network_box.setText("Please connect to network")
        No_network_box.exec()
        
# Show update avaliable message
@QtCore.Slot()
def UpdateNotification() :
    if (internet_stat()) == True:
        LatestVersion=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/version",shell=True).decode('utf-8')
        if LatestVersion != LocalVersion :
            UpdateLog=subprocess.check_output("curl -Lsk https://github.com/powenn/AltServer-LinuxGUI/raw/main/updatelog.md",shell=True).decode('utf-8')
            Update_Avaliable_box = QMessageBox()
            Update_Avaliable_box.setWindowTitle('UPDATE AVALIABLE')
            Update_Avaliable_box.setText(UpdateLog)
            Update_Avaliable_box.exec()
            