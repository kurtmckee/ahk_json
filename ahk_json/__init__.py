# Copyright (c) 2018-2022 Kurt McKee <contactme@kurtmckee.org>
# The code is licensed under the terms of the MIT license.
# https://github.com/kurtmckee/ahk_json

import atexit
import json
import os
import pathlib
import subprocess
import weakref


ahk_runner = os.path.join(os.path.dirname(__file__), 'runner.ahk')


def find_ahk():
    bases = [
        pathlib.Path(__file__).parent.parent,
        pathlib.Path(os.environ['programfiles']),
    ]
    if os.environ.get('programfiles(x86)'):
        bases.append(pathlib.Path(os.environ['programfiles(x86)']))

    paths = [
        'AutoHotkeyU32.exe',
        'AutoHotkeyU64.exe',
        'autohotkey/AutoHotkeyU32.exe',
        'autohotkey/AutoHotkeyU64.exe',
    ]
    failures = []
    for base in bases:
        for path in paths:
            exe = base / path
            if exe.is_file():
                return str(exe)
            failures.append(str(exe))

    msg = 'Unable to find an AutoHotkey executable at these locations:\n\n'
    msg += '\n'.join(failures)
    raise EnvironmentError(msg)


def close(reference):
    if reference():
        reference().__exit__()


class AHK:
    def __init__(self, exe=None):
        if exe is None:
            exe = find_ahk()

        self.instance = subprocess.Popen(
            [exe, ahk_runner],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        atexit.register(close, weakref.ref(self))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.write({'function': 'exit_ahk'})

    def write(self, command):
        blob = json.dumps(command, ensure_ascii=True).encode('utf-8')
        self.instance.stdin.write(blob + '\n'.encode('utf-8'))
        self.instance.stdin.flush()

    def read(self):
        blob = self.instance.stdout.readline()
        return json.loads(blob.decode('utf-8'))
