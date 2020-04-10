import json
import logging
import os
import re
import ssl
import jinja2
import jsonschema
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


logger = logging.getLogger(__name__)
MAX_DEPTH = 10
TEMPLATE_FILENAME = os.path.join(os.path.dirname(__file__), 'report.html.tpl')
CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",

    "definitions": {
        "datacenter": {
            "type": "object",
            "properties": {
                "hostname": {"type": "string"},
                "port": {"type": "integer"},
                "username": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["hostname", "username", "password"],
            "additionalProperties": False
        }
    },

    "type": "array",
    "items": {"$ref": "#/definitions/datacenter"}
}


def vm_summary(vm):
    summary = vm.summary
    config = summary.config
    info = {
        'name': config.name,
        'path': config.vmPathName,
        'guest': config.guestFullName,
        'annotation': config.annotation,
        'state': summary.runtime.powerState,
        'ip': None,
        'question': None,
        'san': None
    }
    if summary.guest is not None:
        info['ip'] = summary.guest.ipAddress
    if summary.runtime.question is not None:
        info['question'] = summary.runtime.question.text
    m = re.match('^.*\[([^]]+)\].*', info['path'])
    if m:
        info['san'] = m.group(1)
    return info


def vms_from_list(vmList, depth=0):
    if depth > MAX_DEPTH:
        return

    for vm in vmList:

        if hasattr(vm, 'childEntity'):
            yield from vms_from_list(vm.childEntity, depth+1)
            continue

        if isinstance(vm, vim.VirtualApp):
            yield from vms_from_list(vm.vm, depth+1)
            continue

        assert isinstance(vm, vim.VirtualMachine)
        yield vm


def load_vms_from_datacenters(auth_filename):

    with open(auth_filename) as f:
        config = json.loads(f.read())
        jsonschema.validate(config,  CONFIG_SCHEMA)

    for dc in config:

        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()

        si = None
        try:
            port = dc.get('port', 443)
            si = SmartConnect(
                host=dc['hostname'],
                port=port,
                user=dc['username'],
                pwd=dc['password'],
                sslContext=context)

            if not si:
                print(f'error connecting to {dc["hostname"]}:{port}')
                return -1

            content = si.RetrieveContent()
            for datacenter in content.rootFolder.childEntity:
                if hasattr(datacenter, 'vmFolder'):
                    yield {
                        'datacenter': datacenter.name,
                        'vms': vms_from_list(datacenter.vmFolder.childEntity)
                    }

        finally:
            if si:
                Disconnect(si)


def get_vms(config_filename):
    for dc in load_vms_from_datacenters(config_filename):
        for vm in dc['vms']:
            summary = vm_summary(vm)
            summary['datacenter'] = dc['datacenter']
            yield summary


def generate_html_report(vmList):
    with open(TEMPLATE_FILENAME) as f:
        template = jinja2.Template(f.read())

    return template.render(vms=vmList)


if __name__ == "__main__":

    CONFIG_FILENAME = 'config.json'
    report = generate_html_report(get_vms(CONFIG_FILENAME))
    print(report)
