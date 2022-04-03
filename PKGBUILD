pkgname=altserver-gui
pkgver=0.1.7
pkgrel=1
pkgdesc="GUI for AltServerLinux."
arch=('x86_64')
url="https://github.com/powenn/AltServer-LinuxGUI"
license=('AGPL3')
conflicts=('altserver-gui-bin')
options=('!strip' '!emptydirs')
depends=('python-pyqt5' 'pyside2' 'altserver-bin' 'libimobiledevice')
makedepends=('pyinstaller')
# makedepends=('pyside2' 'pyinstaller' 'python-pyqt5-3d' 'python-pyqt5-chart' 'python-pyqt5-datavisualization' 'python-pyqt5-networkauth' 'python-pyqt5-purchasing' 'python-pyqt5-webengine' 'python-pyqt5-sip')
source=("https://codeload.github.com/powenn/AltServer-LinuxGUI/tar.gz/refs/tags/${pkgver}"
    "https://raw.githubusercontent.com/powenn/AltServer-Linux-ShellScript/main/AltStore.ipa")
sha256sums=('cdf9b77198d12ba9a5e80360fc8a4e214dade53efb55786399bb7d67bb1bad50'
    '3d1e566ec2406587ddaf1ea749c4808d308fba50cb7f3ce39d7f6a980bc5440e')
noextract=('AltStore.ipa')

prepare() {
    tar -xzf "${pkgver}"
    mv "AltServer-LinuxGUI-${pkgver}"/* .
    mv "AltStore.ipa" "resources"
}

build() {
    pyinstaller -w -n altserver UI.py
}

package() {
    install -d "$pkgdir/usr/lib"
    cp -r "dist/altserver/" "$pkgdir/usr/lib"
    cp -r "resources" "$pkgdir/usr/lib/altserver/"
    chmod -R 0755 "$pkgdir/usr/lib/altserver"
    install -Dm0644 "resources/AppIcon.png" "$pkgdir/usr/share/icons/Icon.ico"
    install -Dm0644 "AltServer.desktop" "$pkgdir/usr/share/applications/AltServer.desktop"
}
