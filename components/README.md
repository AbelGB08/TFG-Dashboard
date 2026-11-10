# RoboComp components

The components in this directory form the Ice-based implementation of the
dashboard. The legacy `../Rasp` and `../Server` directories are kept untouched
as the original HTTP prototype.

## Data flow

```text
INA226Sensor ──────powerState──────┐
ds18b20TempSensor ─thermalState────┤
SBC/SBT/Victron ───RobotStatusPub──┴──> IceStorm topic RobotStatusPub
                                                   │
                                                   v
                                            RobotDashboard
                                       ┌───────────┴───────────┐
                                       v                       v
                                    TinyDB              Flask + Socket.IO
                                                               │
                                                               v
                                                           browser
```

The sensor -> dashboard path uses IceStorm only. The browser -> dashboard path
uses HTTP for pages/search and Socket.IO for live updates.

## Components

| Component | Role |
|---|---|
| `INA226Sensor` | Publishes `INA1`...`INA5` power samples |
| `ds18b20TempSensor` | Publishes `base`, `chimenea`, `exterior`, `bandeja` temperatures |
| `RobotDashboard` | Subscribes to `RobotStatusPub`, stores data and serves the web UI |

SBC, SBT and Victron are expected to publish through the same
`RobotStatusPub` topic. The dashboard accepts the key conventions documented in
`RobotDashboard/README.md`.

## Build

Each component is built independently:

```bash
cd INA226Sensor
cmake . && make
```

`RobotStatusPub.idsl` must be discoverable by `ROBOCOMP_IDSL_TO_ICE`
(`$ROBOCOMP/interfaces/IDSLs`, `/opt/robocomp/interfaces/IDSLs` or
`SLICE_PATH`).

## Run

```bash
rcnode

cd INA226Sensor && bin/INA226Sensor etc/config
cd ds18b20TempSensor && bin/ds18b20TempSensor etc/config
cd RobotDashboard && bin/RobotDashboard etc/config
```

Open `http://<host>:5000/live` for the live dashboard and
`http://<host>:5000/search` for historical data.
