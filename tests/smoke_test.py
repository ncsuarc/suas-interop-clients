import subprocess

import interop_clients


def test_version():
    # Ensure that interop was at least properly installed
    proc = subprocess.run(
        ["interop", "--version"], check=True, stdout=subprocess.PIPE
    )
    assert interop_clients.__version__.encode() in proc.stdout
