#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rubus Launcher
Copyright (C) 2014-2015, Rafał 'BluRaf' Kołucki

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
import platform
import tarfile
import urllib.request
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

ShortID = 'mcpi'
LongID = 'minecraft-pi'

GameVersion = '0.1.1'
LauncherVersion = '0.1.1'

RemotePool = 'https://s3.amazonaws.com/assets.minecraft.net/pi/'
RemoteFeed = 'http://pi.minecraft.net/?feed=rss2'

EnvPool = os.path.join(os.path.expanduser('~'), '.' + ShortID)
LocalPool = os.path.join(EnvPool, 'packages')
GamePool = os.path.join(EnvPool, 'versions')

Intro = '''\n    Rubus Launcher, copyright (C) Rafał 'BluRaf' Kołucki, 2014-2015\n\
    This program comes with ABSOLUTELY NO WARRANTY;
    for details press 'License' button in 'About' card.\n\
    This is free software, and you are welcome to redistribute it\n\
    under certain conditions;
    press 'License' button in 'About' card for details.\n'''


def detectPlatform():
    if platform.machine() in ('armv6l' or 'armv7l'):
        print('''[PLATFORM] Running on ''' + platform.machine().upper())
        isARM = True
    else:
        print('''[PLATFORM] {!} Running on ''' + platform.machine() +
              ''' processor instead of ARM processor, ''' +
              '''MCPi won't even try to run :v''')
        isARM = False
    if os.path.isfile('/dev/vcihq'):
        print('''[PLATFORM] BCM VideoCore messaging port available''')
        isVCHIQ = True
    else:
        print('''[PLATFORM] {!} BCM VideoCore messaging port not available,
           MCPi won't work''')
        isVCHIQ = False
    if platform.system() == 'Linux':
        print('''[PLATFORM] Running under GNU/Linux distribution''')
        isLinux = True
    else:
        print('''[PLATFORM] {!} Not running under GNU/Linux system''')
        isLinux = False
    return (isARM, isVCHIQ, isLinux)


def download(LongID, GameVersion, RemotePool, LocalPool):
    '''Downloads game package'''
    RemotePackage = urllib.request.urlopen('%s%s-%s.tar.gz'
                                           % (RemotePool, LongID, GameVersion))
    LocalPackage = open(os.path.join(LocalPool, '%s-%s.tar.gz'
                                     % (LongID, GameVersion)), 'wb')
    LocalPackage.write(RemotePackage.read())
    LocalPackage.close()


def unpack(LongID, GameVersion, LocalPool, GamePool):
    '''Unpacks game package'''
    LocalPackage = tarfile.open(os.path.join(LocalPool,
                                             '%s-%s.tar.gz'
                                             % (LongID, GameVersion)), "r:gz")
    LocalPackage.extractall(GamePool)
    LocalPackage.close()


def prepareEnvTree(EnvPool, GamePool, LocalPool):
    if os.path.isdir(EnvPool) == 1:
        print('''[ENV     ] Switching to launcher environment directory...''')
        os.chdir(EnvPool)
    else:
        print('''[ENV     ] Preparing launcher environment directory...''')
        os.mkdir(EnvPool)
    print('''[ENV     ] Checking for game directories:''')
    if os.path.isdir(GamePool) == 1:
        print('''[ENV     ] - unpacked game directory exists''')
    else:
        print('''[ENV     ] - making unpacked game directory...''')
        os.mkdir(GamePool)
    print('''[ENV     ] Checking for local repository:''')
    if os.path.isdir(LocalPool) == 1:
        print('''[ENV     ] - local repository exists''')
    else:
        print('''[ENV     ] - making local repository directory...''')
        os.mkdir(LocalPool)


def prepareGameInstance(ShortID, LongID, GameVersion,
                        GamePool, RemotePool, LocalPool):
    if os.path.isdir(os.path.join(GamePool, GameVersion)) == 1:
        print('[GameEnv ] Switching to unpacked game directory...')
        os.chdir(os.path.join(GamePool, GameVersion))
    else:
        print('[GameEnv ] Unpacked game directory not detected, ...')
        try:
            print('[GameEnv ] trying to unpack game package...')
            unpack(LongID, GameVersion, LocalPool, GamePool)
        except IOError:
            print('[GameEnv ] ... game package not found in local repository!')
            print('[GameEnv ] Downloading game package...')
            download(LongID, GameVersion, RemotePool, LocalPool)
            print('[GameEnv ] Unpacking game package...')
            unpack(LongID, GameVersion, LocalPool, GamePool)
            print('[GameEnv ] Game package unpacked!')
        print('[GameEnv ] Renaming version directory...')
        os.rename(os.path.join(GamePool, ShortID),
                  os.path.join(GamePool, GameVersion))
        prepareGameInstance(ShortID, LongID, GameVersion,
                            GamePool, RemotePool, LocalPool)


def runBinary(BinaryPath, BinaryName):
    print('''[ BINARY ] Trying to run game...''')
    print('[ BINARY ] {0}'.format(subprocess.check_output(
        ['file', os.path.join(BinaryPath, BinaryName)]
        ).decode("UTF-8").rstrip())
    )  # Check binary type
    subprocess.Popen(os.path.join(BinaryPath, BinaryName))  # Run binary


def justLaunchGame(ShortID, LongID, GameVersion,
                   EnvPool, GamePool, LocalPool, RemotePool):
    prepareEnvTree(EnvPool, GamePool, LocalPool)
    prepareGameInstance(ShortID, LongID, GameVersion,
                        GamePool, RemotePool, LocalPool)
    runBinary(os.path.join(GamePool, GameVersion), LongID)


def main():
    print(Intro)
    if False in detectPlatform():
        if messagebox.showerror(title="Initialization error!",
                                message='Incompatible platform, ' +
                                        'MCPi won\'t work properly.'):
            sys.exit("[EXIT    ] Incompatible platform.")

    root = Tk()
    root.title("Rubus Launcher")
    infolabel = ttk.Label(root, text=('Rubus Launcher ' + LauncherVersion))
    launchbutton = ttk.Button(root, text=('Launch version ' + GameVersion),
                              command=lambda: justLaunchGame(ShortID, LongID,
                                                             GameVersion,
                                                             EnvPool, GamePool,
                                                             LocalPool,
                                                             RemotePool))
    infolabel.grid(row=0, column=1)
    launchbutton.grid(row=1, column=1)
    root.mainloop()
    sys.exit("[EXIT    ] Exited.")

if __name__ == "__main__":
    main()
else:
    print("hack me!")
