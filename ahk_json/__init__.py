# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import atexit
import itertools
import json
import os
import subprocess
import weakref


ahk_runner = os.path.join(os.path.dirname(__file__), 'runner.ahk')


def find_ahk():
    bases = [os.environ['programfiles'], os.environ.get('programfiles(x86)')]
    paths = ['autohotkey\AutoHotkeyU32.exe']
    failures = []
    for base in bases:
        for path in paths:
            exe = os.path.join(base, path)
            if os.path.isfile(exe):
                return exe
            failures.append(exe)
            
    msg = 'Unable to find an AutoHotkey executable at these locations:\n\n'
    msg += '\n'.join(failures)
    raise EnvironmentError(msg)


def close(reference):
    if reference():
        reference().__exit__()


class AHK(object):
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
