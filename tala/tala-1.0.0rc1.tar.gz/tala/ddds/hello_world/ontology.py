from tala.model.ontology import DddOntology


class HelloWorldOntology(DddOntology):
    sorts = {"alarm": {}}
    predicates = {
        "current_time": "string",
        "hour_to_set": "integer",
        "minute_to_set": "integer",
        "alarm_hour": "integer",
        "alarm_minute": "integer",
        "alarm_to_select": "alarm",
        "greenwich_mean_time": "string",
        "alarm_image_url": "image",
        "clock_view": "webview",
    }
    individuals = {"work_alarm": "alarm"}
    actions = set([
        "set_time",
        "set_alarm",
        "remove_alarm",
        "select_alarm",
        "snooze",
        "turn_off_alarm",
        "sync_to_internet",
        "update_clock_software",
    ])
