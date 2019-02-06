from random import shuffle

name_list = [
  'Dmitri',
  'Henchman 21',
  'Ricky',
  'Henchman 24',
  'Etna',
  'Nipper',
  'Artax',
  'Gmork',
  'Dermott',
  'Hank',
  'Brock',
  'Rocket',
  'Molotov',
  'Wena',
  'H.E.L.P.eR.',
  'Boomer',
  'Atreyu',
  'Brock',
  'Mrs. Z',
  'Goblorse',
  'Roslin',
  'Hotdog',
  'Elle',
  'Ivan',
  'Jonas',
  'Ali',
  'Catclops',
  'Killinger',
  'JJ',
  'Sam',
  'Hunter',
  'Quetzal',
  'Billy',
  'Itztla',
  'Servo',
  'Zeroken',
  'Dr. Septapus',
  'Zero',
  'Manservant',
  'Benji',
  'Brainulo',
  'Lilith',
  'Actual',
  'Dean',
  'Gaius',
  'Ghost Robot',
  'Xolotl',
  'Morla',
  'Oscar',
  'Cody',
  'Rusty',
  'Alexei',
  'Captain Sunshine',
  'Aena',
  'Xiuhtec',
  'Laharl',
  'Kano',
  'Tommy',
  'Kelvin',
  'Truckules',
  'Tommy',
  'Brick Frog',
  'King Gorilla',
  'Hamilton',
  'Beatrix',
  'Petey',
  'Anna',
  'Horace',
  'Red',
  'Dr. Z',
  'Donny',
  'Baudtack',
]

for _ in range(100):
  shuffle(name_list)

def iterpairs(lst, missing=None):
  lstlen = len(lst)
  _ = 0
  while _ < int(lstlen / 2) * 2:
    yield lst[_], lst[_+1]
    _ += 2
  if lstlen % 2 == 1:
    yield lst[-1], missing

name_dict = dict(_ for _ in iterpairs(name_list))
