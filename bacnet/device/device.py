import asyncio
import os
from argparse import Namespace

from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject

BACNET_ADDRESS = os.environ.get("BACNET_ADDRESS", "10.20.0.20")
BACNET_PREFIX = os.environ.get("BACNET_PREFIX", "24")
DEVICE_INSTANCE = int(os.environ.get("BACNET_DEVICE_INSTANCE", "2001"))


def application_arguments() -> Namespace:
    return Namespace(
        address=f"{BACNET_ADDRESS}/{BACNET_PREFIX}",
        bbmd=None,
        foreign=None,
        instance=DEVICE_INSTANCE,
        name="BACnet-Simulated-PLC",
        network=None,
        ttl=None,
        vendoridentifier=999,
    )


async def main() -> None:
    app = Application.from_args(application_arguments())
    app.add_object(
        AnalogValueObject(
            objectIdentifier=("analog-value", 1),
            objectName="Process-Temperature",
            presentValue=21.5,
            units="degreesCelsius",
            description="Simulated process temperature",
        )
    )
    app.add_object(
        AnalogValueObject(
            objectIdentifier=("analog-value", 2),
            objectName="Temperature-Setpoint",
            presentValue=22.0,
            units="degreesCelsius",
            description="Directly writable temperature setpoint",
        )
    )

    print(
        f"Starting simulated BACnet PLC: device {DEVICE_INSTANCE} "
        f"at {BACNET_ADDRESS}:47808/udp"
    )
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
