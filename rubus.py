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


ShortID = 'mcpi'
LongID = 'minecraft-pi'

GameVersion = '0.1.1'
# GameVersion = '0.1'   #if you want to download leaked version

# for GameVersion >= 0.1.1
RemotePool = 'https://s3.amazonaws.com/assets.minecraft.net/pi/'
# for GameVersion == 0.1.0
# RemotePool = 'http://technowiz2cubed.weebly.com/uploads/1/6/8/9/16891832/'

EnvPool = os.path.join(os.path.expanduser('~'), '.' + ShortID)
LocalPool = os.path.join(EnvPool, 'packages')
GamePool = os.path.join(EnvPool, 'versions')

Intro = '''\n    Rubus Launcher for Minecraft: Pi Edition,
    copyright (C) Rafał 'BluRaf' Kołucki, 2014\n\
    This program comes with ABSOLUTELY NO WARRANTY;
    for details press 'License' button in 'About' card.\n\
    This is free software, and you are welcome to redistribute it\n\
    under certain conditions;
    press 'License' button in 'About' card for details.\n'''


while True:
    if os.path.isdir(EnvPool) == 1:
        print('Switching to launcher environment directory...')
        os.chdir(EnvPool)
        break
    else:
        print('Making launcher environment directory...')
        os.mkdir(EnvPool)


def checkLocalPool(LocalPool):
    while True:
        if os.path.isdir(LocalPool) == 1:
            print('- local repository exists')
            break
        else:
            print('- making local repository directory...')
            os.mkdir(LocalPool)


def checkGamePool(GamePool):
    while True:
        if os.path.isdir(GamePool) == 1:
            print('- unpacked game directory exists')
            break
        else:
            print('- unpacked game directory doesn\'t exist')
            os.mkdir(GamePool)


def download(LongID, GameVersion, RemotePool, LocalPool):
    RemotePackage = urllib.request.urlopen('%s%s-%s.tar.gz'
                                           % (RemotePool, LongID, GameVersion))
    LocalPackage = open(os.path.join(LocalPool, '%s-%s.tar.gz'
                                     % (LongID, GameVersion)), 'wb')
    LocalPackage.write(RemotePackage.read())
    LocalPackage.close()


def unpack(LongID, GameVersion, LocalPool, GamePool):
    LocalPackage = tarfile.open(os.path.join(LocalPool,
                                             '%s-%s.tar.gz'
                                             % (LongID, GameVersion)), "r:gz")
    LocalPackage.extractall(GamePool)
    LocalPackage.close()


def prepareGameInstance(ShortID, LongID, GameVersion,
                        GamePool, RemotePool, LocalPool):
    if os.path.isdir(os.path.join(GamePool, GameVersion)) == 1:
        print('Switching to unpacked game directory, ...')
        os.chdir(os.path.join(GamePool, GameVersion))
    else:
        print('Unpacked game directory not detected, ...')
        try:
            print('trying to unpack game package...')
            unpack(LongID, GameVersion, LocalPool, GamePool)
        except:
            print('... game package not found in local repository!')
            print('Downloading game package...')
            download(LongID, GameVersion, RemotePool, LocalPool)
            print('unpacking game package...')
            unpack(LongID, GameVersion, LocalPool, GamePool)
            print('Game package unpacked!')
        print('Renaming version directory...')
        os.rename(os.path.join(GamePool, ShortID),
                  os.path.join(GamePool, GameVersion))
        prepareGameInstance(ShortID, LongID, GameVersion,
                            GamePool, RemotePool, LocalPool)


def runBinary(BinaryPath, BinaryName):
    Popen(['file', os.path.join(BinaryPath, BinaryName)])
    Popen(os.path.join(BinaryPath, BinaryName))


def main():
    print(Intro)
    print('Checking for local repository:')
    checkLocalPool(LocalPool)
    print('Checking for game directories:')
    checkGamePool(GamePool)

    # prepare
    prepareGameInstance(ShortID, LongID, GameVersion,
                        GamePool, RemotePool, LocalPool)

    # here launch the game
    runBinary(os.path.join(GamePool, GameVersion), LongID)

    # Label(root, text=(LongID + ' (' + ShortID + ') ' + GameVersion)).pack()
    # root.mainloop()


if __name__ == "__main__":
    main()
else:
    print('intro')
    print("debug CLI ready.")
