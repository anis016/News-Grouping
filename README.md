# Business Data Matching

Implemented a business data matching algorithm on the daily news from various sources by grouping the relevant news together. 
This is based on transitive matching and in the end visualized the results in a suitable manner

### Tools used
1. Python - 3.6
2. MongoDB - 3.2.16
3. Django - 1.11
4. HighChart.JS

### Running the program
1. **`bdm_configurations.json`** file handles the configuration of the program.
2. **`mongo_export.py`** is the mongo listener that crawls the data crawls the data, cleans it and store into new collection set as per `bdm_configurations.json` file.

### Python Librarires
1. `nltk`
2. `BeautifulSoup`
3. `newspaper`