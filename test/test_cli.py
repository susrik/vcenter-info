from vcenter_info import cli
from click.testing import CliRunner


def test_happy_flow(mocked_vcenter, config_file):
    expected_measurement = 'abab'
    runner = CliRunner()
    result = runner.invoke(
        cli.cli, [
            '--measurement', expected_measurement,
            '--config', config_file
        ])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines  # there should be some output
    # TODO: verify influx format if necessary
