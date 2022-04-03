# Copyright (c) 2018-2022 Kurt McKee <contactme@kurtmckee.org>
# The code is licensed under the terms of the MIT license.
# https://github.com/kurtmckee/ahk_json

import codecs
import json
import os

import hypothesis.strategies as st
from hypothesis import given, settings

import ahk_json

ahk_instance = ahk_json.AHK()


def standardize(thing):
    if isinstance(thing, dict):
        return {standardize(key): standardize(value) for key, value in thing.items()}
    if isinstance(thing, list):
        return [standardize(value) for value in thing]
    if isinstance(thing, bool) or thing is None:
        return str(int(thing or 0))
    return str(thing)


lowercase_characters = st.characters(
    blacklist_characters=(
        [chr(c) for c in range(65, 91)] + [str(i) for i in range(10)] + [chr(0)]
    )
)
text = st.text(alphabet=lowercase_characters)

key_strategy = lowercase_characters
value_strategy = (
    text
    | st.integers(min_value=-1000, max_value=1000)
    | st.sampled_from([1.04, -1.04])
    | st.booleans()
    | st.none()
)
json_strategy = st.recursive(
    st.dictionaries(key_strategy, value_strategy),
    lambda children: st.dictionaries(key_strategy, children),
    max_leaves=3,
)


@given(json_strategy)
@settings(max_examples=200)
def test_identity(expected):
    expected["function"] = "identity"
    ahk_instance.write(expected)
    actual = ahk_instance.read()
    assert standardize(expected) == actual


def test_file():
    filename = os.path.join(os.path.dirname(__file__), "test.json")
    with open(filename, "rb") as f:
        blob = f.read()
    expected = json.loads(blob.decode("utf-8"))

    instruction = {"function": "load_file", "filename": filename}
    ahk_instance.write(instruction)
    actual = ahk_instance.read()
    assert standardize(expected) == actual


def find_files(base, extensions):
    for root, directories, files in os.walk(base):
        for filename in files:
            if not filename.endswith(tuple("." + e for e in extensions)):
                continue
            if ".tox" in root:
                continue
            yield os.path.join(root, filename)


def test_ahk_utf8_bom():
    bad_files = []
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    for path in find_files(base, ["ahk"]):
        with open(path, "rb") as f:
            blob = f.read(len(codecs.BOM_UTF8))

        # Find any files missing a UTF-8 BOM.
        if blob and blob[: len(codecs.BOM_UTF8)] != codecs.BOM_UTF8:
            bad_files.append(os.path.relpath(path, base))

    msg = "These files are missing a UTF-8 BOM (byte order mark):\n\n"
    msg += "\n".join(bad_files)
    msg += "\n\nYou must add the following bytes at the top of each file:\n"
    msg += repr(codecs.BOM_UTF8)[1:-1]
    assert not bad_files, msg
