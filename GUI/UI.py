# AltServer-Linux GUI wrote in PyQT5
# This is the UI part 
# Author of the GUI : powen

# import
from Main import *

# check permission
if subprocess.run('stat %s | grep -- "-rw-r--r--"' %AltServer,shell=True) != "" :
    subprocess.run("chmod +x %s" %AltServer,shell=True)
if subprocess.run('stat %s | grep -- "-rw-r--r--"' %AltServerDaemon,shell=True) != "" :
    subprocess.run("chmod +x %s" %AltServerDaemon,shell=True)
if subprocess.run('stat %s | grep -- "-rw-r--r--"' %AutoStart,shell=True) != "" :
    subprocess.run("chmod +x %s" %AutoStart,shell=True)

# UI part
app = QApplication(sys.argv)
app.setApplicationName("AltServer")
app.setQuitOnLastWindowClosed(False)

# Create the icon
icon = QIcon(resource_path("MenuBar.png"))
app.setWindowIcon(QIcon(resource_path("AppIcon.png")))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
About = QAction("About AltServer")
About.triggered.connect(about_message)
menu.addAction(About)
menu.addSeparator()

# Add Inatall AltStore option to the menu.
AltInstall = QAction('Install AltStore')
AltInstall.triggered.connect(Installation)
menu.addAction(AltInstall)
menu.addSeparator()

# Add Launch At Login in  option to the menu.
LaunchAtLogin = QAction("Launch at Login",checkable=True)
launch_enable=False
CheckTime=0
if glob.glob("/home/*/.config/autostart/AltServer.desktop") and CheckTime==0:
    LaunchAtLogin.setChecked(True)
    launch_enable=True
    CheckTime=1
if not glob.glob("/home/*/.config/autostart/AltServer.desktop") and CheckTime==0:
    LaunchAtLogin.setChecked(False)
    launch_enable=False
    CheckTime=1
def launch_config() :
    if LaunchAtLogin.isChecked():
        launch_enable=True
    if not LaunchAtLogin.isChecked():
         launch_enable=False
    if launch_enable :
        LaunchAtLogin.setChecked(True)
        sh_file = open(AutoStart, "r")
        list_of_lines = sh_file.readlines()
        list_of_lines[8] = 'Exec="%s"\n' %Exec
        sh_file = open(AutoStart, "w")
        sh_file.writelines(list_of_lines)
        sh_file.close()
        subprocess.run("%s" %resource_path("AutoStart.sh"),shell=True)
    if not launch_enable :
        LaunchAtLogin.setChecked(False)
        subprocess.run("rm -rf /home/*/.config/autostart/AltServer.desktop",shell=True)

LaunchAtLogin.toggled.connect(launch_config)

menu.addAction(LaunchAtLogin)

# Add Pair in  option to the menu.
Pair = QAction("Pair")
menu.addAction(Pair)
Pair.triggered.connect(pair)

# Add Restart Daemon in  option to the menu.
RestartDaemon = QAction("Restart AltDaemon")
menu.addAction(RestartDaemon)
RestartDaemon.triggered.connect(restart_daemon)
menu.addSeparator()

# Add Check Update option to the menu.
CheckUpdate = QAction("Check for Update")
CheckUpdate.triggered.connect(check_update)
menu.addAction(CheckUpdate)
menu.addSeparator()

# Add a Quit option to the menu.
def app_quit():
    subprocess.run('killall %s' %AltServerDaemon,shell=True)
    app.quit()
    
quit = QAction("Quit AltServer")
quit.triggered.connect(app_quit)

quit.setCheckable(False)
quit.setShortcut('Ctrl+Q')
menu.addAction(quit)


# Add the menu to the tray
tray.setContextMenu(menu)
subprocess.run('%s &> /dev/null &' %AltServerDaemon,shell=True)
UpdateNotification()
app.exec_()

