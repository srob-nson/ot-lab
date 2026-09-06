import asyncio
import os
from argparse import Namespace

from bacpypes3.app import Application

BACNET_ADDRESS = os.environ.get("BACNET_ADDRESS", "10.20.0.21")
BACNET_PREFIX = os.environ.get("BACNET_PREFIX", "24")


def application_arguments() -> Namespace:
    return Namespace(
        address=f"{BACNET_ADDRESS}/{BACNET_PREFIX}",
        bbmd=None,
        foreign=None,
        instance=2002,
        name="BACnet-Lab-Client",
        network=None,
        ttl=None,
        vendoridentifier=999,
    )


async def main() -> None:
    app = Application.from_args(application_arguments())

    try:
        while True:
            devices = await app.who_is(timeout=2)

            if devices:
                for device in devices:
                    print(
                        f"Discovered BACnet device {device.iAmDeviceIdentifier[1]} "
                        f"at {device.pduSource}"
                    )
            else:
                print("No BACnet devices discovered")

            await asyncio.sleep(3)
    finally:
        app.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
