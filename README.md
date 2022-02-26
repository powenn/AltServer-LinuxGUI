# AltServer-LinuxGUI
 
Currently Works on newer debian-based linux distributions

Demo videos at the bottom

AltServer from https://github.com/NyaMisty/AltServer-Linux/releases

Special thanks to [NyaMisty](https://github.com/NyaMisty) for AltServer-Linux project 

![photo][1]

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

Just make sure it has execute permission ,and double click to run 

If you didn't see the app display on tray,you have to install `gnome-shell-extension-appindicator`
```
sudo apt install gnome-shell-extension-appindicator
```

For older versions and others linux distributions,you have to compile it manually at the moment



## How to build

It's written in PyQt5,so you have to install it and used modules and pyinstaller

Modify UI.spec,relpace the path to yours,and then run this

```
pyinstaller -i Icon.ico UI.spec
```


## Demo Video

<a href="https://www.youtube.com/watch?v=14uSA_JxZTo">
  <img src="https://img.youtube.com/vi/14uSA_JxZTo/maxresdefault.jpg" >
</a>

[1]:https://github.com/powenn/AltServer-LinuxGUI/blob/main/photos/01.jpg
