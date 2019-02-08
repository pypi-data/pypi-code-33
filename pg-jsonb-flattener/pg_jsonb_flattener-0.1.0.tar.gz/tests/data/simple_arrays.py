schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
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
}"""


json = """{
  "int_arr": [42, 77, 1664],
  "num_arr": [3.141592, 1.618034, 37.2],
  "str_arr": ["pouet", "foo", "bar"]
}"""


columns = [
    'int_arr__item',
    'int_arr__item__index',
    'num_arr__item',
    'num_arr__item__index',
    'str_arr__item',
    'str_arr__item__index',
]
