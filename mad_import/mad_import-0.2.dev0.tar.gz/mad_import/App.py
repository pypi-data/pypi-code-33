import pieqt
class App():
	def __init__(self,argv=[]):
		self.app = QApplication(argv)
		self.window = QMainWindow()
		self.layout = QVBoxLayout()
		self.widget = QWidget()
	
	def setApp(self,app):
		self.app = app

	def setWindow(self,window):
		self.window = window

	def setLayout(self,layout):
		self.layout = layout
		self.widget.setLayout(self.layout)
		self.window.setCentralWidget(self.widget)

	def setWidget(self,widget):
		self.widget = widget

	def getApp(self):
		return self.app

	def getWindow(self):
		return self.window

	def getLayout(self):
		return self.layout

	def getWidget(self):
		return self.widget
	
	def run(self):
		self.window.show()
		self.app.exec_()
	
	def addWidget(self,widget):
		self.layout.addWidget(widget)
		self.setLayout(self.layout)
		
