import os
import time

from cpppo.server.enip import client


DISCOVERY_ADDRESS = os.environ.get("ENIP_DISCOVERY_ADDRESS", "10.20.0.255")
DEVICE_ADDRESS = os.environ.get("ENIP_DEVICE_ADDRESS", "10.20.0.30")
ONCE = os.environ.get("ENIP_ONCE") == "1"


def discover() -> None:
    # List Identity is the small UDP/44818 discovery exchange used by ENIP.
    # A bridge-network broadcast reaches peers on the same Docker network only.
    with client.client(host=DISCOVERY_ADDRESS, udp=True, broadcast=True) as connection:
        connection.list_identity(timeout=2)
        response, _elapsed = client.await_response(connection, timeout=2)

    if response:
        product_name = response[
            "enip.CIP.list_identity.CPF.item[0].identity_object.product_name"
        ]
        print(f"Discovered EtherNet/IP device: {product_name}")
    else:
        print("No EtherNet/IP devices discovered")


def read_process_value() -> None:
    # Tag reads use an ENIP TCP/44818 session after discovery identifies a peer.
    with client.connector(host=DEVICE_ADDRESS) as connection:
        result = list(
            connection.synchronous(
                operations=client.parse_operations(["ProcessValue"])
            )
        )[0][-1]
    print(f"ProcessValue: {result[0]}")


while True:
    try:
        discover()
        read_process_value()
    except Exception as error:
        print(f"EtherNet/IP error: {error}")

    if ONCE:
        break
    time.sleep(5)
