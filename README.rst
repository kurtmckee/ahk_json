..  Copyright (c) 2018-2022 Kurt McKee <contactme@kurtmckee.org>
..  The code is licensed under the terms of the MIT license.
..  https://github.com/kurtmckee/ahk_json


Parse JSON data in AutoHotkey
*****************************


``ahk_json`` allows you to parse JSON data in AutoHotkey.

It features Unicode support when loading and serializing JSON data,
and uses AutoHotkey objects to support JSON lists and dictionaries.
The code exists in a single file, ``json.ahk``, which you should put
in your ``lib/`` directory so that it can be found by ``#include``
directives.

To load JSON data from a string, use the ``json_load()`` function.

..  code:: ahk

    #include <json>

    blob := "{""a"": ""awesome"", ""b"": [0, 10, 20], ""c"": {""d"": true}}"
    data := json_load(blob)

    msgbox, % "data['a'] == '" . data["a"] . "'"  ; `awesome`
    msgbox, % "data['b'][1] == " . data["b"][1]  ; `10`
    msgbox, % "data['c']['d'] == " . data["c"]["d"]  ; `1`


To dump JSON data into a string, use the ``json_dump()`` function.

..  code:: ahk

    #include <json>

    data := {"a": 10, "b": ["it's", "a", "list"], "c": {"nest": "yes"}}
    blob := json_dump(data)

    msgbox, % blob



Limitations
===========

Due to mistakes in the AutoHotkey design, ``json_load()`` and ``json_dump()`` both
have limitations that currently cannot be corrected.


Booleans and ``null` are loaded as numbers
------------------------------------------

AutoHotkey has no concept of booleans or null values.
Its built-in ``true`` and ``false`` literals are aliases for ``1`` and ``0``, respectively.

To accommodate this limitation, ``json_load()`` loads these JSON values in this way:

=============== ================
JSON value      AutoHotkey value
=============== ================
``true``        ``1``
``false``       ``0``
``null``        ``0``
=============== ================


Numbers are dumped as strings
-----------------------------

AutoHotkey makes no distinction between text and numeric values.
As a result, when ``json_dump()`` renders values that are not objects or arrays,
there is no way to determine whether the value is a number or a string.
Therefore, ``json_dump()`` only outputs strings, even if the value might be numeric:

..  code:: ahk

    data := {"integer": 0, "float": 1.0}
    msgbox, % json_dump(data)  ; `{"integer": "0", "float": "1.0"}`


Applications that consume the JSON output from ``ahk_json`` must convert strings to numbers if needed.


JSON object keys are case insensitive
-------------------------------------

AutoHotkey ignores the case of all dictionary keys. As a result, if JSON data
contains keys that only differ by case, AutoHotkey will quietly overwrite the
existing data:

..  code:: ahk

    blob := "{""A"": ""UPPERCASE"", ""a"": ""lowercase""}"
    data := json_load(blob)
    msgbox, % "data['A'] == " . data["A"]  ; `data['A'] == lowercase`


Currently there is no known way to force AutoHotkey to respect the case of dictionary keys.
Applications that load JSON data must be aware that they may lose data due to AutoHotkey's behavior.


Some key names are reserved
---------------------------

AutoHotkey stores object data keys in the same namespace as object methods and attributes.
This means that key names like ``"base"`` and ``"length"`` will collide with AutoHotkey's own methods and attributes.

Currently there is no way to avoid these collisions.
Applications that load JSON data should design their domain-specific JSON schema to avoid the problem.


Null characters cannot be used
------------------------------

AutoHotkey cannot handle null characters (``\`0``) in strings.
If a JSON string is loaded with an escaped null character (``\u0000``), data may be lost.

Applications should avoid dealing with null characters in JSON.


Unit tests
==========

``ahk_json`` uses Python to test the code in ``json.ahk``.

If you want to run the test suite you must install AutoHotkey 1.1.27.04 or
higher. Python will automatically find and launch AutoHotkey from the
``PROGRAMFILES`` or ``PROGRAMFILES(x86)`` environment variables.



License
=======

``ahk_json`` is released under the terms of `the MIT license`_.
The text of the license can be found in the ``LICENSE.txt`` file.

..  _the MIT license: https://opensource.org/licenses/MIT
