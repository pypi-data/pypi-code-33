#!/bin/python
# coding: utf-8

##########################################################################################################################################

try:
	import ujson as json
except ImportError:
	import json

from .wrapper import GenericWrapper

##########################################################################################################################################

# Comments
COMMENT_PREFIX = ("#",";","//")
MULTILINE_START = "/*"
MULTILINE_END = "*/"

# Data strings
LONG_STRING = '"""'

##########################################################################################################################################

class JsonComment(GenericWrapper):
	def __init__(self, wrapped=json):
		super().__init__(wrapped)

	# Loads a JSON string with comments
	def loads(self, jsonsc, *args, **kwargs):
		# Splits the string in lines
		lines = jsonsc.splitlines()
		# Process the lines to remove commented ones
		jsons = self._preprocess(lines)
		# Calls the wrapped to parse JSON
		return self.wrapped.loads(jsons, *args, **kwargs)

	# Loads a JSON opened file with comments
	def load(self, jsonf, *args, **kwargs):
		# Reads a text file as a string
		# Process the readed JSON string
		return self.loads(jsonf.read(), *args, **kwargs)

	# Opens a JSON file with comments
	# Allows a default value if loading or parsing fails
	def loadf(self, path, *args, default = None, **kwargs):
		# Preparing the default
		json_obj = default

		# Opening file in append+read mode
		# Allows creation of empty file if non-existent
		with open( path, mode="a+", encoding="UTF-8" ) as jsonf:
			try:
				# Back to file start
				jsonf.seek(0)
				# Parse and load the JSON
				json_obj = self.load(jsonf, *args, **kwargs)
			# If fails, default value is kept
			except ValueError:
				pass

		return json_obj

	# Saves a JSON file with indentation
	def dumpf(self, json_obj, path, *args, indent=4, **kwargs):
		# Opening file in write mode
		with open( path, mode="w", encoding="UTF-8" ) as jsonf:
			# Dumping the object
			json.dump(json_obj, jsonf, *args, indent=indent, **kwargs)

	def _preprocess(self, lines):
		standard_json = ""
		is_multiline = False
		keep_trail_space = 0

		for line in lines:
			# 0 if there is no trailing space
			# 1 otherwise
			keep_trail_space = int(line.endswith(" "))

			# Remove all whitespace on both sides
			line = line.strip()

			# Skip blank lines
			if len(line) == 0:
				continue

			# Skip single line comments
			if line.startswith(COMMENT_PREFIX):
				continue

			# Mark the start of a multiline comment
			# Not skipping, to identify single line comments using multiline comment tokens, like
			# /***** Comment *****/
			if line.startswith(MULTILINE_START):
				is_multiline = True

			# Skip a line of multiline comments
			if is_multiline:
				# Mark the end of a multiline comment
				if line.endswith(MULTILINE_END):
					is_multiline = False
				continue

			# Replace the multi line data token to the JSON valid one
			if LONG_STRING in line:
				line = line.replace(LONG_STRING, '"')

			standard_json += line + " " * keep_trail_space

		# Removing non-standard trailing commas
		standard_json = standard_json.replace(",]", "]")
		standard_json = standard_json.replace(",}", "}")

		return standard_json

##########################################################################################################################################
