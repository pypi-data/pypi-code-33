
def mount (app):
	@app.route ("/")
	def index (was):
		return was.render ("index.html")
