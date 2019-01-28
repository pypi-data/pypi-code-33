from injector import singleton
from lola.utils import lojson
from lola.utils.config import LolaEnv
from lola.utils.injection import injector, Environment

from config import Configuration
from lola.gmail import GmailManager

from lola.trips.parsing.base_parsing import TripEmailParser

def main():
	injector.binder.bind(Environment, 'test', singleton)
	lola_env = Configuration
	injector.binder.bind(LolaEnv, lola_env, singleton)
	filename = lola_env.get('OUTPUT_PATH')

	gmail_manager = GmailManager()
	messages = gmail_manager.scan(lola_env.get('USERNAME'), auth={'password': lola_env.get('PASSWORD')})

	email_parser = TripEmailParser()
	gens = email_parser.parse(messages)

	for g in gens:
	    if g.itinerary:
		with open(filename, mode='w') as file:
		    print lojson.dumps(g.itinerary)
