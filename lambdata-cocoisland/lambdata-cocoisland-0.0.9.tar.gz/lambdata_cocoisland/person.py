class Person:
  '''
  p1 = Person("Apple",18)
  p1.myfunc()
  '''
  def __init__(self, name, age):
    self.name = name
    self.age = age

  def myfunc(self):
    print("Hello my name is " + self.name)

