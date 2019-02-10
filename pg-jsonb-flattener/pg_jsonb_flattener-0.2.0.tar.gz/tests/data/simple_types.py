schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "integer": {"type": "integer"},
    "number": {"type": "number"},
    "string": {"type": "string"},
    "boolean": {"type": "boolean"}
  }
}"""


json = """{
  "integer": 42,
  "number": 3.141592,
  "string": "pouet",
  "boolean": false
}"""


columns = [
    'integer',
    'number',
    'string',
    'boolean',
]
