import os

from cpppo.server.enip import client


DEVICE = os.environ.get("ENIP_DEVICE_ADDRESS", "10.22.0.30")


with client.connector(host=DEVICE) as connection:
    before = list(
        connection.synchronous(operations=client.parse_operations(["ProcessValue"]))
    )[0][-1]
    assert before == [0.0], before

    write_result = list(
        connection.synchronous(
            operations=client.parse_operations(["ProcessValue=(REAL)24.5"])
        )
    )[0][-1]
    assert write_result is True, write_result

    after = list(
        connection.synchronous(operations=client.parse_operations(["ProcessValue"]))
    )[0][-1]
    assert after == [24.5], after

print("EtherNet/IP direct write verified: 0.0 -> 24.5")
