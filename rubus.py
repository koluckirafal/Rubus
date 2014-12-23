#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rubus Launcher for Minecraft Pi edition
Copyright (C) 2014, Rafał 'BluRaf' Kołucki

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import tarfile
import urllib.request
from subprocess import Popen, PIPE, STDOUT


shortID='mcpi'
longID='minecraft-pi'

gameVersion='0.1.1'
#gameVersion='0.1'   #if you want to download leaked version

#gameVersion >= 0.1.1
remotePool='https://s3.amazonaws.com/assets.minecraft.net/pi/'            
#gameVersion == 0.1.0
#remotePool='http://technowiz2cubed.weebly.com/uploads/1/6/8/9/16891832/'

envPool=os.path.join(os.path.expanduser('~'), '.' + shortID)
localPool=os.path.join(envPool, 'packages')
gamePool=os.path.join(envPool, 'versions')

intro='''\n    Rubus Launcher for Minecraft: Pi Edition, 
    copyright (C) Rafał 'BluRaf' Kołucki, 2014\n\
    This program comes with ABSOLUTELY NO WARRANTY; 
    for details press 'License' button in 'About' card.\n\
    This is free software, and you are welcome to redistribute it\n\
    under certain conditions; 
    press 'License' button in 'About' card for details.\n'''


while True:
    if os.path.isdir(envPool) == 1:
        print('Switching to launcher environment directory...')
        os.chdir(envPool)
        break
    else:
        print('Making launcher environment directory...')
        os.mkdir(envPool)


def checkLocalPool(localPool):
    while True:
        if os.path.isdir(localPool) == 1:
            print('- local repository exists')
            break
        else:
            print('- making local repository directory...')
            os.mkdir(localPool)

def checkGamePool(gamePool):
    while True:
        if os.path.isdir(gamePool) == 1:
            print('- unpacked game directory exists')
            break
        else:
            print('- unpacked game directory doesn\'t exist')
            os.mkdir(gamePool)


def download(longID, gameVersion, remotePool, localPool):
    remotePackage=urllib.request.urlopen('%s%s-%s.tar.gz' % (remotePool, longID, gameVersion))
    localPackage=open(os.path.join(localPool, '%s-%s.tar.gz' % (longID, gameVersion)), 'wb')
    localPackage.write(remotePackage.read())
    localPackage.close()

def unpack(longID, gameVersion, localPool, gamePool):
    localPackage=tarfile.open(os.path.join(localPool, \
					   '%s-%s.tar.gz' % (longID, gameVersion)), "r:gz")
    localPackage.extractall(gamePool)
    localPackage.close()


def prepareGameInstance(shortID, longID, gameVersion, gamePool, remotePool, localPool):
    if os.path.isdir(os.path.join(gamePool, gameVersion)) == 1:
        print('Switching to unpacked game directory, ...')
        os.chdir(os.path.join(gamePool, gameVersion))
    else:
        print('Unpacked game directory not detected, ...')
        try:
            print('trying to unpack game package...')
            unpack(longID, gameVersion, localPool, gamePool)
        except:
            print('... game package not found in local repository!')
            print('Downloading game package...')
            download(longID, gameVersion, remotePool, localPool)
            print('unpacking game package...')
            unpack(longID, gameVersion, localPool, gamePool)
            print('Game package unpacked!')
        print('Renaming version directory...')
        os.rename(os.path.join(gamePool, shortID), os.path.join(gamePool, gameVersion))
        prepareGameInstance(shortID, longID, gameVersion, gamePool, remotePool, localPool)


def runBinary(binaryPath, binaryName):
    Popen(['file', os.path.join(binaryPath, binaryName)])
    Popen(os.path.join(binaryPath, binaryName))
    
    
def main():
    print(intro)
    print('Checking for local repository:')
    checkLocalPool(localPool)
    print('Checking for game directories:')
    checkGamePool(gamePool)

    #prepare 
    prepareGameInstance(shortID, longID, gameVersion, gamePool, remotePool, localPool)

    #here launch the game
    runBinary(os.path.join(gamePool, gameVersion), longID)

    #Label(root, text=(longID + ' (' + shortID + ') ' + gameVersion)).pack()
    #root.mainloop()


if __name__ == "__main__":
    main()
else:
    print('intro')
    print("debug CLI ready.")
