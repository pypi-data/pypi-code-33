from mqttbcp.helper import requires_keys, targets, register


@register("0")
def status(client, userdata, topic, data):
    return {"name": client.name, "desc": client.name, "type": client.tags}


@register("1")
@requires_keys({"room"})
@targets
def join_room(client, userdata, topic, data):
    room = data["room"]
    qos = data.get("qos")
    qos = qos if qos else 0
    client.rooms.append({room: qos})
    return client.client.subscribe(room, qos)
