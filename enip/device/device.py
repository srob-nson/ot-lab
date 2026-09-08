import os

from cpppo.server.enip.device import Attribute
from cpppo.server.enip.main import main as enip_main


DEVICE_ADDRESS = os.environ.get("ENIP_DEVICE_ADDRESS", "10.20.0.30")


class InitializedAttribute(Attribute):
    """Supply distinct startup values for the two PLC tags."""

    def __init__(self, name, type_cls, default=0, error=0, mask=0):
        if name == "ProcessValue":
            default = 25.0
        elif name == "Setpoint":
            default = 22.0
        super().__init__(name, type_cls, default=default, error=error, mask=mask)


def run_cycle() -> None:
    print(
        f"Starting simulated EtherNet/IP PLC at {DEVICE_ADDRESS}:44818 "
        "(TCP for tags, UDP for directed identity)"
    )
    enip_main(
        argv=[
            "--config",
            "/cpppo.cfg",
            "--address",
            "0.0.0.0:44818",
            "ProcessValue=REAL",
            "Setpoint=REAL",
        ],
        attribute_class=InitializedAttribute,
    )


if __name__ == "__main__":
    run_cycle()
