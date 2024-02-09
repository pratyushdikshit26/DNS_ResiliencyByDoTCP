**Evaluating DNS Resiliency and Responsiveness with Truncation, Fragmentation & DoTCP Fallback**

IEEE Transactions on Network and Service Management

Dataset - https://zenodo.org/records/10632827

**Reproducibility**
In order to enable the reproduction of our ﬁndings, we make the raw data of our measurements as well as the analysis scripts and supplementary ﬁles publicly available within this repository.

**1. RIPE Atlas Measurement**
The following tools were developed:

1. The _measurement.py_ and _measurement_table.py_ include the main creation of RIPE Atlas measurements using the API
2. The _database_table.py_ and _probe_table.py_ summarize database functionalities
3. The _plot_util.py_, _file_util.py_ and _db_util.py_ are a collection of useful scripts and functions for the analysis of the results.

To make communication with the RIPE Atlas measurement API easier, the package [ripe.atlas.cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau) is used. For further analysis, especially for the parsing of results, we additionally make use of [ripe.atlas.sagan](https://github.com/RIPE-NCC/ripe-atlas-sagan). The system is designed to work with local SQLite databases ([Python package SQLite3](https://docs.python.org/3/library/sqlite3.html)). For data analysis, we use pandas.

**2. Probe Selection**

To specify the probes that are requested to participate in a measurement, [ripe.atlas.cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau) offers the opportunity to send a list of probe-ids along with the measurement specification itself. _probes.py_ allows retrieval of the probes that have the desired attributes and to store them in a database or their IDs in a _.txt_-file.

**3. Measurement Creation**
_measurements.py_ provides the functionality to create RIPE Atlas measurements. It offers several functions to create different types of measurements, like DNS and Traceroute, and to create the measurement blocks for each of the experiments.

To now start a specific experiment, we first retrieve the probes whose IDs were saved to a _.txt-file_ before and prepare them for sending. We then use the respective functions for assembling and executing one measurement block. By running the script for creating one block multiple times, the measurement series can be created. We started all of the experiments from a machine running Ubuntu 20.04.3.

**4. Results Retrieval**

1. _ripe_results_to_db.ipynb_ provides the functionality to select measurements with a specific tag and store them in a database.
2. _database_table.py_ allows to creation of tables with specified columns and automatically transfers the RIPE Atlas results to SQLite database entries

**CORE DNS Plugins**

[echo](https://github.com/nilsfaulhaber/echo-plugin-for-coredns) and [fallback-monitor](https://github.com/nilsfaulhaber/fallbackmonitor-plugin-for-coredns) plugins firstly retrieve the data from the incoming request by their _ServeDNS_ function. _assembleRR_ is then used in both plugins to realize the encoding of the DNS message alongside the sender’s IP address and the transport protocol that was used. _server.go_ is used to get the information about the used transport protocol. The requests over one protocol are stored in the _context-variables_. It is necessary to add _util.go_ in the _go source_ when the file is added to the repository of _echo_. _MsgAcceptFunc_ is added to leave all requests through to the plugins.

**CONTACTS**

Please feel welcome to contact the authors for further details.

* Pratyush Dikshit (pratyush.dikshit@cispa.de)(corresponding author)
* Mike Kosek (kosek@in.tum.de)
* Nils Faulhaber (n.faulhaber@membrain-it.com)
* Jayasree Sengupta (jayasree.sengupta@cispa.de)
* Vaibhav Bajpai (vaibhav.bajpai@hpi.de)

