# Etymograph

For anyone interested in the origin of words, Etymograph is a website and API that shows etymological data in a structured and easy-to-use way.

### Things you'll need to have

* Python 3
* pip for Python 3

### Things you'll need to do
* Clone this repository
* In the root directory, run `pip3 install -r requirements.txt`
* To set up the database, run:
  * `python3 manage.py init`
  * `python3 manage.py migrate`
  * `python3 manage.py upgrade`
* This repository contains an import tool designed to be used with an existing etymological data set, the [Etymological Wordnet](http://www1.icsi.berkeley.edu/~demelo/etymwn/). To use this tool, run `python3 manage.py import_tsv <tsv_file>`.
* The database is slow to import _all_ of the data, so you may want to take a subset of it. A good one to try is all of Old, Middle, and Modern English - about a million lines in total.
* To create this subset, download the etymwn TSV file, and use grep to create a file with only the languages you want (for the Englishes, `(ang|enm|eng):` should do the trick). Then, run the import tool on this file.
* For testing, simply use `python3 app.py`

### Deploying
* The server will run at http://localhost:5000/ by default.
* This project is deployed on http://etymograph.com using nginx and uwsgi. If you'd like to do similar, a guide can be found [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04) - but be prepared to troubleshoot.
