#!/usr/bin/python2.7

import sys
import getopt
import string
import urllib
import socket
import ConfigParser
import os.path
from os import path

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

def usage(log_string=''):
    sys.stderr.write("\n")
    sys.stderr.write('ERROR: ###### ***** ERROR ***** #####' + "\n")
    sys.stderr.write('ERROR: Message: ' + log_string + "\n")
    sys.stderr.write('ERROR: Usage:' + "\n")
    sys.stderr.write('ERROR:   --config <path to config file>' + "\n")
    sys.stderr.write('ERROR: ###### ***** ERROR ***** #####' + "\n")
    sys.exit(1)

def update_dns_records(config_file):
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    domain_name = config.get('Main', 'domain_name')
    node_id = config.get('Main', 'node_id')
    password = config.get('Main', 'password')
    update_base_url = "https://dynamicdns.park-your-domain.com/update"
    node_a_record_int = node_id + "-int"
    node_a_record_ext = node_id + "-ext"
    my_local_ip = get_ip()
    web_page = urllib.urlopen("http://iptools.bizhat.com/ipv4.php")
    my_ext_ip = web_page.read()
    update_url = update_base_url + "?host=" + node_a_record_int + "&domain=" + domain_name + "&ip=" + my_local_ip + "&password=" + password
    urllib.urlopen(update_url).read()
    update_url = update_base_url + "?host=" + node_a_record_ext + "&domain=" + domain_name + "&ip=" + my_ext_ip + "&password=" + password
    urllib.urlopen(update_url).read()

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

if __name__ == "__main__":
   main(sys.argv[1:])
