# Easier way to quickly build scripts and update version.
import PyInstaller.__main__
import subprocess


PyInstaller.__main__.run([
    'networktest.py',
    '--onefile',
    '--distpath',
    'C:\\Users\\K\\Documents\\networktest'
])

PyInstaller.__main__.run([
    'report.py',
    '--onefile',
    '--distpath',
    'C:\\Users\\K\\Documents\\networktest'
])

# Append overall version only when build.py is run:
# Incase there has been multiple builds since actual version update:
subprocess.call(str('git checkout HEAD VERSION.txt'))
version = open('VERSION.txt', 'r').read().split(".")
versionMinor = int(version[2])
newver = [version[0], version[1], str(versionMinor + 1)]
verout = '{}.{}.{}'.format(version[0], version[1], str(versionMinor + 1))
open('VERSION.txt', 'w').write(verout)
# Major versions update must be manually managed.