schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "nested_arrays": {
      "type": "array",
      "items": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  }
}"""


json = """{
  "nested_arrays": [
    ["abc", "def"],
    ["tuw", "xyz"]
  ]
}"""


columns = [
    'nested_arrays__item__index',
    'nested_arrays__item__item',
    'nested_arrays__item__item__index',
]
