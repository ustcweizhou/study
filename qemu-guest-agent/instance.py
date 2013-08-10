﻿
import helper
import json
import os
import requests


"""
Data structure of instances cache:
{
    "uuid1": {
        "name1": "instance-name1",
        "domain1": "domain-in-libvirt",
        "last_heartbeat": "123457890",
        "last_monitor": "1235680",
        "temp": {
            'total_cpu_time': 0,
            'last_cpu_idle_time': 0,
            'disk_read_request': 0,
            'disk_write_request': 0,
            'disk_read': 0,
            'disk_write': 0,
            'disk_read_delay': 0,
            'disk_write_delay': 0,
            'network_receive_bytes': 0,
            'network_transfer_bytes': 0,
            'disk_partition_info': {

            },
            'timestamp': 0
        }
    },

}
"""

instances_path = "/var/lib/nova/instances/"
# libvirt_libdir = "/var/lib/libvirt/qemu/"
TOKEN = None
TENANT_ID = None

auth_url = "http://127.0.0.1:5000/v2.0/tokens"
api_url_prefix = "http://localhost:8774/v2/"

def _get_token():
    global TOKEN
    global TENANT_ID
    data = {"auth": {"tenantName": "admin",
                     "passwordCredentials":
                            {"username": "admin",
                             "password": "admin"}}}
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(auth_url, data=json.dumps(data), headers=headers)
        TOKEN = r.json()['access']['token']['id']
        TENANT_ID = r.json()['access']['token']['tenant']['id']
        print "get token: %s, belong to tenant: %s" % (TOKEN, TENANT_ID)
    except (TypeError, KeyError, ValueError) as e:
        print "get token error, exception: %s" % e
        TOKEN = None
        TENANT_ID = None


# get instances running on this host
def get_all_instances_on_host():
    global TOKEN
    global TENANT_ID

    retry = 0
    while retry < 2:
        if TOKEN is None or TENANT_ID is None:
            _get_token()

        headers = {"Accept": "application/json", "X-Auth-Token": TOKEN}
        params = {"all_tenants": 1, "host": "114-113-199-8"}
        api_url = api_url_prefix + TENANT_ID + "/servers/detail"

        try:
            r = requests.get(api_url, params=params, headers=headers, timeout=3)
            if r.status_code == 413:
                retry += 1
                _get_token()
            elif r.status_code == 200:
                servers = r.json()["servers"]
                # print "-------\n%s\n------" % servers
                # print "url: %s" % r.url
                return servers
            else:
                print "get instances error, code: %s" % r.status_code
                return []
        except Exception as e:
            print "get instances error, exception: %s" % e
            return []
