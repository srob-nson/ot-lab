# OT Lab

This repo is a minimalistic lab for testing OT networks. 
Includes examples of Modbus, BACnet and ENIP traffic currently but will be expanded for many others

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
