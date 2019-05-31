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
    try:
        logger.info("running traceroute")
        tracer = Tracer(
            dst=ip_address,
            hops=hop,
            timeout=timeout
        )
        tracert_result = tracer.run()

        logger.info("finished traceroute.")
    except Exception as e:
        print(str(e))

    return tracert_result


def parse_config(url):
    config = eTree.parse(url)
    meta = config.getroot()
    config_json = bf.data(meta)

    return config_json


def task_execute(settings, device42):
    _resource = settings["device42"]

    doql = _resource['@doql']

    logger.info("Getting all devices and ip addresses in D42.")
    sources = device42.doql(query=doql)
    logger.info("Finished getting all devices and ip addresses in D42.")
    for source in sources:
        if source["name"] is None:
            device_name = ""
        else:
            device_name = source["name"]
        if source["ip_address"] is None:
            ip_address = ""
        else:
            ip_address = source["ip_address"]
        if source["device_tags"] is None:
            device_tags = ""
        else:
            device_tags = source["device_tags"]
        if source["ipaddress_tags"] is None:
            ipaddress_tags = ""
        else:
            ipaddress_tags = source["ipaddress_tags"]

        logger.info("Processing device %s, ipaddress %s" % (device_name, ip_address))
        if source["device_pk"] is None:
            if "@no-device" in settings["ip-tags"]:
                device42.set_ipaddress_tags(ip_address, ipaddress_tags, settings["ip-tags"]["@no-device"])
        if source["ipaddress_pk"] is None:
            if "@no-ipaddress" in settings["ip-tags"]:
                device42.set_device_tags(device_name, device_tags, settings["device-tags"]["@no-ipaddress"])
        else:
            tracert_result = tracert(ip_address, settings)
            if tracert_result:
                if "@success" in settings["ip-tags"]:
                    device42.set_ipaddress_tags(ip_address, ipaddress_tags, settings["ip-tags"]["@success"])
                if "@success" in settings["device-tags"] and source["device_pk"] is not None:
                    device42.set_device_tags(device_name, device_tags, settings["device-tags"]["@success"])
            else:
                if "@failure" in settings["ip-tags"]:
                    device42.set_ipaddress_tags(ip_address, ipaddress_tags, settings["ip-tags"]["@failure"])
                if "@failure" in settings["device-tags"] and source["device_pk"] is not None:
                    device42.set_device_tags(device_name, device_tags, settings["device-tags"]["@failure"])
        logger.info("finished device %s, ipaddress %s" % (device_name, ip_address))


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
    print('Running...')
    ret_val = main()
    print('Done')
    sys.exit(ret_val)
