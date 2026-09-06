import os

from cpppo.server.enip.main import main as enip_main


DEVICE_ADDRESS = os.environ.get("ENIP_DEVICE_ADDRESS", "10.20.0.30")


print(
    f"Starting simulated EtherNet/IP PLC at {DEVICE_ADDRESS}:44818 "
    "(TCP for queries, UDP for discovery)"
)

# Listen on every container interface.  This is important on a Docker bridge:
# UDP List Identity broadcasts reach 0.0.0.0, while the static container IP is
# still used by clients for their TCP/44818 tag sessions.
enip_main(
    argv=[
        "--config",
        "/cpppo.cfg",
        "--address",
        "0.0.0.0:44818",
        "ProcessValue=REAL",
    ]
)
