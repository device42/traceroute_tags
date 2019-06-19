__author__ = 'Roman Nyschuk'

import os
import sys
import logging
import json
import argparse
from device42 import Device42
import xml.etree.ElementTree as eTree
from xmljson import badgerfish as bf
import time
from traceroute import Tracer
import platform
import socket


logger = logging.getLogger('log')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter('%(asctime)-15s\t%(levelname)s\t %(message)s'))
logger.addHandler(ch)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description="tracert")

parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode - outputs only errors')
parser.add_argument('-c', '--config', help='Config file', default='configuration.xml')
parser.add_argument('-l', '--logfolder', help='log folder path', default='.')


def tracert(ip_address, settings):
    try:
        hop = settings["hop"]["@value"]
    except:
        hop = 2

    try:
        timeout = settings["timeout"]["@value"]
    except:
        timeout = 1000  # 1 second

    tracert_result = False
    last_ip = None
    try:
        logger.info("running traceroute")
        tracer = Tracer(
            dst=ip_address,
            hops=hop,
            timeout=timeout
        )
        tracert_result, last_ip = tracer.run()

        logger.info("finished traceroute.")
    except Exception as e:
        print(str(e))

    return tracert_result, last_ip


def parse_config(url):
    config = eTree.parse(url)
    meta = config.getroot()
    config_json = bf.data(meta)

    return config_json


def task_execute(settings, device42):
    _resource = settings["device42"]

    doql = _resource['@doql']

    logger.info("Getting all ip addresses in D42.")
    sources = device42.doql(query=doql)
    logger.info("Finished getting all ip addresses in D42.")

    run_ip = socket.gethostbyname(socket.gethostname())

    for source in sources:
        if source["ip_address"] is None or source["ip_address"].strip() == "":
            continue
        else:
            ip_address = source["ip_address"]

        ip_id = device42.create_ipaddress(ip_address)
        if ip_id is None:
            logger.info("Can't get id for ip %s." % ip_address)
            continue

        logger.info("Processing ipaddress %s" % ip_address)
        success, last_ip = tracert(ip_address, settings)

        device42.set_ipaddress_custom_field(ip_id, settings["ip-tags"]["@custom-field"], last_ip, run_ip)

        logger.info("finished ipaddress %s" % ip_address)


def main():
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.ERROR)

    try:
        log_file = "%s/d42_tracert_%d.log" % (args.logfolder, int(time.time()))
        logging.basicConfig(filename=log_file)
    except Exception as e:
        print("Error in config log: %s" % str(e))
        return -1

    config = parse_config(args.config)
    logger.debug("configuration info: %s" % (json.dumps(config)))

    settings = config["meta"]["settings"]
    device42 = Device42(settings['device42']['@url'], settings['device42']['@user'], settings['device42']['@pass'])

    print("setting info: %s" % (json.dumps(settings)))
    task_execute(settings, device42)

    print("Completed! View log at %s" % log_file)
    return 0


if __name__ == "__main__":
    system = platform.system().lower()
    if system != 'windows' and system != 'linux':
        print("This script runs on Linux or Windows.")
        sys.exit()
    else:
        print('Running...')
        ret_val = main()
        print('Done')
        sys.exit(ret_val)
