
class Phrase:
	starters = []
	@classmethod
	def check(cl,ar,kw=''):
		
		return ar in cl.starters

class View_as(Phrase):
	starters = ['view-as']


		
print(View_as.check('view-as'))