def get_schema():
    key = "monitoring"
    schema = {
        "description": "Monitoring agent configuration",
        "type": "object",
        "properties": {
            "response-prefix": {
                "description": "",
                "type": "string"
            },
            "onboarding-topic": {
                "description": "",
                "type": "string"
            },
            "location": {
                "description": "",
                "type": "string"
            },
            "room": {
                "description": "",
                "type": "string"
            },
            "device": {
                "description": "",
                "type": "string"
            },
            "gid": {
                "description": "",
                "type": "string"
            },
            "name": {
                "description": "",
                "type": "string"
            },
            "description": {
                "description": "",
                "type": "string"
            },

        },
        "required": ["response-prefix", "onboarding-topic", "location", "room", "device", "gid", "name", "description"]
    }

    return key, schema
