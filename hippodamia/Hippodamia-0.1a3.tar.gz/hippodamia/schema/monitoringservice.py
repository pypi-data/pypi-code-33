def get_schema():
    schema = {
        "monitoringservice": {
            "description": "Hippodamia observes the state of all registered microservices (aka watch dog).",
            "type": "object",
            "properties": {
                "topics": _topics(),
                "timings": _timings(),
                "expected-services": _expected_services(),
                "mongodb": _mongodb(),
                "webpage": _webpage()
            },
            "required": ["topics", "timings", "expected-services", "mongodb", "webpage"],
            "additionalProperties": False
        }
    }
    return schema


def _topics():
    schema = {
        "type": "object",
        "description": "all topics for the monitoring services",
        "properties": {
            "onboarding-request": {
                "type": "string",
                "example": "/test/hippodamia/onboarding/request",
                "description": "hippodamia listens on this topic for new onboarding request"
            },
            "activity-base": {
                "type": "string",
                "example": "/test/hippodamia/incoming/",
                "description": "this topic will be used as base for each registered service. e.g .../incoming/1/ping"
            },
            "command-end": {
                "type": "string",
                "example": "/test/hippodamia/command/end",
                "description": "end command messages are published to this topic"
            },
            "command-reonboarding": {
                "type": "string",
                "example": "/test/hippodamia/command/reonboarding",
                "description": "reonboarding request are published to this topic"
            },
            "command-ping-on-request": {
                "type": "string",
                "example": "/test/hippodamia/command/ping_on_request",
                "description": "spontaneous ping messages are requested via this topic"
            },
            "command-config-on-request": {
                "type": "string",
                "example": "/test/hippodamia/command/command/config_on_request",
                "description": "spontaneous config messages are requested via this topic"
            },
            "command-runtime-on-request": {
                "type": "string",
                "example": "/test/hippodamia/command/command/runtime_on_request",
                "description": "spontaneous runtime messages are requested via this topic"
            },
            "heartbeat": {
                "type": "string",
                "example": "/test/hippodamia/heartbeat",
                "description": "heartbeat is published via this topic"
            }
        },
        "required": ["onboarding-request", "activity-base", "command-end", "command-reonboarding", "command-ping-on-request",
                     "command-config-on-request", "command-runtime-on-request", "heartbeat"],
        "additionalProperties": False
    }
    return schema


def _timings():
    schema = {
        "type": "object",
        "description": "all timings for the monitoring service",
        "properties": {
            "onboarding_timeout": {
                "type": "integer",
                "example": "60",
                "description": "seconds * 2 to be waited until an onboarding request should have been processed and a response been recevied"
            },
            "wait_for_message_timeout": {
                "type": "integer",
                "example": "180",
                "description": "seconds - if no message has been received for this period, the service is considered to be inactive"
            },
            "deactivation_timeout": {
                "type": "integer",
                "example": "360",
                "description": "seconds - an inactive service becomes a stopped service after this time span"
            },
            "heartbeat_interval": {
                "type": "integer",
                "example": "60",
                "description": "seconds - send heartbeat to all connected services"
            },
            "archivation_timeout": {
                "type": "integer",
                "example": "86400",
                "description": "seconds - a stopped service is archived after this time span."
            }
        },
        "required": ["onboarding_timeout", "wait_for_message_timeout", "deactivation_timeout",
                     "heartbeat_interval", "archivation_timeout"],
        "additionalProperties": False
    }
    return schema


def _expected_services():
    schema = {
        "type": "object",
        "description": "pre-configure which services are expected to be onboarded",
        "properties": {
            "enforcement": {
                "type": "string",
                "example": "none",
                "description": "spontaneously appearing services are either [none]-accepted, [ignore]-ignored, "
                               "[strict]-leads to a error log entry",
                "enum": ["none", "ignore", "strict"]
            },
            "services": {
                "type": "array",
                "description": "list of expected services",
                "items": {
                    "type": "object",
                    "properties": {
                        "gid": {
                            "type": ["string", "integer"],
                            "example": "1",
                            "description": "gid of the service"
                        },
                        "name": {
                            "type": "string",
                            "example": "Thermostat GUI",
                            "description": "name of the service (optional)"
                        },
                        "location": {
                            "type": "string",
                            "example": "vienna",
                            "description": "location of the service (optional)"
                        },
                        "room": {
                            "type": "string",
                            "example": "living room",
                            "description": "room of the service (optional)"
                        },
                        "device": {
                            "type": "string",
                            "example": "thermostat",
                            "description": "device the service is running on (optional)"
                        },
                        "necessity": {
                            "type": "string",
                            "example": "required",
                            "description": "configure if the expected service is [required] or [optional]",
                            "enum": ["required", "optional"]
                        }
                    },
                    "required": ["gid", "necessity"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["enforcement", "services"],
        "additionalProperties": False
    }
    return schema


def _mongodb():
    schema = {
        "type": "object",
        "description": "persistance database",
        "properties": {
            "credentials-file": {
                "type": "string",
                "example": "~/credentials.yaml",
                "description": "credentials for mongodb"
            },
            "mongodb-address": {
                "type": "string",
                "example": "localhost",
                "description": "host name"
            },
            "mongodb-port": {
                "type": "integer",
                "example": 21017,
                "description": "port"
            },
            "database": {
                "type": "string",
                "example": "hippodamia",
                "description": "database name"
            },
            "mongodb-user": {
                "description": "User name for mongodb",
                "type": "string"
            },
            "mongodb-password": {
                "description": "Password for mongodb",
                "type": "string"
            },
            "log-level": {
                "type": "string",
                "example": "DEBUG",
                "description": "log level for mongodb client related messages",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            }
        },
        "required": ["mongodb-address", "mongodb-port", "database", "log-level"],
        "additionalProperties": False
    }
    return schema


def _webpage():
    schema = {
        "type": "object",
        "description": "web page to view the state of the services",
        "properties": {
            "port": {
                "type": "integer",
                "example": "6060",
                "description": "web server port"
            },
            "webpage-user": {
                "description": "User name for webpage",
                "type": "string"
            },
            "webpage-password": {
                "description": "Password for webpage",
                "type": "string"
            },
            "credentials-file": {
                "type": "string",
                "example": "~/credentials.yaml",
                "description": "if credentials are set, website is password protected"
            },
            "log-level": {
                "type": "string",
                "example": "DEBUG",
                "description": "log level for mongodb client related messages",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            }
        },
        "required": ["port", "log-level"],
        "additionalProperties": False
    }
    return schema
