# src/pymock/constants/schemas.py
CONFIG_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "server": {
            "type": "object",
            "properties": {"host": {"type": "string"}, "port": {"type": "integer", "minimum": 0, "maximum": 65535}},
        },
        "endpoints_path": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["server", "endpoints_path"],
}
