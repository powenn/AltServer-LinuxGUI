# AltServer-LinuxGUI

Currently providing release for x64

Tested on Debian11,Ubuntu20.04,Manjaro21.2.4

If the release not working on the distribution which you're using,please build manually with the instruction below

Demo videos at the bottom

AltServer from https://github.com/NyaMisty/AltServer-Linux/releases

Special thanks to [NyaMisty](https://github.com/NyaMisty) for AltServer-Linux project 

 <img src="https://github.com/powenn/AltServer-LinuxGUI/blob/main/photos/02.png" alt="02.png"> 
 <img src="https://github.com/powenn/AltServer-LinuxGUI/blob/main/photos/04.png" alt="04.png">

## About the GUI

It's just a simple GUI to make the operation of AltServer-Linux more easier ,now inclides features below

## Features
- System tray app just like AltServer on MacOS

### Others editions are available

For python edition,you can get from [AltServer-Linux-PyScript](https://github.com/powenn/AltServer-Linux-PyScript)

For shell script edition,you can get from [AltServer-Linux-ShellScript](https://github.com/powenn/AltServer-Linux-ShellScript)

## Announcement

AltServer for Linux is from [NyaMisty](https://github.com/NyaMisty),so you should thank to NyaMisty more ,also for any question to AltServer-Linux,you should ask or crate issue in https://github.com/NyaMisty/AltServer-Linux rather than this repository,I just providing GUI to make the operation more easier. 

## Note 

Needed dependencies

```
sudo apt-get install usbmuxd libimobiledevice6 libimobiledevice-utils wget curl
```

## How to install and uninstall

Install

`Download the release and do `
```
sudo dpkg -i AltServer.deb
```
or
```
sudo apt install ./AltServer.deb
```

Uninstall

```
sudo apt remove altserverlinux
```
or
```
sudo dpkg -r altserverlinux
```

If you are using gnome and didn't see the app display on tray,you have to install `gnome-shell-extension-appindicator`

And enable it

please check https://extensions.gnome.org/extension/615/appindicator-support/



## How to build

For others architecture,replace AltServer binary in resources folder,and then run build.sh

It's written in PyQt5,so you have to install it and all used modules and pyinstaller then run build.sh(If you are on lower version os,you might need to do some modification)

I am using VScode to maintain this,so I would say that VScode is a great choice to build,test,develop or contribute to it 

Require dependencies

`python3-pyqt5 python3-pip`
```
sudo apt install python3-pyqt5 python3-pip
```
```
python3 -m pip install --upgrade pip
```
`Pyside2 pyinstaller pyqt5-plugins `
```
pip3 install Pyside2 pyinstaller pyqt5-plugins 
```
Place AltServer-Linux binary and AltStore.ipa into resources folder then run build.sh
```
resources
    AltServer
    AltStore.ipa
    AutoStart.sh
    and others
```

## Demo Video

<a href="https://www.youtube.com/watch?v=kEYg-f8lDOQ">
  <img src="https://img.youtube.com/vi/kEYg-f8lDOQ/maxresdefault.jpg" >
</a>
