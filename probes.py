import requests as req
import json 
from ripe.atlas.cousteau import (
    AtlasSource,
    ProbeRequest
)
import pandas as pd
import sys

from ripe_wrapper.database.probe_table import ProbeTable

def get_probes_for_different_ip_versions():
    # Number of probes that should be used (out of suited probes retrieved from RA API)
    # Filter for probes that are retrieved from RA API
    # Wanted probes: working V3+ probes at home (not datacenter) which are currently online
    filters = {"tags": "home", "is_anchor": False, "status": 1}    
    exclude_tags = [
        "system-ipv4-doesnt-work",
        "system-anchor",
        "system-v1",
        "system-v2"
    ]
  
    probes = ProbeRequest(**filters)
    ipv4 = []
    ipv4_only = []
    ip_dual = []
    ipv6_only = []
    ip_no = []

    ipv4_string = "prefix_v4"
    ipv6_string = "prefix_v6"
    i = 0
    
    for probe in probes:
        tags = probe["tags"]

        tags_ok = True
        for tag in tags:
            if tag["slug"] in exclude_tags:
                tags_ok = False
                break
        if not tags_ok:
            continue
        if probe['id'] > 1000000:
            continue
        if probe[ipv4_string] is not None and probe[ipv6_string] is not None:
            ip_dual.append(probe)
            ipv4.append(probe)
        else:
            if probe[ipv4_string] is not None:
                ipv4_only.append(probe)  # not ipv6 only -> only ipv4
                ipv4.append(probe)
            elif probe[ipv6_string] is not None:
                ipv6_only.append(probe)
            else:
                ip_no.append(probe)
    # Print total count of found probes
    print("Total with \"home\" tag: " + str(probes.total_count))
    print("Suited (after filtering excluded tags): " + str(sum([len(ip_dual), len(ipv4_only), len(ipv6_only)])))
    print("ip_dual: " + str(len(ip_dual)))
    print("ipv4: " + str(len(ipv4)))
    #ipv4 = random.sample(ipv4, COUNT_OF_IPv4_PROBES)  # cap probes because of limits
    print("ipv4-cap: " + str(len(ipv4)))
    print("ipv4-only: " + str(len(ipv4_only)))
    print("ipv6-only: " + str(len(ipv6_only)))
    print("no-ip: " + str(len(ip_no)))
    return (ipv4, ipv4_only, ipv6_only, ip_dual, ip_no)

def get_source_for_probelist(probes):
    probe_temp = []
    for probe in probes:
        probe_temp.append((str(probe['id'])))

    probes_str = ",".join(probe_temp)

    source = AtlasSource(type="probes",
                            value=probes_str,
                            requested=len(probes)) 
    return source

def get_source_from_probestr(str, count):
    source = AtlasSource(type="probes",
                            value=str,
                            requested=count)  
    return source

def save_probes_to_db(ip_dual, ipv4_only, ipv6_only):
    for probe in ip_dual:
        save_single_probe(probe, True, True)
    for probe in ipv4_only:
        save_single_probe(probe, True, False)
    for probe in ipv6_only:
        save_single_probe(probe, False, True)

def save_single_probe(probe, ipv4_capable, ipv6_capable):
    probe_table = ProbeTable()
    probe_to_save = {
            'id': probe['id'],
            'ipv4_capable': ipv4_capable,
            'ipv6_capable': ipv6_capable
        }
    
    if ipv4_capable:
        probe_to_save['asn_v4'] = probe['asn_v4']
    
    if ipv6_capable:
        probe_to_save['asn_v6'] = probe['asn_v6']

    if 'geometry' in probe.keys():
        geo = probe['geometry']
        if geo is not None and 'coordinates' in geo.keys():
            probe_to_save['longitude'] = geo['coordinates'][0]
            probe_to_save['latitude'] =  geo['coordinates'][1]

    if 'country_code' in probe.keys() and probe['country_code'] is not None:
        probe_to_save['country_code'] = probe['country_code']
        try:
            country_codes = pd.read_csv('./ripe_wrapper/database/country_codes.csv')
            country_code = country_codes[country_codes['Two_Letter_Country_Code'] == probe['country_code']]
            continent_code = country_code['Continent_Code'].to_numpy()[0]
            if pd.isna(continent_code):
                continent_code = "NA"
            probe_to_save['continent_code'] = continent_code        
        except Exception as e:
            print(e)
            print("Could not retrieve continent code")
    probe_table.save_probe(probe_to_save)
    

#(_,v4, v6, dual, _) = get_probes_for_different_ip_versions()
#save_probes_to_db(dual, v4, v6)