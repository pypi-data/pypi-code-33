from parse import *

p = Parser()
p.set_string("""a b c  de
fg
last line""")

w = p.next_word()
p.unread()

while True:
    w = p.next_word()
    if not w:
        break
    print(w)
