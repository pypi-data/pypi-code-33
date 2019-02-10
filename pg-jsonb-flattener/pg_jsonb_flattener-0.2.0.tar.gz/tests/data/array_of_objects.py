schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "array": {
      "type": "array",
      "items": {
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
}"""


json = """{
  "array": [
    {
      "obj_int": 42,
      "obj_num": 3.141592,
      "obj_str": "pouet",
      "obj_bln": true
    },
    {
      "obj_int": 77,
      "obj_num": 1.618034,
      "obj_str": "toto",
      "obj_bln": false
    }
  ]
}"""


columns = [
    'array__item__index',
    'array__item__obj_int',
    'array__item__obj_num',
    'array__item__obj_str',
    'array__item__obj_bln',
]
