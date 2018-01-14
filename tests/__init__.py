# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import time
import unittest

from hypothesis import given, settings, unlimited
import hypothesis.strategies as st
import json

import ahk_json


try:
    unichr
    unicode
except NameError:
    unichr = chr
    unicode = str


ahk_instance = ahk_json.AHK()


def standardize(thing):
    if isinstance(thing, dict):
        return {
            standardize(key): standardize(value)
            for key, value in thing.items()
        }
    if isinstance(thing, list):
        return [
            standardize(value)
            for value in thing
        ]
    if isinstance(thing, bool) or thing is None:
        return unicode(int(thing or 0))
    return unicode(thing)


lowercase_characters = st.characters(
    blacklist_characters=
        [unichr(c) for c in range(65, 91)]
        + [unicode(i) for i in range(10)]
        + [unichr(0)]
)
text = st.text(alphabet=lowercase_characters)

key_strategy = lowercase_characters
value_strategy = (
    text |
    st.integers(min_value=-1000, max_value=1000) |
    st.sampled_from([1.04, -1.04]) |
    st.booleans() |
    st.none()
)
json_strategy = st.recursive(
    st.dictionaries(key_strategy, value_strategy),
    lambda children: st.dictionaries(key_strategy, children),
    max_leaves=3
)


class TestThings(unittest.TestCase):
    @given(json_strategy)
    @settings(max_examples=200, deadline=None, timeout=unlimited)
    def test_identity(self, expected):
        expected['function'] = 'identity'
        ahk_instance.write(expected)
        actual = ahk_instance.read()
        self.assertEqual(standardize(expected), actual)


def find_files(base, extensions):
    for root, directories, files in os.walk(base):
        for filename in files:
            if not filename.endswith(tuple('.' + e for e in extensions)):
                continue
            if '.tox' in root:
                continue
            yield os.path.join(root, filename)


class TestStandards(unittest.TestCase):
    def test_utf8_bom(self):
        bad_files = []
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        for path in find_files(base, ['ahk']):
            with open(path, 'rb') as f:
                blob = f.read(len(codecs.BOM_UTF8))

            # Find any files missing a UTF-8 BOM.
            if blob and blob[:len(codecs.BOM_UTF8)] != codecs.BOM_UTF8:
                bad_files.append(os.path.relpath(path, base))

        if not bad_files:
            return

        msg = 'These files are missing a UTF-8 BOM (byte order mark):\n\n'
        msg += '\n'.join(bad_files)
        msg += '\n\nYou must add the following bytes at the top of each file:\n'
        msg += repr(codecs.BOM_UTF8)[1:-1]
        self.assertFalse(bad_files, msg)

    def test_utf8_declaration(self):
        declaration = '# -*- coding: utf-8 -*-'.encode('utf-8')
        bad_files = []
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        for path in find_files(base, ['py']):
            with open(path, 'rb') as f:
                blob = f.read(len(codecs.BOM_UTF8) + len(declaration))
            if blob and blob[:len(codecs.BOM_UTF8)] == codecs.BOM_UTF8:
                blob = blob[len(codecs.BOM_UTF8):]

            # Find any Python files missing an encoding declaration.
            if blob and not blob.startswith(declaration):
                bad_files.append(os.path.relpath(path, base))

        if not bad_files:
            return

        msg = 'These files are missing an encoding declaration:\n\n'
        msg += '\n'.join(bad_files)
        msg += '\n\nYou must add this line to the top of each file:\n'
        msg += '# -*- coding: utf-8 -*-'
        self.assertFalse(bad_files, msg)

    def test_utf8_encoded(self):
        bad_files = []
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        for path in find_files(base, ['ahk', 'py']):
            with open(path, 'rb') as f:
                blob = f.read()
            if blob[:len(codecs.BOM_UTF8)] == codecs.BOM_UTF8:
                blob = blob[:len(codecs.BOM_UTF8)]

            # Find any files that cannot be decoded as UTF-8.
            try:
                blob.decode('utf-8')
            except UnicodeDecodeError:
                bad_files.append(os.path.relpath(path, base))

        if not bad_files:
            return

        msg = 'These files are not encoded in UTF-8:\n\n'
        msg += '\n'.join(bad_files)
        self.assertFalse(bad_files, msg)


def run():
    unittest.main(exit=False)
    ahk_instance.write({'function': 'exit_ahk'})


if __name__ == '__main__':
    run()
