from ripe_wrapper.database.database_table import DatabaseTable

class ProbeTable(DatabaseTable):
    COLUMNS = {
        'id': 'integer NOT NULL PRIMARY KEY', 
        'latitude':  'real DEFAULT NULL', 
        'longitude':  'real DEFAULT NULL',
        'country_code': 'text DEFAULT NULL', 
        'continent_code': 'text DEFAULT NULL',
        'ipv4_capable': 'text',
        'ipv6_capable': 'text',
        'asn_v4': 'text',
        'asn_v6': 'text'
    }
    TABLE_NAME = "probes"

    def save_probe(self, probe):
        filters = {'id': probe['id']}
        if self.exists(filters):
            return 
        self.add_item(probe)
    # probe_table = ProbeTable()
    # probe_table.create_table()
