import json
import logging
import re
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import datetime


logger = logging.getLogger(__name__)
MAX_DEPTH = 10


def vm_to_dict(vm):
    summary = vm.summary
    config = summary.config
    info = {
        'name': config.name,
        'path': config.vmPathName,
        'guest': config.guestFullName,
        'annotation': config.annotation,
        'state': summary.runtime.powerState,
        'overallStatus': str(summary.overallStatus),
        'ip': None,
        'question': None,
        'san': None,
        'boot': None,
        'stats': {
            # cf. https://vdc-download.vmware.com/vmwb-repository/dcr-public/da47f910-60ac-438b-8b9b-6122f4d14524/16b7274a-bf8b-4b4c-a05e-746f2aa93c8c/doc/vim.vm.Summary.QuickStats.html  # noqa
            'balloonedMemory': -1,
            'compressedMemory': -1,
            'consumedOverheadMemory': -1,
            'distributedCpuEntitlement': -1,
            'distributedMemoryEntitlement': -1,
            'ftLatencyStatus': None,
            'ftLogBandwidth': -1,
            'ftSecondaryLatency': -1,
            'guestHeartbeatStatus': None,
            'guestMemoryUsage': -1,
            'hostMemoryUsage': -1,
            'overallCpuDemand': -1,
            'overallCpuUsage': -1,
            'privateMemory': -1,
            'sharedMemory': -1,
            'ssdSwappedMemory': -1,
            'staticCpuEntitlement': -1,
            'staticMemoryEntitlement': -1,
            'swappedMemory': -1,
            'uptimeSeconds': -1
        }
    }
    if summary.guest is not None:
        info['ip'] = summary.guest.ipAddress
    if summary.runtime.question is not None:
        info['question'] = summary.runtime.question.text
    m = re.match(r'^.*\[([^]]+)\].*', info['path'])
    if m:
        info['san'] = m.group(1)

    if isinstance(summary.runtime.bootTime, datetime.datetime):
        info['boot'] = summary.runtime.bootTime.isoformat()

    for name in info['stats']:
        value = getattr(summary.quickStats, name, None)
        info['stats'][name] = value if isinstance(value, int) else str(value)

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


def load_vms_from_datacenters(auth_config):

    for dc in auth_config:

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


def get_vms(auth_config):
    for dc in load_vms_from_datacenters(auth_config):
        for vm in dc['vms']:
            summary = vm_to_dict(vm)
            summary['datacenter'] = dc['datacenter']
            yield summary


if __name__ == "__main__":

    import jinja2
    # import jsonschema
    import os

    TEMPLATE_FILENAME = os.path.join(
        os.path.dirname(__file__),
        'report.html.tpl')
    CONFIG_FILENAME = 'config.json'

    with open(CONFIG_FILENAME) as f:
        config = json.loads(f.read())
        # jsonschema.validate(config,  CONFIG_SCHEMA)

    with open(TEMPLATE_FILENAME) as f:
        template = jinja2.Template(f.read())

    report = template.render(vms=get_vms(config))

    print(report)
