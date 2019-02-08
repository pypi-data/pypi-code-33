import PySide2
import PySide2.QtCore
from PySide2.QtGui import*
from PySide2.QtWidgets import*

QApplication = PySide2.QtWidgets.QApplication
QTextEdit = PySide2.QtWidgets.QTextEdit
QLabel = PySide2.QtWidgets.QLabel
QPushButton = PySide2.QtWidgets.QPushButton
QCheckBox = PySide2.QtWidgets.QCheckBox
QMainWindow = PySide2.QtWidgets.QMainWindow
QVBoxLayout = PySide2.QtWidgets.QVBoxLayout
QWidget = PySide2.QtWidgets.QWidget

def user_function():
	print("I am a user function")
callbacks = []
def run():
	global callbacks
	for callback in callbacks:
		callback()
def callback_user_functions():
	global callbacks
	for callback in callbacks:
		callback()
def add_function(function):
	global callbacks
	callbacks.append(function)
def main():
	print("Enter your code below!!!")
	global callbacks
	add_function(user_function)
	run()
	#callback_user_functions()

if __name__ == "__main__":
	main()
