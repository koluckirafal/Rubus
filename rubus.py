#!/usr/bin/env python3

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
import argparse
from collections import OrderedDict
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

try:
    import pwd
except ImportError:
    import getpass

    pwd = None

ShortID = 'mcpi'
LongID = 'minecraft-pi'

versions = OrderedDict({'0.1.0': {'pkg_checksum': '',
                                  'exec_checksum': ''},
                        '0.1.1': {'pkg_checksum': 'e0d68918874cdd403de1fd399380ae2930913fcefdbf60a3fbfebb62e2cfacab',
                                  'exec_checksum': '45280c16930d3c787412a8c6239df77d8b34ad6d2698e01d73f94d914080f085'}})

LauncherVersion = '0.1.1'

RemotePool = 'https://s3.amazonaws.com/assets.minecraft.net/pi/'
RemoteFeed = 'http://pi.minecraft.net/?feed=rss2'

EnvPool = os.path.join(os.path.expanduser('~'), '.' + ShortID)
LocalPool = os.path.join(EnvPool, 'packages')
GamePool = os.path.join(EnvPool, 'versions')

Intro = '''\n    Rubus Launcher, copyright (C) Rafał 'BluRaf' Kołucki, 2014-2016\n\
    This program comes with ABSOLUTELY NO WARRANTY;
    for details press 'License' button in 'About' card.\n\
    This is free software, and you are welcome to redistribute it\n\
    under certain conditions;
    press 'License' button in 'About' card for details.\n'''


parser = argparse.ArgumentParser(description='Manages Minecraft: Pi Edition instances.')
parser.add_argument('--skip-checks', action='store_false', dest='platform_checks',
                    help='Disables platform compatibility checks.')


def current_user():
    if pwd:
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()


def detect_platform():
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


class Game:
    def __init__(self, long_id, short_id, version, package_checksum, main_exec_checksum):
        self.version = version
        self.short_id = short_id
        self.long_id = long_id
        self.package_checksum = package_checksum
        self.main_exec_checksum = main_exec_checksum

    def print_info(self):
        print(self.long_id + " (" + self.short_id + ") " + self.version)


class Instance:
    def __init__(self, base_game, texture_pack):
        self.base_game = base_game
        self.texture_pack = texture_pack


class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


def download(LongID, GameVersion, RemotePool, LocalPool):
    """Downloads game package"""
    RemotePackage = urllib.request.urlopen('%s%s-%s.tar.gz'
                                           % (RemotePool, LongID, GameVersion))
    LocalPackage = open(os.path.join(LocalPool, '%s-%s.tar.gz'
                                     % (LongID, GameVersion)), 'wb')
    LocalPackage.write(RemotePackage.read())
    LocalPackage.close()


def unpack(LongID, GameVersion, LocalPool, GamePool):
    """Unpacks game package"""
    LocalPackage = tarfile.open(os.path.join(LocalPool,
                                             '%s-%s.tar.gz'
                                             % (LongID, GameVersion)), "r:gz")
    LocalPackage.extractall(GamePool)
    LocalPackage.close()


def prepare_envtree(EnvPool, GamePool, LocalPool):
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


def prepare_gameinstance(ShortID, LongID, GameVersion,
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
        prepare_gameinstance(ShortID, LongID, GameVersion,
                             GamePool, RemotePool, LocalPool)


def run_binary(BinaryPath, BinaryName):
    print('''[ BINARY ] Trying to run game...''')
    print('[ BINARY ] {0}'.format(subprocess.check_output(
        ['file', os.path.join(BinaryPath, BinaryName)]
    ).decode("UTF-8").rstrip())
          )  # Check binary type
    subprocess.Popen(os.path.join(BinaryPath, BinaryName))  # Run binary


def just_launch_game(ShortID, LongID, GameVersion,
                     EnvPool, GamePool, LocalPool, RemotePool):
    prepare_envtree(EnvPool, GamePool, LocalPool)
    prepare_gameinstance(ShortID, LongID, GameVersion,
                         GamePool, RemotePool, LocalPool)
    try:
        run_binary(os.path.join(GamePool, GameVersion), LongID)
    except OSError as err:
        print("[ BINARY ] OS Error: {0}".format(err))
        messagebox.showerror(title="Executable file error",
                             message='Executable file format error.\n' +
                                     'Are you trying to run ' +
                                     'Minecraft: Pi Edition ' +
                                     'on processor other than ARM?')
        errorlevel = 1


def init_game(gver):
    return Game('minecraft-pi', 'mcpi', gver,
                versions[gver]['pkg_checksum'], versions[gver]['exec_checksum'])


def switch_game(game, version_number):
    game = init_game(list(versions)[version_number])


def main():
    args = parser.parse_args()
    print(Intro)
    print("Hello, " + current_user())

    if args.platform_checks:
        if False in detect_platform():
            if messagebox.showerror(title="Initialization error!",
                                    message='Incompatible platform, ' +
                                            'MCPi won\'t work properly. ' +
                                            'For details check stdout.'):
                sys.exit("[EXIT    ] Incompatible platform.")

    root = Tk()
    root.title("Rubus Launcher")
    root.resizable(False, False)

    selected_version_in_gui = len(versions)-1
    selected_version = list(versions)[selected_version_in_gui]

    instance_selector = ttk.Combobox(root, textvariable=selected_version)
    instance_selector['state'] = 'readonly'
    instance_selector['values'] = list(versions)
    instance_selector.current(selected_version_in_gui)


    game = init_game(instance_selector.get())
    game.print_info()

    infolabel = ttk.Label(root, text=('Rubus Launcher ' + LauncherVersion))
    launchbutton = ttk.Button(root, text=('Launch'),
                              command=lambda: just_launch_game(game.short_id, game.long_id,
                                                               game.version, EnvPool, GamePool,
                                                               LocalPool, RemotePool))
    status = StatusBar(root)
    status.set("Hello, " + current_user() + "! " + "Ready to play Minecraft: Pi Edition " + game.version)
    instance_selector.bind('<<ComboboxSelected>>', switch_game(game, selected_version_in_gui))

    status.grid(row=2, column=0, columnspan=2)
    infolabel.grid(row=0, column=0, columnspan=2)
    instance_selector.grid(row=1, column=0)
    launchbutton.grid(row=1, column=1)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
else:
    print("hack me!")
