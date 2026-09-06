import time
from pymodbus.client import ModbusTcpClient

PLC = "10.20.0.10"

while True:
    client = ModbusTcpClient(PLC, port=502)

    if client.connect():
        result = client.read_holding_registers(
            address=0,
            count=4,
        )

        if not result.isError():
            print(f"PLC registers: {result.registers}")
        else:
            print(f"Modbus error: {result}")

        client.close()
    else:
        print("Unable to connect to PLC")

    time.sleep(5)
