import majka

@profile
def my_func():
  m = majka.Majka('/home/pulc/Projekty/linker/cs.w-lt')
  #m.tags = False
  #x = m.find('nejhloub')
  #print(x)
  for i in range(1,100000):
    m.find('hloupne')
  del m

if __name__ == '__main__':
  my_func()
