def get_schema():
    key = "monitoring-agent"
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
            "log-level": {
                "description": "Log level to be used.",
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            },
            "timings": {
                "type": "object",
                "description": "intervals in seconds for different tasks",
                "properties": {
                    "restart-onboarding": {
                        "description": "timeout in seconds after which an restart onboarding request is restarted. "
                                       "example: 60 seconds.",
                        "type": "integer"
                    },
                    "send-ping": {
                        "description": "interval in seconds for the scheduler to send a ping message to the "
                                       "monitoring service. 0 deactivates the scheduler. example: 60 seconds.",
                        "type": "integer"
                    },
                    "send-runtime": {
                        "description": "interval in seconds for the scheduler to send a runtime message to the "
                                       "monitoring service. 0 deactivates the scheduler. example: 500 seconds.",
                        "type": "integer"
                    },
                    "send-config": {
                        "description": "interval in seconds for the scheduler to send a config message to the "
                                       "monitoring service. 0 deactivates the scheduler. example: 3600 seconds.",
                        "type": "integer"
                    },
                    "expect-heartbeat": {
                        "description": "maximum interval in seconds until a heartbeat message from the monitoring"
                                       "service should be received. If violated, the agent start the re-onboarding"
                                       "procedures. 0 deactivates this feature. example: 500 seconds.",
                        "type": "integer"
                    }

                },
                "required": ["restart-onboarding", "send-ping", "send-runtime", "send-config", "expect-heartbeat"]
            }

        },
        "required": ["timings", "response-prefix", "onboarding-topic", "location", "room", "device", "gid", "name",
                     "description", "log-level"]
    }

    return key, schema
