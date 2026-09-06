import asyncio
from argparse import Namespace

from bacpypes3.app import Application


async def main() -> None:
    app = Application.from_args(
        Namespace(
            address="10.21.0.22/24",
            bbmd=None,
            foreign=None,
            instance=2003,
            name="BACnet-Read-Write-Test",
            network=None,
            ttl=None,
            vendoridentifier=999,
        )
    )

    try:
        before = await app.read_property(
            "10.21.0.20", "analog-value,2", "present-value"
        )
        assert before == 22.0, before

        response = await app.write_property(
            "10.21.0.20", "analog-value,2", "present-value", 24.5
        )
        assert response is None, response

        after = await app.read_property(
            "10.21.0.20", "analog-value,2", "present-value"
        )
        assert after == 24.5, after
        print("BACnet direct write verified: 22.0 -> 24.5")
    finally:
        app.close()


asyncio.run(main())
