from pymodbus.server import StartTcpServer
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)

INITIAL_REGISTERS = [25, 22, 1, 67]


def build_device() -> ModbusServerContext:
    """Build the PLC data model with its fixed process values."""
    # ModbusDeviceContext translates protocol address 0 to datastore address 1.
    device = ModbusDeviceContext(
        di=ModbusSequentialDataBlock(1, [False] * 8),
        co=ModbusSequentialDataBlock(1, [False] * 8),
        ir=ModbusSequentialDataBlock(1, [0] * 8),
        hr=ModbusSequentialDataBlock(1, INITIAL_REGISTERS + [0] * 4),
    )
    return ModbusServerContext(devices=device, single=True)


def run_cycle() -> None:
    print("Starting simulated Modbus PLC on TCP/502")
    StartTcpServer(context=build_device(), address=("0.0.0.0", 502))


if __name__ == "__main__":
    run_cycle()
