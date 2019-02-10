schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "object": {
      "type": "object",
      "properties": {
        "nested": {
          "type": "object",
          "properties": {
            "obj_int": {"type": "integer"},
            "obj_num": {"type": "number"},
            "obj_str": {"type": "string"},
            "obj_bln": {"type": "boolean"}
          }
        }
      }
    }
  }
}"""


json = """{
  "object": {
    "nested": {
      "obj_int": 42,
      "obj_num": 3.141592,
      "obj_str": "pouet",
      "obj_bln": true
    }
  }
}"""


columns = [
    'object__nested__obj_int',
    'object__nested__obj_num',
    'object__nested__obj_str',
    'object__nested__obj_bln',
]
