import jsonschema
import random
import string
from pyVmomi import vim
from unittest.mock import patch
from unittest.mock import MagicMock
from vcenter_info import vcenter


VMLIST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "definitions": {
        "vm": {
            "type": "object",
            "properties": {
                "annotation": {"type": "string"},
                "datacenter": {"type": "string"},
                "guest": {"type": "string"},
                "ip": {"type": ["string", "null"]},
                "name": {"type": "string"},
                "path": {"type": "string"},
                "question": {"type": ["string", "null"]},
                "san": {"type": ["string", "null"]},
                "state": {"type": "string"},
            },
            "required": [
                "annotation", "datacenter", "guest",
                "ip", "name", "path", "question", "san", "state"],
            "additionalProperties": False
        }
    },

    "type": "array",
    "items": {"$ref": "#/definitions/vm"}

}
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
    v.summary.runtime.powerState = spec['state']
    v.summary.runtime.question = Object()
    v.summary.runtime.question.text = spec['question']

    v.summary.guest = Object()
    v.summary.guest.ipAddress = spec['ip']

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
    si.RetrieveContent = lambda : mocked_content
    return si


def mocked_Disconnect(si):
    pass


@patch('vcenter_info.vcenter.SmartConnect', mocked_SmartConnect)
@patch('vcenter_info.vcenter.Disconnect', lambda si: None)
def test_vcenter_content_parsing():
    values = vcenter.get_vms(AUTH_CONFIG)
    jsonschema.validate(list(values), VMLIST_SCHEMA)
