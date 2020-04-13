import datetime
import json
import string
import random
import tempfile

import pytest
from unittest.mock import patch, MagicMock
from pyVmomi import vim


class Object(object):
    pass


def random_string(num, letters=string.ascii_letters + string.digits):
    return ''.join(random.choice(letters) for _ in range(num))


def _random_vm_spec():
    return {
        'annotation': random_string(100),
        'boot': datetime.datetime.now().isoformat(),
        'datacenter': random_string(15),
        'guest': random_string(15),
        'ip': random_string(20),
        'name': random_string(20),
        'overallStatus': random_string(10),
        'path': '[' + random_string(10) + '] ' + random_string(40),
        'question': random_string(40),
        'state': random.choice(['poweredOn', 'poweredOff']),
        'stats': {
            'balloonedMemory': random.randint(-1, 1000000),
            'compressedMemory': random.randint(-1, 1000000),
            'consumedOverheadMemory': random.randint(-1, 1000000),
            'distributedCpuEntitlement': random.randint(-1, 1000000),
            'distributedMemoryEntitlement': random.randint(-1, 1000000),
            'ftLatencyStatus': random_string(10),
            'ftLogBandwidth': random.randint(-1, 1000000),
            'ftSecondaryLatency': random.randint(-1, 1000000),
            'guestHeartbeatStatus': random_string(10),
            'guestMemoryUsage': random.randint(-1, 1000000),
            'hostMemoryUsage': random.randint(-1, 1000000),
            'overallCpuDemand': random.randint(-1, 1000000),
            'overallCpuUsage': random.randint(-1, 1000000),
            'privateMemory': random.randint(-1, 1000000),
            'sharedMemory': random.randint(-1, 1000000),
            'ssdSwappedMemory': random.randint(-1, 1000000),
            'staticCpuEntitlement': random.randint(-1, 1000000),
            'staticMemoryEntitlement': random.randint(-1, 1000000),
            'swappedMemory': random.randint(-1, 1000000),
            'uptimeSeconds': random.randint(-1, 1000000)
        }
    }


def mocked_vm(spec=None):
    """
    basically the reverse of vcenter.vm_to_dict
    """
    if not spec:
        spec = _random_vm_spec()

    v = MagicMock(spec=vim.VirtualMachine)
    v.summary = Object()
    v.summary.overallStatus = spec['overallStatus']

    v.summary.config = Object()
    v.summary.config.name = spec['name']
    v.summary.config.vmPathName = spec['path']
    v.summary.config.guestFullName = spec['guest']
    v.summary.config.annotation = spec['annotation']

    v.summary.runtime = Object()
    v.summary.runtime.bootTime = datetime.datetime.fromisoformat(spec['boot'])
    v.summary.runtime.powerState = spec['state']
    v.summary.runtime.question = Object()
    v.summary.runtime.question.text = spec['question']

    v.summary.guest = Object()
    v.summary.guest.ipAddress = spec['ip']

    v.summary.quickStats = Object()
    for name, value in spec['stats'].items():
        setattr(v.summary.quickStats, name, value)

    return v


@pytest.fixture
def auth_config():
    yield [
        {
            "hostname": "vcenter.domain",
            "username": "username",
            "password": "XXXXXXXXXXXXX"
        },
        {
            "hostname": "another-vcenter.domain",
            "username": "another-username",
            "password": "XXXXXXXXXXXX"
        },
        {
            "hostname": "blah-vcenter.domain",
            "username": "some-other-username",
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
        dc.name = random_string(20)

    si = Object()
    si.RetrieveContent = lambda: mocked_content
    return si


@pytest.fixture
def config_file():
    def _dc():
        return {
            'hostname': random_string(20),
            'username': random_string(20),
            'password': random_string(20)
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
        yield config_file.name


@pytest.fixture
def mocked_vcenter():
    with patch('vcenter_info.vcenter.SmartConnect', mocked_SmartConnect):
        with patch('vcenter_info.vcenter.Disconnect', lambda si: None):
            yield
