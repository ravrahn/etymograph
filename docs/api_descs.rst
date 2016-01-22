
Descendants
===========
The descendants query takes a word ID, and returns the descendants of the word.

Query Format
------------
    ``/api/<word_id>/descs?depth=<depth>``

Replace ``<word_id>`` with the word ID, and ``<depth>`` with the depth. Omit the query string to set the depth to unlimited.

Return Format
-------------
The query returns a JSON object similar to the word object, but with the additional ``descs`` property. This is an array of word objects that are the word's descendants. Each word in the array will also have a ``descs`` property.

Example Output
~~~~~~~~~~~~~~

    ``{
        "id": 246764,
        "orig_form": " example\n",
        "language": "enm",
        "lang_name": "Middle English",
        "flag_count": 0,
        "descs": [
            {
                "id": 246763,
                "orig_form": " example",
                "language": "eng",
                "lang_name": "English",
                "flag_count": 0,
                "descs": [
                    {
                        "id": 192273,
                        "orig_form": " counterexample\n",
                        "language": "eng",
                        "lang_name": "English",
                        "flag_count": 0,
                        "descs": []
                    }
                ]
            }
        ]
    }``
