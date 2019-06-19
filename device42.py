# -*- coding: utf-8 -*-


import os
import requests

requests.packages.urllib3.disable_warnings()


class Device42BaseException(Exception):
    pass


class Device42BadArgumentError(Exception):
    pass


class Device42HTTPError(Device42BaseException):
    pass


class Device42WrongRequest(Device42HTTPError):
    pass


class Device42(object):
    def __init__(self, endpoint, user, password, **kwargs):
        self.base = endpoint
        self.user = user
        self.pwd = password
        self.verify_cert = False
        self.debug = kwargs.get('debug', False)
        self.logger = kwargs.get('logger', None)
        self.base_url = "%s" % self.base
        self.headers = {}

    def _send(self, method, path, data=None):
        """ General method to send requests """
        url = "%s/%s" % (self.base_url, path)
        params = None
        if method == 'GET':
            params = data
            data = None
        resp = requests.request(method, url, data=data, params=params,
                                auth=(self.user, self.pwd),
                                verify=self.verify_cert, headers=self.headers)
        if not resp.ok:
            raise Device42HTTPError("HTTP %s (%s) Error %s: %s\n request was %s" %
                                    (method, path, resp.status_code, resp.text, data))
        retval = resp.json()
        return retval

    def _get(self, path, data=None):
        return self._send("GET", path, data=data)

    def _post(self, path, data):
        if not path.endswith('/'):
            path += '/'
        return self._send("POST", path, data=data)

    def _put(self, path, data):
        if not path.endswith('/'):
            path += '/'
        return self._send("PUT", path, data=data)

    def _delete(self, path):
        return self._send("DELETE", path)

    def _log(self, message, level="DEBUG"):
        if self.logger:
            self.logger.log(level.upper(), message)

    def get_device_by_name(self, name):
        path = "api/1.0/devices/name/%s" % name
        return self._get(path)

    def set_device_tags(self, device_name, original_tags, tags):
        path = "api/1.0/devices/"
        new_tags = original_tags
        if new_tags is None or new_tags == "":
            new_tags = tags
        else:
            new_tags += ", " + tags
        params = {"name": device_name, "tags": new_tags}
        try:
            ret = self._post(path, params)
            if ret["code"] == 0:
                return True
        except:
            pass
        return False

    def set_ipaddress_tags(self, ipaddress, original_tags, tags):
        path = "api/1.0/ips/"
        new_tags = original_tags
        if new_tags is None or new_tags == "":
            new_tags = tags
        else:
            new_tags += ", " + tags
        params = {"ipaddress": ipaddress, "tags": new_tags}
        try:
            ret = self._post(path, params)
            if ret["code"] == 0:
                return True
        except:
            pass
        return False

    def set_ipaddress_custom_field(self, ip_id, custom_field, value, notes):
        path = "api/1.0/custom_fields/ip_address/"

        params = {"id": ip_id, "key": custom_field, "value": value,
                  "notes": notes}
        try:
            ret = self._put(path, params)
            if ret["code"] == 0:
                return True
        except Exception as e:
            print(str(e))
            pass
        return False

    def doql(self, url=None, query=None):
        if url is None:
            url = "services/data/v1.0/query/"
        path = url
        if query is None:
            query = "select distinct view_ipaddress_v1.ipaddress_pk, view_ipaddress_v1.ip_address from view_device_v1 left join view_ipaddress_v1 on view_device_v1.device_pk = view_ipaddress_v1.device_fk"

        data = {"output_type": "json", "query": query}

        result = self._post(path, data)
        return result

    def create_ipaddress(self, ip_address):
        path = "api/1.0/ips/"

        data = {"ipaddress": ip_address}

        try:
            ret = self._post(path, data)
            if ret["code"] == 0:
                return ret["msg"][1]
            return None
        except:
            return None

    def find_ipaddress(self, ip_address):
        path = "api/1.0/ips/"

        data = {"ip": ip_address}

        try:
            ret = self._get(path, data)
            if ret["total_count"] > 0:
                return ret["ips"][0]["id"]
            return None
        except:
            return None
