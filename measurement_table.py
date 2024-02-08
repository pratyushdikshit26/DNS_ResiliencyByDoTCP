from ripe_wrapper.database.database_table import DatabaseTable
from ripe_wrapper.database.tag_table import TagTable

class MeasurementTable(DatabaseTable):
    COLUMNS = {
        'af': 'integer', 
        'creation_time': 'integer', 
        'description': 'text',
        'group_id': 'integer',
        'id': 'integer PRIMARY KEY',
        'participant_count': 'integer',
        'port': 'integer',
        'probes_requested': 'integer',
        'probes_scheduled': 'integer',
        'protocol': 'text',
        'query_argument': 'text', 
        'query_class': 'text', 
        'query_type': 'text',
        'resolve_on_probe': 'integer',
        'start_time': 'integer', 
        'stop_time': 'integer', 
        'target': 'text',        
        'type': 'text', 
        'udp_payload_size': 'integer', 
        'use_probe_resolver': 'integer'
    }
    TABLE_NAME = "measurements"

    def save_measurement(self, measurement):
        filters = { 'id': measurement['id']}
        if self.exists(filters):
            return 
        self.add_item(measurement)
        tags = measurement['tags']
        tag_table = TagTable()
        for tag in tags:
            tag_table.save_tag(measurement['id'],tag)

