



HTML_TAG_TYPE_STRUCTURE = 1
HTML_TAG_TYPE_INLINE_CONTENT = 2
HTML_TAG_TYPE_INLINE_ALL = 3




_HTML_ESCAPE_TABLE = {
	"&": "&amp;",
	"\"": "&quot;",
	"'": "&apos;",
	">": "&gt;",
	"<": "&lt;",
}

def htmlEscape(text:str):
	return "".join(_HTML_ESCAPE_TABLE.get(c, c) for c in text)
#





