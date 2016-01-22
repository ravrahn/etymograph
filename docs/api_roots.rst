
Roots
=====
The roots query takes a word ID, and returns the roots of the word.

Query Format
------------
    ``/api/<word_id>/roots?depth=<depth>``

Replace ``<word_id>`` with the word ID, and ``<depth>`` with the depth. Omit the query string to set the depth to unlimited.

Return Format
-------------
The query returns a JSON object similar to the word object, but with the additional ``roots`` property. This is an array of word objects that are the word's roots. Each word in the array will also have a ``roots`` property.

Example Output
~~~~~~~~~~~~~~

    ``{
        "id": 246763,
        "orig_form": " example",
        "language": "eng",
        "lang_name": "English",
        "flag_count": 0,
        "roots": [
            {
                "id": 246764,
                "orig_form": "example",
                "language": "enm",
                "lang_name": "Middle English",
                "flag_count": 0,
                "roots": [
                    {
                        "id": 602351,
                        "orig_form": "essample",
                        "language": "fro",
                        "lang_name": "Old French",
                        "flag_count": 0,
                        "roots": []
                    }
                ]
            }
        ]
    }``
