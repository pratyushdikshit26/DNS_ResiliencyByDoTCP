**Evaluating DNS Resiliency and Responsiveness with Truncation, Fragmentation & DoTCP Fallback**

IEEE Transactions on Network and Service Management

Dataset - https://zenodo.org/records/10632827

**Reproducibility**
**1. RIPE Atlas Measurement**
The following tools were developed:

1. The 'measurement' folder includes the main creation of RIPE Atlas measurements using the API
2. The 'database' folder summarizes database functionalities
3. The 'analysis' folder is a collection of useful scripts and functions for the analysis of the results.

To make communication with the RIPE Atlas measurement API easier, the package [ripe.atlas.cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau) is used. For further analysis, especially for the parsing of results, we additionally make use of [ripe.atlas.sagan](https://github.com/RIPE-NCC/ripe-atlas-sagan). The system is designed to work with local SQLite databases ([Python package SQLite3](https://docs.python.org/3/library/sqlite3.html)). For data analysis, we use pandas.



