import pelops.schema.mymqttclient
import pelops.schema.mylogger


def get_schema(sub_schema):
    schema = {
        "$schema": "http://json-schema.org/draft-06/schema#",
        "title": "Configuration for pelops mqtt microservices.",
        "type": "object",
        "properties": sub_schema,
        "required": []
    }

    for k in sub_schema.keys():
        schema["required"].append(k)

    key, sub = pelops.schema.mymqttclient.get_schema()
    schema["properties"][key] = sub
    schema["required"].append(key)

    key, sub = pelops.schema.mylogger.get_schema()
    schema["properties"][key] = sub
    schema["required"].append(key)

    return schema
