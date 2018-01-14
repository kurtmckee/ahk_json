# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re

from distutils.core import setup


def get_version():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'ahk_json/lib/json.ahk'), 'r') as f:
        blob = f.read()
    return re.search(r'VERSION = "(.+)"', blob).group(1)


setup(
    name='ahk_json',
    version=get_version(),
    url='https://github.com/kurtmckee/ahk_json',
    author='Kurt McKee',
    author_email='contactme@kurtmckee.org',
    license='MIT',
    long_description='Parse JSON in AutoHotkey',
)
