import logging
import click
from vcenter_info import vcenter, config

logger = logging.getLogger(__name__)


def _key_values(d):
    return ['%s=%s' % (k, v) for k, v in d.items()]


def _make_influx_line(measurement, fields, tags):
    return '{measurement},{tags} {fields}'.format(
        measurement=measurement,
        tags=','.join(_key_values(tags)),
        fields=','.join(_key_values(fields)))


def _validate_config(ctx, param, value):
    """
    loads, validates and returns configuration parameters

    :param ctx:
    :param param:
    :param value: filename (string)
    :return: a dict containing configuration parameters
    """
    try:
        return config.parse_config_and_add_defaults(value.read())
    except Exception as e:
        raise click.BadParameter(e)


@click.command()
@click.option(
    '--measurement',
    required=True,
    type=click.STRING,
    help='influx measurement name')
@click.option(
    '--config',
    required=True,
    type=click.File('r'),
    help='config filename',
    callback=_validate_config)
def cli(measurement, config):

    for vm in vcenter.get_vms(config['auth']):
        if vm['state'] != 'poweredOn':
            continue
        tags = {'name': vm['name'], 'datacenter': vm['datacenter']}
        fields = dict([
            (k, v) for k, v in vm['stats'].items()
            if isinstance(v, int)])
        print(_make_influx_line(
            measurement=measurement,
            fields=fields,
            tags=tags))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cli()
