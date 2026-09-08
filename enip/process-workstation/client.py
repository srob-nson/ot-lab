import os
import time

from cpppo.server.enip import client


DEVICE_ADDRESS = os.environ.get("ENIP_DEVICE_ADDRESS", "10.20.0.30")
CYCLE_SECONDS = 10


def _request(connection, operations):
    return list(
        connection.synchronous(
            operations=client.parse_operations(operations), timeout=3
        )
    )


def _has_protocol_error(records) -> bool:
    return any(len(record) < 2 or record[-2] != 0 for record in records)


def run_cycle(setpoint: float) -> bool:
    """Read both tags, write a setpoint, then read it back over TCP/CIP."""
    try:
        with client.connector(host=DEVICE_ADDRESS, timeout=3) as connection:
            initial = _request(connection, ["ProcessValue", "Setpoint"])
            if _has_protocol_error(initial):
                print(f"EtherNet/IP process protocol error during read: {initial}")
                return False

            write = _request(connection, [f"Setpoint=(REAL){setpoint}"])
            if _has_protocol_error(write) or write[0][-1] is not True:
                print(f"EtherNet/IP process protocol error during write: {write}")
                return False

            confirmed = _request(connection, ["Setpoint"])
            if _has_protocol_error(confirmed):
                print(
                    "EtherNet/IP process protocol error during confirmation: "
                    f"{confirmed}"
                )
                return False
            value = confirmed[0][-1]
            if not value or value[0] != setpoint:
                print(
                    "EtherNet/IP process confirmation failed: "
                    f"requested={setpoint} actual={value}"
                )
                return False

        print(
            "EtherNet/IP process confirmed "
            f"ProcessValue={initial[0][-1]} Setpoint={setpoint}"
        )
        return True
    except Exception as error:
        print(f"EtherNet/IP process error: {error}")
        return False


def run_loop(cycle_fn=run_cycle, sleep_fn=time.sleep, cycles=None) -> bool:
    setpoint = 20.0
    completed = 0
    all_succeeded = True
    while cycles is None or completed < cycles:
        if cycle_fn(setpoint):
            setpoint = 24.0 if setpoint == 20.0 else 20.0
        else:
            all_succeeded = False
        completed += 1
        if cycles is None or completed < cycles:
            sleep_fn(CYCLE_SECONDS)
    return all_succeeded


def configured_cycles():
    value = os.environ.get("OTLAB_CYCLES")
    return None if value is None else int(value)


if __name__ == "__main__":
    succeeded = run_loop(cycles=configured_cycles())
    raise SystemExit(0 if succeeded else 1)
