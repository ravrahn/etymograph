
Search
======
The Search query takes a query string and returns an ordered array of words.

Query Format
------------
    ``/api/search?q=<query>``

Replace ``<query>`` with the search query.

Return Format
-------------
The query returns a JSON array of word objects, as described in the Info api page. The words are sorted by their closeness to the query.

Example Output
~~~~~~~~~~~~~~
    ``GET /api/search?q=example``
    ``[{
        "id": 246763,
        "orig_form": " example"
        "language": "eng",
        "lang_name": "English",
        "flag_count": 0
    },
    {
        "id": 589174,
        "orig_form": "example"
        "language": "enm",
        "lang_name": "Middle English",
        "flag_count": 0
    }]``