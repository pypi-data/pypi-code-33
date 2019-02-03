from opentmi_client import OpenTmiClient, Event


client = OpenTmiClient(port=3000)
client.login("admin", "admin")

# create event and send it
event = Event()
event.priority.level = "info"
event.priority.facility = "result"
event.ref.result = "5697740f956cd2fd35c69062"
event.traceid = "123"
print(event.data)
client.post_event(event)
