from ripe_wrapper.database.error_table import ErrorTable
from ripe_wrapper.database.database_table import DatabaseTable
from ripe_wrapper.database.txt_result_table import TxtResultTable
import ipaddress
import json 

class ResultTable(DatabaseTable):
    COLUMNS = {
        'rt': 'real', 
        'size': 'integer', 
        'sub_id': 'integer', 
        'sub_max': 'integer',
        'msm_id': 'integer',
        'prb_id': 'integer', 
        'ancount': 'integer', 
        'qdcount': 'integer', 
        'nscount': 'integer', 
        'arcount': 'integer',
        'time': 'integer',
        'qbuf': 'text',
        'abuf': 'text',
        'result_id': 'integer',
        'lts': 'integer',
        'dst_addr': 'text',
        'dst_port': 'integer',
        'src_addr': 'text',
        'af': 'integer',
        'proto': 'text',
        'udp_size': 'integer',
        'return_code': 'text',
        'question_name': 'text'
    }

    FOREIGN_KEYS = '''FOREIGN KEY(msm_id, prb_id) REFERENCES measurement_probes(msm_id, prb_id)'''
    PRIMARY_KEY = 'PRIMARY KEY (sub_id, msm_id, prb_id)'
    TABLE_NAME = 'results'
    UPDATE_TABLES = True

    def save_result(self, original_result, parsed_result):
        if 'result' in original_result:
           self.save_single_result(original_result, parsed_result)
        elif 'resultset' in original_result:
           self.save_result_set(original_result, parsed_result)
        else:  # add result set with error message to db
            self.save_original_result(original_result, parsed_result)

    def exists_result(self, msm_id, prb_id, measurement_detail):
        return False
        sub_id = measurement_detail['subid'] if 'subid' in measurement_detail else 1
        filters = { 'msm_id': msm_id,'prb_id': prb_id, 'sub_id': sub_id}
        return self.exists(filters)

    def save_single_result(self, original_result, parsed_result):
        if self.UPDATE_TABLES and self.exists_result(original_result['msm_id'],original_result['prb_id'], original_result):
                return

        self.add_result_to_db(original_result['msm_id'],
                                            original_result['prb_id'],
                                            original_result,
                                            parsed_result.responses[0],
                                            original_result['result'])


    def save_result_set(self, original_result, parsed_result):
        responses = original_result['resultset']
        if len(responses) == 0:
            return
        if len(responses) > 1:
            meta_responses = []
            for response_i in range(len(responses)):
                try:
                    ip = ipaddress.ip_address(
                        responses[response_i]['dst_addr']) if 'dst_addr' in responses[response_i] else None
                except ValueError:
                    ip = None

                entry = {
                    'i': response_i,
                    'is_private': ip.is_private if ip is not None else False,
                    'af': responses[response_i]['af'] if 'af' in responses[response_i] else 0,
                    'has_rt': 'result' in responses[response_i] and 'rt' in responses[response_i][
                        'result'] and responses[response_i]['result']['rt'] is not None
                }

                meta_responses.append(entry)
            selected_entry = None

            for response_check_local_af_rt in meta_responses:
                if response_check_local_af_rt['af'] == 4 and response_check_local_af_rt['is_private'] and \
                        response_check_local_af_rt['has_rt']:
                    selected_entry = response_check_local_af_rt['i']
                    break

            if selected_entry is None:
                for response_check_local_af in meta_responses:
                    if response_check_local_af['af'] == 4 and response_check_local_af['is_private']:
                        selected_entry = response_check_local_af['i']
                        break

            if selected_entry is None:
                for response_check_af_rt in meta_responses:
                    if response_check_af_rt['af'] == 4 and response_check_af_rt['has_rt']:
                        selected_entry = response_check_af_rt['i']
                        break

            if selected_entry is None:
                for response_check_rt in meta_responses:
                    if response_check_af_rt['has_rt']:
                        selected_entry = response_check_rt['i']
                        break

            if selected_entry is None:
                selected_entry = 0
        else:
            selected_entry = 0

        if self.UPDATE_TABLES and self.exists_result(original_result['msm_id'],
                                                                original_result['prb_id'],
                                                                responses[selected_entry]):
            return

        # add data for resultset to db
        self.add_result_to_db(original_result['msm_id'],
                                    original_result['prb_id'],
                                    responses[selected_entry],
                                    parsed_result.responses[selected_entry],
                                    responses[selected_entry]['result']
                                    if 'result' in responses[selected_entry] else None)

    def save_original_result(self, original_result, parsed_result):
        if self.UPDATE_TABLES and self.exists_result(original_result['msm_id'],
                                                                    original_result['prb_id'],
                                                                    original_result):
            return

        self.add_result_to_db(original_result['msm_id'], original_result['prb_id'], original_result)


    def add_result_to_db(self, measurement_id, probe_id, measurement_detail, parsed_data=None, result_detail=None):
        timestamp = measurement_detail['timestamp'] if 'timestamp' in measurement_detail else None
        timestamp = measurement_detail[
            'time'] if measurement_detail is not None and 'time' in measurement_detail else timestamp

        if timestamp is None:
            print("Fatal: No timestamp found for measurement: ")
            print(measurement_detail)
            print(result_detail)
            raise Exception("No timestamp found for measurement: " + str(measurement_id) + " / " + str(probe_id))

        # noinspection SpellCheckingInspection
        question_wrapper = parsed_data.qbuf if parsed_data else None
        question = question_wrapper.questions[0] if question_wrapper is not None and len(question_wrapper.questions) != 0 else None
        question_name = question.name if question is not None else None 

        qbuf = measurement_detail['qbuf'] if 'qbuf' in measurement_detail else None
        qbuf = result_detail['qbuf'] if result_detail is not None and 'qbuf' in result_detail else qbuf
        error = None
        udp_size = None
        if parsed_data is None or parsed_data.abuf is None:
            # noinspection SpellCheckingInspection
            abuf_parsed = dict.fromkeys(["error"], [measurement_detail['error']])
            err = abuf_parsed['error'][0]
            err_key = list(err.keys())[0]
            error = {
                'error' : err_key,
                'description': err[err_key] 
            }
            print(error)
        else:
            # noinspection SpellCheckingInspection
            abuf_parsed = parsed_data.abuf.raw_data
            if 'EDNS0' in abuf_parsed.keys():
                udp_size = abuf_parsed['EDNS0']['UDPsize']

        qbuf_parsed = None
        if parsed_data is not None and parsed_data.qbuf is not None:
            # noinspection SpellCheckingInspection
            qbuf_parsed = json.dumps(parsed_data.qbuf.raw_data)
            # print("QBUF: " + qbuf_parsed if qbuf_parsed is not None else "No qbuf decoded")
            # print("QBUF native: " + str(qbuf))
        if 'HEADER' in abuf_parsed.keys():
            return_code = abuf_parsed['HEADER']['ReturnCode']
        else: 
            return_code = None
        result = {
            'msm_id': measurement_id,
            'prb_id': probe_id,
            'sub_id': measurement_detail['subid'] if 'subid' in measurement_detail else 1,
            'sub_max': measurement_detail['submax'] if 'submax' in measurement_detail else 1,
            'time': timestamp,
            'lts': measurement_detail['lts'],
            'dst_addr': measurement_detail['dst_addr'] if 'dst_addr' in measurement_detail else
                                (measurement_detail['dst_name'] if 'dst_name' in measurement_detail else None),
            'dst_port': measurement_detail['dst_port'] if 'dst_port' in measurement_detail else 0,
            'af': measurement_detail['af'] if 'af' in measurement_detail else 0,
            'src_addr': measurement_detail['src_addr'] if 'src_addr' in measurement_detail else None,
            'proto': measurement_detail['proto'],
            'qbuf': qbuf,
            'rt': result_detail['rt'] if result_detail is not None else None,
            'size': result_detail['size'] if result_detail is not None else None,
            'abuf': result_detail['abuf'] if result_detail is not None else None,
           # 'error': error,
            'result_id': result_detail['ID'] if result_detail is not None else None,
            'ancount': result_detail['ANCOUNT'] if result_detail is not None else None,
            'qdcount': result_detail['QDCOUNT'] if result_detail is not None else None,
            'nscount': result_detail['NSCOUNT'] if result_detail is not None else None,
            'arcount': result_detail['ARCOUNT'] if result_detail is not None else None,
            'udp_size': udp_size,
            'return_code': return_code,
            'question_name': question_name
        }
        self.add_item(result)
        if error is not None:
            error['msm_id'] = measurement_id
            error['prb_id'] = probe_id
            error['sub_id'] = measurement_detail['subid'] if 'subid' in measurement_detail else 1
            error_table = ErrorTable()
            error_table.add_item(error)

        if result_detail is not None and "answers" in result_detail:
            txtResultTable = TxtResultTable()
            sub_id = measurement_detail['subid'] if 'subid' in measurement_detail else 1
            txtResultTable.add_txt_results(result_detail["answers"], measurement_id, probe_id, sub_id)
        else:
            print("Item has no answer section")