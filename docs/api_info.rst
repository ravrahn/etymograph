
Info
====
The info query takes a word ID and returns information about the word.

Query Format
------------
    ``/api/info/<word_id>``

Replace ``<word_id>`` with the word ID.

Return Format
-------------
The query returns an object with the following properties::
    * ``id``: The ID of the word, used in other API requests.
    * ``orig_form``: The word in its original script.
    * ``language``: The word's language code.
    * ``lang_name``: The English name of the language.
    * ``flag_count``: How many times the word has been flagged as incorrect.
The object may also contain these optional properties, if they exist for the word::
    * ``definition``: The word's definition.
    * ``ipa_form``: The IPA transcription of the word.
    * ``latin_form``: The Latin (English) tranliteration of the word.

Example Output
~~~~~~~~~~~~~~
    ``GET /api/246763/info``
    ``{
        "id": 246763,
        "orig_form": "example",
        "language": "eng",
        "lang_name": "English",
        "flag_count": 0
    }``