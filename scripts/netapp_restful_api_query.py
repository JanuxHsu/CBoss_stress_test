# ! /usr/bin/env python3
"""
Author: JanuxHsu
"""

import base64
import json
import logging

import os
import requests
import urllib3

urllib3.disable_warnings()


class Restful_API_Handler(object):
    def __init__(self):
        self.port = 443
        self.auth_header = None
        self.cluster = ""
        self.api_user = ""
        self.api_password_env = ""
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_cluster(self, cluster=""):
        self.cluster = cluster

    def set_api_user(self, api_user=""):
        self.api_user = api_user

    def set_api_password_env(self, api_password_env=""):
        self.api_password_env = api_password_env

    def set_port(self, port=443):
        self.port = port

    def _get_baseurl(self):
        return "https://{}:{}".format(self.cluster, self.port)

    def _generate_auth_header(self):
        password = os.getenv(self.api_password_env)
        base64string = base64.encodebytes(('%s:%s' % (self.api_user, password)).encode()).decode().replace('\n', '')

        headers = {
            'authorization': "Basic %s" % base64string,
            'content-type': "application/json",
            'accept': "application/json"
        }

        self.auth_header = headers
        return headers

    def trigger_file_clone(self, volume_uuid=None, source_path="", destination_path=""):
        self._generate_auth_header()

        body = {
            "source_path": source_path,
            "destination_path": destination_path,
            "volume": {
                "uuid": volume_uuid
            }
        }

        url = "{}/api/storage/file/clone".format(self._get_baseurl(), volume_uuid)
        response = requests.post(url, headers=self.auth_header, data=json.dumps(body), verify=False)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json

    def get_job_status(self, job_id=""):
        self._generate_auth_header()
        url = "{}/api/cluster/jobs/{}".format(self._get_baseurl(), job_id)
        response = requests.get(url, headers=self.auth_header, verify=False)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json
