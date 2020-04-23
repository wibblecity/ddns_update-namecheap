#!/usr/bin/env python3

import sys
import getopt
import string
import urllib.request
import socket
import configparser
import os.path
from os import path
import json
import hashlib
import time
from datetime import timedelta
import random

results_file = "/tmp/ddns.namecheap.json"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_ext_ip():
    api_url = "https://7snwzdghk9.execute-api.eu-west-1.amazonaws.com/production"
    api_data = json.load(urllib.request.urlopen(api_url))
    ext_ip = api_data['ip']
    if socket.inet_aton(ext_ip):
        return ext_ip
    else:
        print("ERROR: Failure occurred when attempting to validate external IP address")
        sys.exit(1)

def get_uptime():
    uptime_seconds = float(time.clock_gettime(time.CLOCK_MONOTONIC))
    return uptime_seconds

def usage(log_string=''):
    sys.stderr.write("\n")
    sys.stderr.write('ERROR: ###### ***** ERROR ***** #####' + "\n")
    sys.stderr.write('ERROR: Message: ' + log_string + "\n")
    sys.stderr.write('ERROR: Usage:' + "\n")
    sys.stderr.write('ERROR:   --config <path to config file>' + "\n")
    sys.stderr.write('ERROR: ###### ***** ERROR ***** #####' + "\n")
    sys.exit(1)

def get_results():
    if os.path.exists(results_file):
        with open(results_file) as json_file:
            results = json.load(json_file)
    else:
        results = {}
    return results

def update_results(node_fqdn,local_ip,ext_ip):
    node_hash = hashlib.md5(str.encode(node_fqdn)).hexdigest()
    results = get_results()
    results[node_hash] = {}
    results[node_hash]['node_fqdn'] = node_fqdn
    results[node_hash]['local_ip'] = local_ip
    results[node_hash]['ext_ip'] = ext_ip
    results[node_hash]['update_time'] = int(time.time())
    results[node_hash]['update_interval'] = int(random.randint((60 * 60 * 24), (60 * 60 * 24 * 2)))
    with open(results_file, 'w') as outfile:
        json.dump(results, outfile)

def check_dns_records(config_file):
    results = get_results()
    config = configparser.RawConfigParser()
    config.read(config_file)
    domain_name = config.get('Main', 'domain_name')
    node_id = config.get('Main', 'node_id')
    password = config.get('Main', 'password')
    node_fqdn = node_id + '.' + domain_name
    node_hash = hashlib.md5(str.encode(node_fqdn)).hexdigest()
    local_ip = get_ip()
    ext_ip = get_ext_ip()
    perform_update = False
    if node_hash not in results:
        perform_update = True
    elif 'update_interval' not in results[node_hash]:
        perform_update = True
    elif results[node_hash]['update_time'] < results[node_hash]['update_interval']:
        perform_update = True
    else:
        if results[node_hash]['local_ip'] != local_ip or results[node_hash]['ext_ip'] != ext_ip:
            perform_update = True
    if perform_update:
        update_dns_records(node_id,domain_name,local_ip,ext_ip,password)
        update_results(node_fqdn,local_ip,ext_ip)

def update_dns_records(a_record,domain_name,local_ip,ext_ip,password):
    print ('Updating DDNS records for: ' + a_record + '.' + domain_name)
    print ('  Local IP: ' + local_ip)
    print ('  External IP: ' + ext_ip)
    update_base_url = "https://dynamicdns.park-your-domain.com/update"
    update_url = update_base_url + "?host=" + a_record + "-int" + "&domain=" + domain_name + "&ip=" + local_ip + "&password=" + password
    urllib.request.urlopen(update_url).read()
    update_url = update_base_url + "?host=" + a_record + "-ext" + "&domain=" + domain_name + "&ip=" + ext_ip + "&password=" + password
    urllib.request.urlopen(update_url).read()

def main(argv):
    character_set = ''
    try:
        opts, args = getopt.getopt( argv, '', [ 'config=' ] )
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt in ("--config"):
            if not path.exists(arg):
                usage('--config <arg> - file does not exist: ' + str(arg))
            else:
                config_file = str(arg)
    if get_uptime() < 60:
        time.sleep(60)
    time.sleep(random.randint(1, 30))
    check_dns_records(config_file)

if __name__ == "__main__":
   main(sys.argv[1:])
