# Etymograph #

> For anyone interested in the origin of words, Etymograph is a website and API that shows etymological data in a structured and easy-to-use way.

### Setup ###

#### Dependencies ####

* Install Python 3
* Install [neo4j community edition](http://neo4j.com/download/)
* Clone this repository
* In the root directory, run ```pip3 install -r requirements.txt```

### Import and Running ###
#### Before importing, you'll need to run neo4j ####

   * In the neo4j folder you decompressed, run ```bin/neo4j start``` (If that doesn't work, try ```bin/neo4j start-no-wait```)
   * By default you may access the server at localhost:7474; access this via your browser and follow the prompts to login
   * In api.py, add ```authenticate('localhost:7474', <your username>, <your password>)``` with your appropriate credentials from the last step. 
   * lastly, depending on where you cloned this repo, you'll need to run ```/path/to/cloned/repo/etymograph/import_tsv.py <tsv file>``` replacing <tsv file> with whatever tsv you are looking to import into the database.
   * Running the flask instance is as easy as running ```python3 api.py```

### TODO: ###

* Database configuration
* How to run tests
* Deployment instructions
