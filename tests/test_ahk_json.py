# Copyright (c) 2018-2022 Kurt McKee <contactme@kurtmckee.org>
# The code is licensed under the terms of the MIT license.
# https://github.com/kurtmckee/ahk_json

import codecs
import json
import os

import hypothesis.strategies as st
from hypothesis import given, settings, example

import ahk_json

ahk_instance = ahk_json.AHK()


def standardize(thing):
    if isinstance(thing, dict):
        return {standardize(key): standardize(value) for key, value in thing.items()}
    if isinstance(thing, list):
        # If the list is empty, the AHK code will render it as a JSON object.
        return [standardize(value) for value in thing] or {}
    if isinstance(thing, bool) or thing is None:
        return str(int(thing or 0))
    return str(thing)


def key_filter(value: str) -> bool:
    """Prevent specific keys from causing problems.

    *   "1" is blocked to prevent this identity crisis: {"1": {}} -> [{}]
    *   The rest are blocked because Autohotkey keeps its keys in the same
        namespace as its underlying methods and attributes.

    """

    return value not in ["1", "base", "length", "__get", "__put"]


lowercase_characters = st.characters(
    blacklist_characters=["\0"],
    blacklist_categories=["Lu"],
)

key_strategy = lowercase_characters.filter(key_filter)

literal_strategy = (
    st.text(alphabet=st.characters(blacklist_characters=["\0"]))
    | st.integers(min_value=-100000, max_value=100000)
    | st.floats(min_value=-10.0, max_value=10.0, width=16)
    | st.booleans()
    | st.none()
)

value_strategy = literal_strategy | st.lists(literal_strategy)

object_strategy = st.recursive(
    st.dictionaries(key_strategy, value_strategy),
    lambda children: st.dictionaries(key_strategy, children),
    max_leaves=3,
)

array_strategy = st.recursive(
    st.lists(value_strategy),
    lambda children: st.lists(value_strategy),
)


@given(literal_strategy | array_strategy | object_strategy)
@settings(max_examples=1000, deadline=500)
@example(True)
@example(False)
@example(None)
@example("a")
@example(1)
@example(1.0)
@example({"a": "b"})
@example([1, 2, 3])
def test_identity(expected):
    directive = {"function": "identity", "value": json.dumps(expected)}
    ahk_instance.write(directive)
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
