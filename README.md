# OT Lab

This repo is a minimalistic lab for testing OT networks.
It includes three devices for each of Modbus, BACnet, and EtherNet/IP on
the external `ot-net` Docker bridge (`10.20.0.0/24`).

| Protocol | Address | Role | Activity |
| --- | --- | --- | --- |
| Modbus | `10.20.0.10` | PLC | Serves coils and holding registers on TCP/502 |
| Modbus | `10.20.0.11` | HMI | Reads the PLC holding registers every 5 seconds |
| Modbus | `10.20.0.12` | Engineering workstation | Toggles a coil and alternates the setpoint every 10 seconds |
| BACnet | `10.20.0.20` | PLC | Serves temperature and writable setpoint objects on UDP/47808 |
| BACnet | `10.20.0.21` | BMS monitor | Discovers the PLC and reads both analog values every 5 seconds |
| BACnet | `10.20.0.22` | Operator workstation | Alternates and confirms the setpoint every 10 seconds |
| EtherNet/IP | `10.20.0.30` | PLC | Serves identity and process tags on TCP/UDP 44818 |
| EtherNet/IP | `10.20.0.31` | Asset scanner | Sends directed List Identity requests every 5 seconds |
| EtherNet/IP | `10.20.0.32` | Process workstation | Reads process tags and alternates the setpoint every 10 seconds |

## Installing
Requires Docker and Docker Compose
Clone the repo first

```
git clone https://github.com/srob-nson/ot-lab.git
cd ot-lab
```
Then bring up the stack and verify every service is running:
```
./scripts/up.sh
```

The script creates the required `ot-net` Docker network when needed,
builds and starts the full Compose stack, and waits up to 60 seconds for
all services to report a running state. If startup fails, it prints the
current container status and recent logs.
