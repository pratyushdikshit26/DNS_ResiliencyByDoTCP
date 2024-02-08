import json
import os.path as path
import random
import time
from datetime import datetime
from .resolvers import RESOLVER_NAMES
from ripe.atlas.cousteau import (
    Dns,
    Traceroute,
    AtlasCreateRequest
)
import pandas as pd 
import ipaddress
from ripe_wrapper.measurements.probes import *
from ripe_wrapper.measurements.resolvers import RESOLVER_ADDRESSES

class MeasurementManager:
    # ATLAS_API_KEY is the id entification for the RA API
    #key = '17302f34-f016-4dcb-ac1f-fb70f43cb1d5' # Simon Huber
    key = '3232579d-97a3-43a5-972f-5e9cc113e3bc' # Nils Faulhaber
    #key = 'a937c181-8f1a-42ad-ab87-f843757f1937' # unknown, higher credit limit 
    ATLAS_API_KEY = key 
    # Directory of the domain composition files
    DOMAIN_COMPOSITION_DIR = './domain_composition/'
    # Destination of the measurement staging responses
    MEASUREMENT_STAGING_RESPONSE_DIR = './measurement_request_responses_q1-test7/'
    
    measurement_counter = 0 
    start_time = -1 
    measurement_name = ""
    entries_per_post_request = 1
    delay_between_measurement_posts = 1

    def __init__(self, measurement_name, delay_between_measurement_posts = 1, entries_per_post_request = 1, start_time = -1, measurement_count = 0):
        self.measurement_name = measurement_name
        self.delay_between_measurement_posts = delay_between_measurement_posts
        self.entries_per_post_request = entries_per_post_request
        self.start_time = start_time
        self.measurement_counter = measurement_count

    def create_traceroute_measurement(self, is_v4, target):
        af = 4 if is_v4 else 6

        tag = f"traceroute-{'ipv4' if is_v4 else 'ipv6'}"
        tags=[self.measurement_name, tag]
    
        description = f"Traceroute/{'IPv4/4' if is_v4 else 'IPv6/6'}/{self.measurement_name}/target:{target}" 
         
        return Traceroute(af=af,
                    target=target ,
                    protocol='ICMP', 
                    max_hops=30,
                    is_public=True,
                    tags=tags,
                    description=description)


    def create_dns_measurement(self, is_v4, is_udp, use_probe_resolver,target, resolver_ip="", resolver_name="", query_type="A", prepend_probe_id=False):
        protocol = "UDP" if is_udp else "TCP"
        af = 4 if is_v4 else 6

        tag = f"{'dns-' if use_probe_resolver else 'dns-probes'}-{'ipv4' if is_v4 else 'ipv6'}-{'udp' if is_udp else 'tcp'}{'-probe-resolver' if use_probe_resolver else ''}"
        tags=[self.measurement_name, tag]
        
        description = f"DNS/{'IPv4/4' if is_v4 else 'IPv6/6'}/{self.measurement_name}/{protocol}/res:{'probe' if use_probe_resolver else resolver_ip}/target:{target}" 
        if(not use_probe_resolver):
            tags.append("dns-target-" + resolver_name)
        req_target = None if use_probe_resolver else resolver_ip
        return Dns(af=af,
                    udp_payload_size=4096,  # (default=512, 1232 flag day recommendation)
                    use_probe_resolver=use_probe_resolver,  # (default=False)
                    target=req_target ,
                    protocol=protocol,  # (default="UDP")
                    include_qbuf=True,  # (default=False)
                    include_abuf=True,  # (default=True)    
                    query_class="IN",  # (default="IN")
                    query_argument=target,
                    query_type=query_type,
                    is_public=True, 
                    set_rd_bit=True,
                    prepend_probe_id=prepend_probe_id,  # prevent caching
                    tags=tags,
                    description=description)

    def assemble_measurements(self, is_v4, domains, resolver_names):
        # Create measurements
        measurements = []
    
        # Create all measurements for resolver
        for target in domains:
            for resolver in resolver_names.keys():
                use_probe_resolver = False
                for is_udp in [True, False]:
                    resolver_ip = resolver_names[resolver][0] if is_v4 else resolver_names[resolver][1]
                    measurements.append(self.create_dns_measurement(is_v4, is_udp, use_probe_resolver, target, resolver_ip=resolver_ip ,resolver_name=resolver))
                print(f"Created all measurements for resolver {resolver} and target {target}")
            print(f"Created udp/tcp measurement for {target}")
    
        # Create measurements for probe resolvers (use_probe_resolver=True)
        for target in domains:
            use_probe_resolver = True
            for is_udp in [True, False]:
                measurements.append(self.create_dns_measurement(is_v4, is_udp, use_probe_resolver, target))
        print(f"Total measurements: {len(measurements)}")
        return measurements

    def assemble_txt_measurements(self, is_v4, domains, resolver_names):
        # Create measurements
        measurements = []
    
        # Create all measurements for resolver
        for target in domains:
            for resolver in resolver_names.keys():
                use_probe_resolver = False
                for is_udp in [True, False]:
                    resolver_ip = resolver_names[resolver][0] if is_v4 else resolver_names[resolver][1]
                    measurements.append(self.create_dns_measurement(is_v4, is_udp, use_probe_resolver, target, resolver_ip=resolver_ip ,resolver_name=resolver, query_type='TXT', prepend_probe_id=True))
                print(f"Created all measurements for resolver {resolver} and target {target}")
            print(f"Created udp/tcp measurement for {target}")
            
        use_probe_resolver = True
        for is_udp in [True, False]:
            measurements.append(self.create_dns_measurement(is_v4, is_udp, use_probe_resolver, target, query_type='TXT', prepend_probe_id=True))
        return measurements

    def assemble_aaaa_measurements(self, is_v4, domains, resolver_names):
        # Create measurements
        measurements = []
    
        # Create all measurements for resolver
        for domain in domains:
            for resolver in resolver_names.keys():
                use_probe_resolver = False
                target = f"{self.measurement_counter}.{domain}"
                self.measurement_counter += 1
                resolver_ip = resolver_names[resolver][0] if is_v4 else resolver_names[resolver][1]
                measurements.append(self.create_dns_measurement(is_v4, True, use_probe_resolver, target, resolver_ip=resolver_ip ,resolver_name=resolver, query_type='AAAA', prepend_probe_id=True))
                print(f"Created all measurements for resolver {resolver} and target {domain}")
            print(f"Created udp/tcp measurement for {domain}")
            
        use_probe_resolver = True
        target = f"{self.measurement_counter}.{domain}"
        self.measurement_counter += 1
        measurements.append(self.create_dns_measurement(is_v4, True, use_probe_resolver, target, query_type='AAAA', prepend_probe_id=True))
        return measurements

    def assemble_traceroute_measurements_probe_resolver(self):
        probe_to_resolvers = pd.read_csv('prb_to_resolver.csv').to_dict('records')
        measurements_for_probe_id = []
        for item in probe_to_resolvers:
            if item['dst_addr'] in RESOLVER_ADDRESSES:
                print(f"Skipping known public resolver {item['dst_addr']}")
                continue
            addr = ipaddress.ip_address(item['dst_addr'])
            if addr.is_private:
                print(f"Skipping private IP address {addr}")
            if addr.version == 4:
                measurements_for_probe_id.append((self.create_traceroute_measurement(True, item['dst_addr']), item['prb_id']))
            else:
                measurements_for_probe_id.append((self.create_traceroute_measurement(False, item['dst_addr']), item['prb_id']))
        return measurements_for_probe_id


    def assemble_traceroute_measurements(self, is_v4, resolver_names):
        measurements = []
        for resolver in resolver_names.keys():
            resolver_ip = resolver_names[resolver][0] if is_v4 else resolver_names[resolver][1]
            measurements.append(self.create_traceroute_measurement(is_v4, resolver_ip))
        return measurements

    def execute_measurements(self, measurements, source):
        # Split measurement array and submit measurements to RA API
        for i in range(len(measurements)):
            measurement_to_send = measurements[i]

            measurement_description = f"Sending measurement {i}: {measurement_to_send.description}"
            if self.entries_per_post_request == 1:
                measurement_description += f" msm: {measurement_to_send.description}"
            print(str(measurement_description))

            with open('timing_test.csv', 'a') as the_file:
                the_file.write(f'{measurement_to_send.description},{datetime.utcnow()}\n')
        
            atlas_request = AtlasCreateRequest(
                key=self.ATLAS_API_KEY,
                measurements=[measurement_to_send],
                sources=[source],
                is_oneoff=True
            )

            # Access private property of atlas_request class in order to check payload size.
            # Too large payloads are not accepted by webserver of RA (default apache settings)
            atlas_request._construct_post_data()
            request_data = atlas_request.post_data
            print("atlas_request size of post-data: " + str(len(json.dumps(request_data))))

            (is_success, response) = atlas_request.create()

            self.log_results(is_success, response, i)
            if self.delay_between_measurement_posts > 0:
                print(f"Delaying next post by {self.delay_between_measurement_posts} seconds")
                time.sleep(self.delay_between_measurement_posts)




    def log_results(self, is_success, response, i):
        # Save response to file for debugging purposes
        with open('results/response_' + self.measurement_name + '_ipv4_' + str(i) + '-' + str(
                i + self.entries_per_post_request) + ('_failed' if is_success is False else '') + '.txt',
                    'w', newline='\n') as out_file:
            str_response = response
            try:
                str_response = json.dumps(response)
            except TypeError:
                print("not json -> skip json.dumps")

            out_file.write(str_response)

        if is_success is not True:
            print("ERROR: Request Failed")

