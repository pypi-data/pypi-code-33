import re
import html

_REPLACE_WORDS = {
	'intl': 'international',
	'hdg': 'holding',
	'hldg': 'holding',
	'inv': 'investment',
	'inds': 'industries',
	'ind': 'industry',
	'ltd': 'limited',
	'pharm': 'pharmaceutical',
	'pharma': 'pharmaceutical',
	'pharms': 'pharmaceuticals',
	'props': 'properties',
	'res': 'resource',
	'sys': 'systems',
	'tech': 'technology',
	'techs': 'technologies',
	'entm': 'entertainment',
	'corp': 'corporation',
	'comms': 'communications',
	'cap': 'capital'
}

def normalize_word(word):
	"""
	:type word: str
	:rtype: str
	"""
	if word.lower() in _REPLACE_WORDS:
		replacement = _REPLACE_WORDS[word.lower()]
		if word.islower():
			return replacement.lower()
		elif word.isupper():
			return replacement.upper()
		elif word[0].isupper() and word[1:].islower():
			return replacement.capitalize()
		else:
			return replacement
	else:
		return word


def normalize_company_name(name):
	"""
	:type name: str
	:rtype: str
	"""
	try:
		words = re.compile(r'\W+', re.UNICODE).split(html.unescape(str(name)).lower())
		replaced = [normalize_word(word=w) for w in words]
		return ' '.join(replaced).strip()
	except:
		return name