schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "integer": {"type": "integer"},
    "number": {"type": "number"},
    "string": {"type": "string"}
  }
}"""


json = """{
  "integer": 42,
  "number": 3.141592,
  "string": "pouet"
}"""


columns = [
    'integer',
    'number',
    'string',
]
