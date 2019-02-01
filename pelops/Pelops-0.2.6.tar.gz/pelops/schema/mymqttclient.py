def get_schema():
    key = "mqtt"
    schema = {
        "description": "Mqtt_client configuration",
        "type": "object",
        "properties": {
            "mqtt-address": {
                "description": "URL of mqtt broker",
                "type": "string"
            },
            "mqtt-port": {
                "description": "Port of mqtt broker",
                "type": "integer",
                "minimum": 0,
                "exclusiveMinimum": True
            },
            "log-level": {
                "description": "Log level to be used (optional).",
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            },
            "retain-messages": {
                "description": "Signal mqtt broker that messages should be retained.",
                "type": "boolean"
            },
            "qos": {
                "description": "Set quality of service for subscribe, publish, and last will.",
                "type": "integer",
                "minimum": 0,
                "maximum": 2
            },
            "credentials-file": {
                "description": "File containing the credentials (optional).",
                "type": "string"
            },
            "mqtt-user": {
                "description": "User name for mqtt broker (optional).",
                "type": "string"
            },
            "mqtt-password": {
                "description": "Password for mqtt broker (optional).",
                "type": "string"
            }
        },
        "required": ["mqtt-address", "mqtt-port"]
    }

    return key, schema
