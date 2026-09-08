import os
import time

from pymodbus.client import ModbusTcpClient

PLC = os.environ.get("MODBUS_PLC_ADDRESS", "10.20.0.10")
CYCLE_SECONDS = 5


def run_cycle() -> bool:
    client = ModbusTcpClient(PLC, port=502, timeout=3)
    try:
        if not client.connect():
            print("Modbus HMI connection failed")
            return False

        response = client.read_holding_registers(address=0, count=4)
        if response.isError():
            print(f"Modbus HMI read failed: {response}")
            return False

        print(f"Modbus HMI registers 0-3={response.registers}")
        return True
    except Exception as error:
        print(f"Modbus HMI error: {error}")
        return False
    finally:
        client.close()


def run_loop(cycle_fn=run_cycle, sleep_fn=time.sleep, cycles=None) -> bool:
    completed = 0
    all_succeeded = True
    while cycles is None or completed < cycles:
        all_succeeded = cycle_fn() and all_succeeded
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
