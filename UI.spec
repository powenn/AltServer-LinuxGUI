# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['/home/powen/AltServerGUI/GUI/UI.py'],
             pathex=['/home/powen/AltServerGUI/GUI'],
             binaries=[],
             datas=[('/home/powen/AltServerGUI/GUI/AltServer','.'),('/home/powen/AltServerGUI/GUI/AltServerDaemon','.'),('/home/powen/AltServerGUI/GUI/AltStore.ipa','.'),('/home/powen/AltServerGUI/GUI/AppIcon.png','.'),('/home/powen/AltServerGUI/GUI/Icon@128.png','.'),('/home/powen/AltServerGUI/GUI/MenuBar.png','.'),('/home/powen/AltServerGUI/GUI/version','.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='AltServerGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
