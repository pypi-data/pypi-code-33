#!/bin/python
# coding: utf-8

##########################################################################################################################################

try:
	import ujson as json
except ImportError:
	import json
from pathlib import Path

from jsoncomment import JsonComment

##########################################################################################################################################

EXAMPLE_PY = Path(__file__)
EXAMPLE_JF = EXAMPLE_PY.with_suffix(".json")

##########################################################################################################################################

def main():
	parser = JsonComment(json)

	with open(EXAMPLE_JF) as file_json:
		parsed_object = parser.load(file_json)

		print("\n", "*"*80, "\n")

		print(parsed_object["item 1"], "\n")
		print(parsed_object["Section/Subsection"], "\n")

		print(parser.dumps(parsed_object), "\n")

		print("\n", "*"*80, "\n")

if __name__ == "__main__":
	main()

##########################################################################################################################################
