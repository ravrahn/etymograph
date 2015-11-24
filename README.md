# Etymograph

For anyone interested in the origin of words, Etymograph is a website and API that shows etymological data in a structured and easy-to-use way.

### Things you'll need to have

* Python 3
* pip for Python 3

### Things you'll need to do
* Clone this repository
* In the root directory, run `pip3 install -r requirements.txt`
* For testing, simply use `python3 api.py` - see [Deploying](#deploying) for a more permanent solution
* Access the site in your browser by navigating to http://localhost:5000/

### Getting Started
* To set up the database, run:
  * `python3 manage.py init`
  * `python3 manage.py migrate`
  * `python3 manage.py upgrade`
* This repository contains an import tool designed to be used with one of the only existing etymological data sets - the [Etymological Wordnet](http://www1.icsi.berkeley.edu/~demelo/etymwn/). To use it, run `python3 manage.py import_tsv <tsv_file>`.
* The database is slow to import _all_ the data, so it's recommended that you take a subset of it. A good one to try for English speakers might be Old, Middle, and Modern English.
* To create this subset, download the etymwn TSV file, and use grep to create a file with only the languages you want (for the Englishes, `(ang|enm|eng):` should do the trick). Then, run the import tool on this file.

### Deploying
* This project is deployed on http://etymograph.com using nginx and uwsgi. If you'd like to do similar, a guide can be found [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04) - but be prepared to troubleshoot.
