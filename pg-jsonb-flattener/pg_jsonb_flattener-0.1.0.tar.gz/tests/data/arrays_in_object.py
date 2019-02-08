schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "object": {
      "type": "object",
      "properties": {
        "int_arr": {
          "type": "array",
          "items": {"type": "integer"}
        },
        "num_arr": {
          "type": "array",
          "items": {"type": "number"}
        },
        "str_arr": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  }
}"""


json = """{
  "object": {
    "int_arr": [42, 77, 1664],
    "num_arr": [3.141592, 1.618034, 37.2],
    "str_arr": ["pouet", "foo", "bar"]
  }
}"""


columns = [
    'object__int_arr__item',
    'object__int_arr__item__index',
    'object__num_arr__item',
    'object__num_arr__item__index',
    'object__str_arr__item',
    'object__str_arr__item__index',
]
