"""Web dashboard for the RobotDashboard component.

This module is the RoboComp version of the old ``Server/server.py``.  The
sensor -> dashboard path is now IceStorm (see ``specificworker.py``); the
browser -> dashboard path still uses Flask (pages and search) and Socket.IO
(live chart/log notifications).

The legacy ``Server`` directory is intentionally left untouched.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory
from flask_socketio import SocketIO
from tinydb import Query, TinyDB

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

bateries = TinyDB(str(DATABASE_DIR / "bateries.json"))
temperature = TinyDB(str(DATABASE_DIR / "temperature.json"))
victron = TinyDB(str(DATABASE_DIR / "victron.json"))
shadowBaseCurrents = TinyDB(str(DATABASE_DIR / "shadowBaseCurrents.json"))
shadowBaseTemperatures = TinyDB(str(DATABASE_DIR / "shadowBaseTemperatures.json"))
logs = TinyDB(str(DATABASE_DIR / "logs.json"))

# Same database/schema mapping used by the legacy server.  ``VICTRON`` is the
# new entry required by the component implementation.
sensor_config = {
    "INA": {
        "db": bateries,
        "fields": ["volts", "amps", "pow"],
    },
    "BT": {
        "db": temperature,
        "fields": ["base", "chimenea", "exterior", "bandeja"],
    },
    "SBC": {
        "db": shadowBaseCurrents,
        "fields": ["amps1", "amps2", "amps3", "amps4"],
    },
    "SBT": {
        "db": shadowBaseTemperatures,
        "fields": ["temp1", "temp2", "temp3", "temp4"],
    },
    "VICTRON": {
        "db": victron,
        "fields": ["volts", "amps", "pow"],
    },
}

with open(BASE_DIR / "sensor_limits.json", encoding="utf-8") as limits_file:
    sensor_limits = json.load(limits_file)

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# ``threading`` avoids eventlet/gevent monkey-patching, which does not play
# well with Qt and the Ice runtime used by RoboComp.
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

# Ice callbacks run in Ice threads.  Protect TinyDB read-modify-write
# operations with a re-entrant lock.
_db_lock = threading.RLock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now() -> str:
    return datetime.now().strftime(DATE_FORMAT)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Parse a stored or query date (``dd-mm-yyyy [HH:MM[:SS]]``)."""
    if not value:
        return None
    for fmt in (DATE_FORMAT, "%d-%m-%Y %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except (TypeError, ValueError):
            continue
    return None


def _as_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _record_limit_log(
    sensor: str,
    value_type: str,
    value: float,
    limits: Optional[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Insert and return a log entry if ``value`` is outside ``limits``."""
    if not limits:
        return None

    upper = _as_float(limits.get("upper_limit"))
    lower = _as_float(limits.get("lower_limit"))
    if upper is None or lower is None:
        return None

    if lower <= value <= upper:
        return None

    log_data = {
        "sensor": sensor,
        "valueType": value_type,
        "value": value,
        "date": _now(),
    }
    with _db_lock:
        logs.insert(log_data)
    return log_data


def _emit_log(log_data: Mapping[str, Any]) -> None:
    socketio.emit(
        "log",
        {
            "sensor": log_data["sensor"],
            "date": log_data["date"],
            "message": (
                f"Sensor {log_data['sensor']} has exceeded the limit: "
                f"{log_data['valueType']} = {log_data['value']}"
            ),
        },
    )


def emit_chart(data: Mapping[str, Any]) -> None:
    socketio.emit("update_chart", dict(data))


def _emit_logs(log_entries: Iterable[Optional[Dict[str, Any]]]) -> None:
    for entry in log_entries:
        if entry:
            _emit_log(entry)


# ---------------------------------------------------------------------------
# Data ingestion (called from Ice subscriptions, never from HTTP)
# ---------------------------------------------------------------------------
def store_power(sensor: str, voltage: Any, current: Any) -> Optional[Dict[str, Any]]:
    """Store one INA-style power sample and notify the browser."""
    voltage_value = _as_float(voltage)
    current_value = _as_float(current)
    if voltage_value is None or current_value is None:
        return None

    data = {
        "volts": voltage_value,
        "amps": current_value,
        "pow": voltage_value * current_value,
        "date": _now(),
        "sensor": sensor,
    }

    with _db_lock:
        bateries.insert(data)

    limits = sensor_limits.get(sensor, {})
    _emit_logs(
        [
            _record_limit_log(sensor, "Amps", current_value, limits.get("amps")),
            _record_limit_log(sensor, "Volts", voltage_value, limits.get("volts")),
        ]
    )
    emit_chart(data)
    return data


def store_victron(voltage: Any, current: Any) -> Optional[Dict[str, Any]]:
    """Store a Victron power sample and notify the browser."""
    voltage_value = _as_float(voltage)
    current_value = _as_float(current)
    if voltage_value is None or current_value is None:
        return None

    data = {
        "volts": voltage_value,
        "amps": current_value,
        "pow": voltage_value * current_value,
        "date": _now(),
        "sensor": "victron",
    }

    with _db_lock:
        victron.insert(data)

    limits = sensor_limits.get("VICTRON", {})
    _emit_logs(
        [
            _record_limit_log("VICTRON", "Amps", current_value, limits.get("amps")),
            _record_limit_log("VICTRON", "Volts", voltage_value, limits.get("volts")),
        ]
    )
    emit_chart(data)
    return data


def store_temperatures(values: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Store the four body temperatures (BT) and notify the browser."""
    fields = ["base", "chimenea", "exterior", "bandeja"]
    converted: Dict[str, float] = {}
    for field in fields:
        value = _as_float(values.get(field))
        if value is None:
            return None
        converted[field] = value

    data = {
        "base": converted["base"],
        "chimenea": converted["chimenea"],
        "exterior": converted["exterior"],
        "bandeja": converted["bandeja"],
        "date": _now(),
        "sensor": "temps",
    }

    with _db_lock:
        temperature.insert(data)

    _emit_logs(
        _record_limit_log(
            "BT",
            field.capitalize() + " Temp",
            converted[field],
            sensor_limits.get("BT", {}).get(field),
        )
        for field in fields
    )
    emit_chart(data)
    return data


def store_sbc(values: Mapping[int, Any]) -> Optional[Dict[str, Any]]:
    """Store a ShadowBase current sample (four channels)."""
    currents: Dict[str, float] = {}
    for index in range(1, 5):
        value = _as_float(values.get(index))
        if value is None:
            return None
        currents[f"amps{index}"] = value

    data = {
        "amps1": currents["amps1"],
        "amps2": currents["amps2"],
        "amps3": currents["amps3"],
        "amps4": currents["amps4"],
        "date": _now(),
        "sensor": "sbc",
    }

    with _db_lock:
        shadowBaseCurrents.insert(data)

    limits = sensor_limits.get("SBC", {}).get("amps")
    _emit_logs(
        _record_limit_log("SBC", f"Amps{index}", currents[f"amps{index}"], limits)
        for index in range(1, 5)
    )
    emit_chart(data)
    return data


def store_sbt(values: Mapping[int, Any]) -> Optional[Dict[str, Any]]:
    """Store a ShadowBase temperature sample (four channels)."""
    temperatures: Dict[str, float] = {}
    for index in range(1, 5):
        value = _as_float(values.get(index))
        if value is None:
            return None
        temperatures[f"temp{index}"] = value

    data = {
        "temp1": temperatures["temp1"],
        "temp2": temperatures["temp2"],
        "temp3": temperatures["temp3"],
        "temp4": temperatures["temp4"],
        "date": _now(),
        "sensor": "sbt",
    }

    with _db_lock:
        shadowBaseTemperatures.insert(data)

    _emit_logs(
        _record_limit_log(
            "SBT",
            f"Temp{index}",
            temperatures[f"temp{index}"],
            sensor_limits.get("SBT", {}).get(f"temp{index}"),
        )
        for index in range(1, 5)
    )
    emit_chart(data)
    return data


# ---------------------------------------------------------------------------
# Flask routes (browser <-> dashboard only; no ingestion endpoints)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect("/live")


@app.route("/live")
def live():
    return render_template("live.html")


@app.route("/search")
def search():
    return render_template("index.html")


@app.route("/getData", methods=["GET"])
def get_data():
    sensor_name = request.args.get("sensorName")
    start_date = format_date(request.args.get("startDate"))
    end_date = format_date(request.args.get("endDate"))

    if not sensor_name or not start_date or not end_date:
        return jsonify(message="Missing query parameters", data=[]), 400

    start = _parse_date(start_date)
    end = _parse_date(end_date)
    if start is None or end is None:
        return jsonify(message="Invalid date range", data=[]), 400
    if end_date.count(":") == 1:
        # ``datetime-local`` has minute precision: include the whole minute.
        end += timedelta(seconds=59)

    def in_range(record_date: Optional[str]) -> bool:
        parsed = _parse_date(record_date)
        return parsed is not None and start <= parsed <= end

    # Dates are stored as dd-mm-yyyy strings, so comparing them directly is
    # only correct inside the same year.  Compare parsed datetimes instead.
    data_query = Query()
    query_condition = data_query.date.test(in_range)
    if sensor_name.startswith("INA"):
        sensor_key = sensor_name[:3]
        query_condition &= data_query.sensor == sensor_name
    else:
        sensor_key = sensor_name

    config = sensor_config.get(sensor_key)
    if not config:
        return jsonify(message="Invalid sensor name", data=[]), 400

    with _db_lock:
        results = config["db"].search(query_condition)

    response = {field: [] for field in config["fields"]}
    response["dates"] = []
    for result in results:
        for field in config["fields"]:
            response[field].append(result.get(field, None))
        response["dates"].append(result["date"])

    response_list = [response[field] for field in config["fields"]] + [response["dates"]]
    return jsonify(message="GET DATA RESPONSE", data=response_list)


@app.route("/database/logs.json")
def get_logs():
    logs_path = DATABASE_DIR / "logs.json"
    if not logs_path.is_file():
        return jsonify({"error": "logs.json not found"}), 404
    return send_from_directory(
        directory=str(DATABASE_DIR),
        path="logs.json",
        as_attachment=False,
    )


def format_date(date: Optional[str]) -> Optional[str]:
    if not date:
        return None
    try:
        day_part, hour_part = date.split("T")
        year, month, day = day_part.split("-")
        return f"{day}-{month}-{year} {hour_part}"
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------
def start_server(host: str = "0.0.0.0", port: int = 5000) -> threading.Thread:
    """Start Flask-SocketIO in a daemon thread and return it."""

    def run() -> None:
        options = {
            "host": host,
            "port": port,
            "debug": False,
            "use_reloader": False,
            "allow_unsafe_werkzeug": True,
        }
        try:
            socketio.run(app, **options)
        except TypeError:
            # ``allow_unsafe_werkzeug`` is not available in old
            # Flask-SocketIO releases.
            options.pop("allow_unsafe_werkzeug")
            socketio.run(app, **options)
        except Exception as exc:  # pragma: no cover - depends on environment
            print(f"[RobotDashboard] Web server error: {exc}")

    thread = threading.Thread(target=run, name="RobotDashboardWeb", daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
