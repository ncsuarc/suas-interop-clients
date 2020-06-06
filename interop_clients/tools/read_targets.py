from __future__ import print_function

from interop_clients import InteropClient


def run(io: InteropClient) -> None:
    try:
        targets = io.get_targets()
        print("\nTargets:")
        for target in targets:
            print(target)
    except KeyboardInterrupt:
        pass
    finally:
        pass
