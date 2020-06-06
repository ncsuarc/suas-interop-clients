from __future__ import print_function

from interop_clients import InteropClient


def run(io: InteropClient, auto: bool) -> None:
    try:
        targets = io.get_targets()
        for target in targets:
            print("Deleting:")
            print(target)
            print("\n")
            if (not auto) and target.get("autonomous"):
                continue
            io.delete_target(target.get("id"))
    except KeyboardInterrupt:
        pass
    finally:
        pass
