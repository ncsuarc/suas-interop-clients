from __future__ import print_function

from interop_clients import Interop


def run(io: Interop) -> None:
    try:
        targets = io.get_targets()
        print("\nTargets:")
        for target in targets:
            print(target)
    except KeyboardInterrupt:
        pass
    finally:
        pass
