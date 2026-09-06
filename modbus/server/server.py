from pymodbus.server import StartTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

device = SimDevice(
    id=1,
    simdata=(
        [SimData(address=0, values=False, datatype=DataType.BITS)],
        [SimData(address=0, values=False, datatype=DataType.BITS)],
        [SimData(address=0, values=[25, 101, 1, 67], datatype=DataType.REGISTERS)],
        [SimData(address=0, values=0, datatype=DataType.REGISTERS)],
    ),
)

print("Starting simulated Modbus PLC on TCP/502")

StartTcpServer(
    context=device,
    address=("0.0.0.0", 502),
)
