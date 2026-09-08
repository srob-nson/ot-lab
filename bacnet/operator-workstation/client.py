import asyncio
import os
from argparse import Namespace

from bacpypes3.app import Application


BACNET_ADDRESS = os.environ.get("BACNET_ADDRESS", "10.20.0.22")
BACNET_PREFIX = os.environ.get("BACNET_PREFIX", "24")
DEVICE_ADDRESS = os.environ.get("BACNET_DEVICE_ADDRESS", "10.20.0.20")
DEVICE_INSTANCE = int(os.environ.get("BACNET_DEVICE_INSTANCE", "2003"))
CYCLE_SECONDS = 10


def application_arguments() -> Namespace:
    return Namespace(
        address=f"{BACNET_ADDRESS}/{BACNET_PREFIX}",
        bbmd=None,
        foreign=None,
        instance=DEVICE_INSTANCE,
        name="BACnet-Operator-Workstation",
        network=None,
        ttl=None,
        vendoridentifier=999,
    )


async def run_cycle(app: Application, setpoint: float) -> bool:
    try:
        await asyncio.wait_for(
            app.write_property(
                DEVICE_ADDRESS, "analog-value,2", "present-value", setpoint
            ),
            timeout=2,
        )
        confirmed = await asyncio.wait_for(
            app.read_property(DEVICE_ADDRESS, "analog-value,2", "present-value"),
            timeout=2,
        )
        if confirmed != setpoint:
            print(
                "BACnet operator confirmation failed: "
                f"requested={setpoint} actual={confirmed}"
            )
            return False
        print(f"BACnet operator confirmed AV2 setpoint={setpoint}")
        return True
    except Exception as error:
        print(f"BACnet operator error: {error}")
        return False


async def run_loop(app: Application, cycles=None) -> bool:
    setpoint = 20.0
    completed = 0
    all_succeeded = True
    while cycles is None or completed < cycles:
        if await run_cycle(app, setpoint):
            setpoint = 24.0 if setpoint == 20.0 else 20.0
        else:
            all_succeeded = False
        completed += 1
        if cycles is None or completed < cycles:
            await asyncio.sleep(CYCLE_SECONDS)
    return all_succeeded


def configured_cycles():
    value = os.environ.get("OTLAB_CYCLES")
    return None if value is None else int(value)


async def main() -> bool:
    app = Application.from_args(application_arguments())
    try:
        return await run_loop(app, cycles=configured_cycles())
    finally:
        app.close()


if __name__ == "__main__":
    try:
        succeeded = asyncio.run(main())
    except KeyboardInterrupt:
        pass
    else:
        raise SystemExit(0 if succeeded else 1)
