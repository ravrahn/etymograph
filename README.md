# Etymograph

For anyone interested in the origin of words, Etymograph is a website and API that shows etymological data in a structured and easy-to-use way.

#### Things you'll need to have

* A UNIX system
* Python 3 and pip for Python 3
* [Neo4j community edition](http://neo4j.com/download/) (optional)

### Things you'll need to do
* Clone this repository
* In the root directory, run `pip3 install -r requirements.txt`
* You'll need to add authentication for etymograph.com's instance of neo4j to your shell's environment - or run your own.
* For testing, simply use `python3 api.py` - see [Deploying](#deploying) for a more permanent solution
* Access the site in your browser by navigating to http://localhost:5000/

### Creating your own neo4j instance
* Once neo4j is installed, you're already done - neo4j doesn't have a formal predefined schema. It should be running on port 7474. You can use your browser to do basic interactions by navigating to http://localhost:7474/
* This repository contains an import tool designed to be used with one of the only existing etymological data sets - the [Etymological Wordnet](http://www1.icsi.berkeley.edu/~demelo/etymwn/).
* The neo4j database is very, very slow to search when dealing with _all_ the data, so it's recommended that you take a subset of it. A good one to try is the three forms of English - old, middle, and modern.
* To create this subset, download the etymwn TSV file, and use grep to create a file with only the languages you want (for the Englishes, `(ang|enm|eng):` should do the trick). Then, run `./import_tsv.py <file>`
  * Note: The import tool currently outputs a words.csv file where every element is duplicated. It's a good idea to run `sort | uniq` on the output, but remember to move the header line back to the top after (it typically moves to the bottom)
* Once that's done, you can use the [neo4j import tool](http://neo4j.com/docs/stable/import-tool.html) to import the two CSV files created to your database.

### Deploying
* This project is deployed on http://etymograph.com using nginx and uwsgi. If you'd like to do similar, a guide can be found [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04) - but be prepared to troubleshoot.
