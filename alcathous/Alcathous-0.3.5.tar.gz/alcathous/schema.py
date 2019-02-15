def get_schema():
    return {
            "data-preparation": {
                "description": "Root node for alcathous specific entries.",
                "type": "object",
                "properties": {
                    "no_data_behavior": {
                        "description": "How should the algorithm react in case of no data.",
                        "type": "string",
                        "enum": ["mute", "last_valid", "empty_message"]
                    },
                    "update_cycle": {
                        "type": "integer",
                        "minimum": 0,
                        "exclusiveMinimum": True,
                        "description": "new values published each ... seconds"
                    },
                    "number_worker": {
                        "type": "integer",
                        "minimum": 0,
                        "exclusiveMinimum": True,
                        "description": "how many worker threads should be spawned to process task queue"
                    },
                    "methods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "unique name for method",
                                    "type": "string"
                                },
                                "topic-pub-suffix": {
                                    "type": "string",
                                    "description": "results are publish to 'datapoints_prefix & topic-pub-suffix'."
                                },
                                "algorithm": {
                                    "type": "string",
                                    "enum": ["avg", "wavg", "count", "min", "max"]
                                },
                                "time_window": {
                                    "description": "use the values from the last ... minutes",
                                    "type": "number",
                                    "minimum": 0,
                                    "exclusiveMinimum": True
                                }
                            },
                            "required": ["time_window", "algorithm", "topic-pub-suffix"],
                            "additionalProperties": False
                        },
                        "additionalProperties": False
                    },
                    "datapoints": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "topic-sub": {
                                    "description": "subscribe to this topic and apply the methods to it",
                                    "type": "string"
                                },
                                "topic-pub-prefix": {
                                    "description": "publish results to this topic",
                                    "type": "string"
                                },
                                "zero_is_valid": {
                                    "description": "0 is valid or rejected",
                                    "type": "boolean"
                                },
                                "methods": {
                                    "description": "comma separated list of one or more strings. each entry must be "
                                                   "represented by a method entry.",
                                    "type": "string",
                                    "pattern": "(\\d+)(,\\s*\\d+)*"
                                }
                            },
                            "required": ["topic-sub", "topic-pub-prefix", "zero_is_valid", "methods"],
                            "additionalProperties": False
                        },
                        "additionalProperties": False
                    }
                },
                "required": ["no_data_behavior", "update_cycle", "number_worker", "methods", "datapoints"],
                "additionalProperties": False
            }
           }