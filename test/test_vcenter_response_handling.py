import datetime
import json
import jsonschema
import os
import random
import string
import tempfile
import time
from pyVmomi import vim
from unittest.mock import patch
from unittest.mock import MagicMock
import pytest
import vcenter_info
from vcenter_info import vcenter
from vcenter_info import api

VERSION_RESPONSE_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'type': 'object',
    'properties': {
        'api': {'type': 'string'},
        'module': {'type': 'string'}
    },
    'required': ['api', 'module'],
    'additionalProperties': False

}
VMLIST_SCHEMA = {
    '$schema': 'http://json-schema.org/draft-07/schema#',

    'definitions': {
        'stats': {
            'type': 'object',
            'properties': {
                'balloonedMemory': {'type': 'integer', 'minimum': -1},
                'compressedMemory': {'type': 'integer', 'minimum': -1},
                'consumedOverheadMemory': {'type': 'integer', 'minimum': -1},
                'distributedCpuEntitlement': {'type': 'integer', 'minimum': -1},
                'distributedMemoryEntitlement': {
                    'type': 'integer', 'minimum': -1},
                'ftLatencyStatus': {'type': 'string'},
                'ftLogBandwidth': {'type': 'integer', 'minimum': -1},
                'ftSecondaryLatency': {'type': 'integer', 'minimum': -1},
                'guestHeartbeatStatus': {'type': 'string'},
                'guestMemoryUsage': {'type': 'integer', 'minimum': -1},
                'hostMemoryUsage': {'type': 'integer', 'minimum': -1},
                'overallCpuDemand': {'type': 'integer', 'minimum': -1},
                'overallCpuUsage': {'type': 'integer', 'minimum': -1},
                'privateMemory': {'type': 'integer', 'minimum': -1},
                'sharedMemory': {'type': 'integer', 'minimum': -1},
                'ssdSwappedMemory': {'type': 'integer', 'minimum': -1},
                'staticCpuEntitlement': {'type': 'integer', 'minimum': -1},
                'staticMemoryEntitlement': {'type': 'integer', 'minimum': -1},
                'swappedMemory': {'type': 'integer', 'minimum': -1},
                'uptimeSeconds': {'type': 'integer', 'minimum': -1}
            },
            'required': [
                'balloonedMemory',
                'compressedMemory',
                'consumedOverheadMemory',
                'distributedCpuEntitlement',
                'distributedMemoryEntitlement',
                'ftLatencyStatus',
                'ftLogBandwidth',
                'ftSecondaryLatency',
                'guestHeartbeatStatus',
                'guestMemoryUsage',
                'hostMemoryUsage',
                'overallCpuDemand',
                'overallCpuUsage',
                'privateMemory',
                'sharedMemory',
                'ssdSwappedMemory',
                'staticCpuEntitlement',
                'staticMemoryEntitlement',
                'swappedMemory',
                'uptimeSeconds'
            ],
            'additionalProperties': False
        },
        'vm': {
            'type': 'object',
            'properties': {
                'annotation': {'type': 'string'},
                'boot': {'type': ['string', 'null']},
                'datacenter': {'type': 'string'},
                'guest': {'type': 'string'},
                'ip': {'type': ['string', 'null']},
                'name': {'type': 'string'},
                'path': {'type': 'string'},
                'question': {'type': ['string', 'null']},
                'san': {'type': ['string', 'null']},
                'state': {'type': 'string'},
                'stats': {'$ref': '#/definitions/stats'}
            },
            'required': [
                'annotation', 'datacenter', 'guest',
                'ip', 'name', 'path', 'question',
                'san', 'state', 'stats'],
            'additionalProperties': False
        }
    },

    'type': 'array',
    'items': {'$ref': '#/definitions/vm'}

}


@pytest.fixture
def client():
    def _dc():
        return {
            'hostname': _random_string(20),
            'username': _random_string(20),
            'password': _random_string(20)
        }

    config_params = {
        "cache": {"filename": None},
        "auth": [_dc() for _ in range(10)]
    }

    with tempfile.NamedTemporaryFile() as cache_file:
        config_params['cache']['filename'] = cache_file.name
        # the file won't exist when used ...

    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(json.dumps(config_params).encode('utf-8'))
        config_file.flush()
        os.environ['CONFIG_FILENAME'] = config_file.name
        with vcenter_info.create_app().test_client() as c:
            yield c


@pytest.fixture
def dummy_json_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(json.dumps({'a': 1}).encode('utf-8'))
        f.flush()
        yield f.name


class Object(object):
    pass


def _random_string(num, letters=string.printable):
    return ''.join(random.choice(letters) for _ in range(num))


def _random_vm_spec():
    return {
        'annotation': _random_string(100),
        'datacenter': _random_string(15),
        'guest': _random_string(15),
        'ip': _random_string(20),
        'name': _random_string(20),
        'path': '[' + _random_string(10) + '] ' + _random_string(40),
        'question': _random_string(40),
        'state': _random_string(10)
    }


def mocked_vm(spec=None):
    """
    basically the reverse of vcenter.vm_to_dict
    """
    if not spec:
        spec = _random_vm_spec()

    v = MagicMock(spec=vim.VirtualMachine)
    v.summary = Object()

    v.summary.config = Object()
    v.summary.config.name = spec['name']
    v.summary.config.vmPathName = spec['path']
    v.summary.config.guestFullName = spec['guest']
    v.summary.config.annotation = spec['annotation']

    v.summary.runtime = Object()
    v.summary.runtime.bootTime = datetime.datetime.now()
    v.summary.runtime.powerState = spec['state']
    v.summary.runtime.question = Object()
    v.summary.runtime.question.text = spec['question']

    v.summary.guest = Object()
    v.summary.guest.ipAddress = spec['ip']

    v.summary.quickStats = Object()
    v.summary.quickStats.balloonedMemory = -1
    v.summary.quickStats.compressedMemory = -1
    v.summary.quickStats.consumedOverheadMemory = -1
    v.summary.quickStats.distributedCpuEntitlement = -1
    v.summary.quickStats.distributedMemoryEntitlement = -1
    v.summary.quickStats.ftLatencyStatus = Object()
    v.summary.quickStats.ftLogBandwidth = -1
    v.summary.quickStats.ftSecondaryLatency = -1
    v.summary.quickStats.guestHeartbeatStatus = Object()
    v.summary.quickStats.guestMemoryUsage = -1
    v.summary.quickStats.hostMemoryUsage = -1
    v.summary.quickStats.overallCpuDemand = -1
    v.summary.quickStats.overallCpuUsage = -1
    v.summary.quickStats.privateMemory = -1
    v.summary.quickStats.sharedMemory = -1
    v.summary.quickStats.ssdSwappedMemory = -1
    v.summary.quickStats.staticCpuEntitlement = -1
    v.summary.quickStats.staticMemoryEntitlement = -1
    v.summary.quickStats.swappedMemory = -1
    v.summary.quickStats.uptimeSeconds = -1

    return v


AUTH_CONFIG = [
  {
    "hostname": "vcenter.domain",
    "username": "username",
    "password": "XXXXXXXXXXXXX"
  },
  {
    "hostname": "another-vcenter.domain",
    "username": "another-username",
    "password": "XXXXXXXXXXXX"
  }
]


def mocked_SmartConnect(*args, **kwargs):

    mocked_content = Object()
    mocked_content.rootFolder = Object()

    # 3 datacenters
    mocked_content.rootFolder.childEntity = [Object(), Object(), Object()]
    for dc in mocked_content.rootFolder.childEntity:
        dc.vmFolder = Object()
        dc.vmFolder.childEntity = [mocked_vm() for _ in range(10)]
        dc.name = _random_string(20)

    si = Object()
    si.RetrieveContent = lambda: mocked_content
    return si


@patch('vcenter_info.vcenter.SmartConnect', mocked_SmartConnect)
@patch('vcenter_info.vcenter.Disconnect', lambda si: None)
def test_vcenter_content_parsing():
    values = vcenter.get_vms(AUTH_CONFIG)
    jsonschema.validate(list(values), VMLIST_SCHEMA)


def test_version_api_response(client):
    rv = client.get('/api/version', headers={'Accept': ['application/json']})
    assert rv.status_code == 200
    assert rv.is_json
    response_data = json.loads(rv.data.decode('utf-8'))
    jsonschema.validate(response_data, VERSION_RESPONSE_SCHEMA)


@patch('vcenter_info.vcenter.SmartConnect', mocked_SmartConnect)
@patch('vcenter_info.vcenter.Disconnect', lambda si: None)
def test_vmlist_api_response(client):
    rv = client.get('/api/vms', headers={'Accept': ['application/json']})
    assert rv.status_code == 200
    assert rv.is_json
    response_data = json.loads(rv.data.decode('utf-8'))
    jsonschema.validate(response_data, VMLIST_SCHEMA)


def test_cache_loading(dummy_json_file):
    vm_list = api.load_cached_vms({
        'filename': dummy_json_file,
        'expiration_seconds': 100
    })
    assert vm_list


def test_cache_expired(dummy_json_file):
    time.sleep(0.5)
    vm_list = api.load_cached_vms({
        'filename': dummy_json_file,
        'expiration_seconds': .001
    })
    assert vm_list is None


def test_cache_no_file():
    with tempfile.NamedTemporaryFile() as f:
        non_existent_filename = f.name
    vm_list = api.load_cached_vms({
        'filename': non_existent_filename,
        'expiration_seconds': 100
    })
    assert vm_list is None


def test_cache_bad_json():
    with tempfile.NamedTemporaryFile() as f:
        f.write('not json'.encode('utf-8'))
        f.flush
        vm_list = api.load_cached_vms({
            'filename': f.name,
            'expiration_seconds': 100
        })
        assert vm_list is None
