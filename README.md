# Business Data Matching

Research and implement state of the art Data Matching techniques for business relevant data. We propose a business data matching algorithm/system that is based on transitive matching and in the end visualize the results in suitable manner

### Tools used
1. Python - 3.6
2. MongoDB - 3.2.16
3. Django - 1.11
4. D3.JS

### Running the program
1. **`bdm_configurations.json`** file handles the configuration of the program.
2. **`mongo_export.py`** is the mongo listener that crawls the data crawls the data, cleans it and store into new collection set as per `bdm_configurations.json` file.

### Python Librarires

### References
1. Peter Christen. Data Matching Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection.
2. https://en.wikipedia.org/wiki/Fuzzy_matching_(computer-assisted_translation)
3. https://en.wikipedia.org/wiki/Edit_distance
4. Thomas Bocek, Ela Hunt, David Hausheer, Burkhard Stiller. Fast similarity search in peer-to-peer networks.
5. Klaus U. SchulzStoyan Mihov . Levenshtein Automata - Fast string correction with Levenshtein automata.
