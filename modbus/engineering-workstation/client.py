import os
import time

from pymodbus.client import ModbusTcpClient


PLC = os.environ.get("MODBUS_PLC_ADDRESS", "10.20.0.10")
CYCLE_SECONDS = 10


def run_cycle(setpoint: int) -> bool:
    """Toggle coil zero, write the requested setpoint, and confirm both."""
    client = ModbusTcpClient(PLC, port=502, timeout=3)
    try:
        if not client.connect():
            print("Modbus engineering connection failed")
            return False

        coil = client.read_coils(address=0, count=1)
        if coil.isError() or not coil.bits:
            print(f"Modbus engineering coil read failed: {coil}")
            return False

        requested_coil = not coil.bits[0]
        written_coil = client.write_coil(address=0, value=requested_coil)
        if written_coil.isError():
            print(f"Modbus engineering coil write failed: {written_coil}")
            return False

        written_register = client.write_register(address=1, value=setpoint)
        if written_register.isError():
            print(f"Modbus engineering register write failed: {written_register}")
            return False

        confirmed_coil = client.read_coils(address=0, count=1)
        confirmed_register = client.read_holding_registers(address=1, count=1)
        if confirmed_coil.isError() or confirmed_register.isError():
            print("Modbus engineering confirmation failed: read error")
            return False
        if (
            not confirmed_coil.bits
            or not confirmed_register.registers
            or confirmed_coil.bits[0] != requested_coil
            or confirmed_register.registers[0] != setpoint
        ):
            print(
                "Modbus engineering confirmation failed: "
                f"coil={confirmed_coil.bits} register={confirmed_register.registers}"
            )
            return False

        print(
            "Modbus engineering confirmed "
            f"coil0={requested_coil} register1={setpoint}"
        )
        return True
    except Exception as error:
        print(f"Modbus engineering error: {error}")
        return False
    finally:
        client.close()


def run_loop(cycle_fn=run_cycle, sleep_fn=time.sleep, cycles=None) -> bool:
    setpoint = 20
    completed = 0
    all_succeeded = True
    while cycles is None or completed < cycles:
        try:
            confirmed = cycle_fn(setpoint)
        except Exception as error:
            print(f"Modbus engineering error: {error}")
            confirmed = False
        if confirmed:
            setpoint = 24 if setpoint == 20 else 20
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
