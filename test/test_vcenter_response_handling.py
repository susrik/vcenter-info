import json
import jsonschema
import os
import tempfile
import time
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
                'distributedCpuEntitlement': {
                    'type': 'integer', 'minimum': -1},
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
                'overallStatus': {'type': 'string'},
                'path': {'type': 'string'},
                'question': {'type': ['string', 'null']},
                'san': {'type': ['string', 'null']},
                'state': {'type': 'string'},
                'stats': {'$ref': '#/definitions/stats'}
            },
            'required': [
                'annotation', 'datacenter', 'guest',
                'ip', 'name', 'overallStatus', 'path',
                'question', 'san', 'state', 'stats'],
            'additionalProperties': False
        }
    },

    'type': 'array',
    'items': {'$ref': '#/definitions/vm'}

}


@pytest.fixture
def client(config_file):
    os.environ['CONFIG_FILENAME'] = config_file
    with vcenter_info.create_app().test_client() as c:
        yield c


@pytest.fixture
def dummy_json_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(json.dumps({'a': 1}).encode('utf-8'))
        f.flush()
        yield f.name


def test_vcenter_content_parsing(mocked_vcenter, auth_config):
    values = vcenter.get_vms(auth_config)
    jsonschema.validate(list(values), VMLIST_SCHEMA)


def test_version_api_response(client):
    rv = client.get('/api/version', headers={'Accept': ['application/json']})
    assert rv.status_code == 200
    assert rv.is_json
    response_data = json.loads(rv.data.decode('utf-8'))
    jsonschema.validate(response_data, VERSION_RESPONSE_SCHEMA)


def test_vmlist_api_response(mocked_vcenter, client):
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
        f.flush()
        vm_list = api.load_cached_vms({
            'filename': f.name,
            'expiration_seconds': 100
        })
        assert vm_list is None
