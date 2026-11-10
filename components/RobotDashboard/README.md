# RobotDashboard

RoboComp component that subscribes to the `RobotStatusPub` IceStorm topic,
stores the measurements in TinyDB and serves the web dashboard.

The legacy `Server/` directory is kept as-is and is not used by this
component. The browser path is still HTTP + Socket.IO; the sensor path is Ice
only.

## Dependencies

- RoboComp (CMake helpers, `ConfigLoader`, IceStorm)
- Python 3, `PySide6`, `rich`, `Ice`
- `flask`, `flask-socketio`, `tinydb`

## Configuration

`etc/config`:

```ini
Proxies.TopicManager = "IceStorm/TopicManager:default -p 9999"
Endpoints.RobotStatusPubTopic = "tcp -p 0"
Endpoints.RobotStatusPubPrefix = ""

Web.Host = "0.0.0.0"
Web.Port = 5000
```

The databases are created under `components/RobotDashboard/database/`.

## Subscription contract

The component subscribes to `RobotStatusPub` and accepts the following keys.
Unknown keys are ignored and reported once in the component log.

| Interface method | Keys | Destination | Socket.IO event |
|---|---|---|---|
| `powerState` | `INA1`...`INA5` | `bateries` | `update_chart` |
| `powerState` | `Victron` (or any key containing `victron`) | `victron` | `update_chart` |
| `powerState` | `SBC1`...`SBC4`, `SBC/amps1`... etc. | `shadowBaseCurrents` | `update_chart` |
| `thermalState` | `base`, `chimenea`, `exterior`, `bandeja` | `temperature` | `update_chart` |
| `thermalState` | `SBT1`...`SBT4`, `temp1`...`temp4` | `shadowBaseTemperatures` | `update_chart` |

SBC/SBT channels are buffered until all four values have arrived, so a
publisher may send them in a single map or in four separate calls.
Power values are expected in volts/amperes and temperatures in degrees
Celsius. Power (`pow`) is computed as `voltage * current`.

## HTTP routes

- `/live`: live charts and log feed.
- `/search`: historical search.
- `/getData`: JSON data used by the search page.
- `/database/logs.json`: TinyDB log file.

There are no `/insert...` routes: sensor data must arrive through Ice.

## Build and run

```bash
pip install -r requirements.txt   # flask, flask-socketio, tinydb
cmake . && make
rcnode
bin/RobotDashboard etc/config
```

Open `http://<host>:5000/live`.

The legacy `Server/server.py` can still be run independently, but it uses its
own database and HTTP ingestion. Do not run both web servers on the same port
at the same time.
