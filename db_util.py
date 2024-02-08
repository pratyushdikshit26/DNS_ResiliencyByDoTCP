import pandas as pd 
import sqlite3 


class DatabaseReader:
    DATABASE_PATH = ""

    def __init__(self, db_path):
        self.DATABASE_PATH = db_path
        self.conn = sqlite3.connect(db_path)


    def get_top_ases(self):
        query = """SELECT count(*) as count, asn_v4, name FROM (SELECT * FROM probes p, results r WHERE p.id = r.prb_id GROUP BY p.id) t, autonomous_systems a 
                    WHERE a.number = t.asn_v4 GROUP BY asn_v4 ORDER BY count DESC"""

        results = pd.read_sql(query, self.conn).head(10)
        results = results[["asn_v4", "name"]]
        return results.values

    def select_runtime_data(self, ip_version, proto):
        """Select all results for the given ip_version and protocol that did not result in an error (rt != None).
           Joined with probe and autonomous_system information. Returns pd.DataFrame"""

        results = pd.read_sql(f"""SELECT rt, m.use_probe_resolver, r.prb_id, continent_code, dst_addr, p.asn_v4 as asn, a.name as_name, r.msm_id, r.sub_id
                                from probes p, results r, measurements m, autonomous_systems a 
                                WHERE p.id = r.prb_id and
                                        r.msm_id = m.id and 
                                        r.af = {ip_version} and 
                                        r.proto='{proto}'  and 
                                        p.asn_v4 = a.number and
                                        r.rt != 'None'""", self.conn) 
        return results
    
    def select_failure_data(self, ip_version, proto):
        """Select all results for the given ip_version and protocol with (if the case) their error information.
           Joined with probe and autonomous_system information. Returns pd.DataFrame"""

        results = pd.read_sql(f"""SELECT r.rt,  r.prb_id, r.dst_addr, r.proto,
                                         p.continent_code, p.asn_v4 as asn, 
                                         a.name as_name, 
                                         m.use_probe_resolver,
                                         e.error, e.description as error_detail
                                  from probes p 
                                  JOIN results r ON p.id = r.prb_id 
                                  JOIN measurements m ON r.msm_id = m.id 
                                  JOIN autonomous_systems a ON p.asn_v4 = a.number 
                                  LEFT JOIN errors e ON e.prb_id = r.prb_id and 
                                                        e.msm_id = r.msm_id
                                  WHERE r.af = {ip_version} and 
                                        r.proto='{proto}'""", self.conn)
        return results

    def select_traceroute_data(self, ip_version):
        """Select the results of the last hop of each traceroute result for the given ip_version. 
            Joined with probe and autonomous system data. Returns pd.DataFrame"""

        results = pd.read_sql(f"""SELECT max(r.hop) as hops, d.rtt, r.dst_addr, r.af, r.prb_id, r.msm_id,
                                         p.continent_code, p.asn_v4 as asn, 
                                         a.name as_name
                                  FROM hop_results r 
                                  JOIN hop_result_details d ON r.msm_id = d.msm_id and 
                                                               r.prb_id = d.prb_id and 
                                                               r.hop = d.hop 
                                  JOIN measurements m ON m.id = r.msm_id 
                                  JOIN probes p ON p.id = r.prb_id 
                                  JOIN autonomous_systems a ON a.number = p.asn_v4
                                  WHERE m.af = {ip_version} and 
                                        proto = 'ICMP' 
                                  GROUP BY r.prb_id, r.msm_id""", self.conn)
        return results

    def select_buffersize_data(self, ip_version):
        """Select the results of the last hop of each traceroute result for the given ip_version. 
            Joined with probe and autonomous system data. Returns pd.DataFrame"""

        results = pd.read_sql(f"""SELECT r.rt, r.proto, r.udp_size,  r.prb_id,  r.dst_addr, 
                                         p.continent_code, p.asn_v4 as asn, 
                                         a.name as_name,
                                         m.use_probe_resolver
                                  FROM probes p, results r, measurements m, autonomous_systems a 
                                  WHERE p.id = r.prb_id and
                                        r.msm_id = m.id and 
                                        r.af = {ip_version} and 
                                        p.asn_v4 = a.number""", self.conn) 
        return results

    def get_edns_option_data(self, version):
        """Select the detailed results of the echoed requests including pseudosection (edns) results ip_version.
            Joined with probe and autonomous system data. Returns pd.DataFrame"""
        df_results = pd.read_sql(f"""SELECT r.msm_id, r.prb_id, r.sub_id, r.rt, r.dst_addr, 
                                        p.name, p.content,
                                        m.use_probe_resolver,
                                        t.flags, t.header, t.udp_size, t.backend_resolver, t.question,
                                        pr.asn_v4, pr.continent_code, pr.country_code,
                                        a.number, a.name as as_name
                                 from measurements m 
                                 JOIN results r ON m.id = r.msm_id 
                                 LEFT JOIN txt_results t ON t.prb_id = r.prb_id and 
                                                            t.msm_id = r.msm_id and 
                                                            t.sub_id = r.sub_id 
                                 LEFT JOIN pseudosection_results p ON t.prb_id = p.prb_id and 
                                                                      t.msm_id = p.msm_id and 
                                                                      t.sub_id = p.sub_id 
                                 JOIN probes pr ON r.prb_id = pr.id
                                 JOIN autonomous_systems a ON a.number = pr.asn_v4
                                 WHERE r.af = {version} and r.rt != 'None'""", self.conn)
        return df_results


    def get_buffersize_data_txt_results(self, version):
        df_results = pd.read_sql(f"""SELECT r.msm_id, r.prb_id, r.sub_id, r.rt, r.dst_addr, r.udp_size as frontend_udp_size, r.proto as proto,
                                        m.use_probe_resolver,
                                        t.flags, t.header, t.udp_size as backend_udp_size, t.proto as backend_proto, t.backend_resolver, t.question,
                                        pr.asn_v4, pr.continent_code, pr.country_code,
                                        a.number, a.name as as_name
                                 from measurements m
                                 JOIN results r ON m.id = r.msm_id
                                 LEFT JOIN txt_results t ON t.prb_id = r.prb_id and
                                                            t.msm_id = r.msm_id and
                                                            t.sub_id = r.sub_id
                                  JOIN probes pr ON r.prb_id = pr.id
                                  JOIN autonomous_systems a ON a.number = pr.asn_v4
                                WHERE r.af = {version}""",self.conn)
        return df_results

