import colors as c

def main():
    print(c.clear)
    print(c.base03 + 'Base03' + c.reset, end=' ')
    print(c.base02 + 'Base02' + c.reset, end=' ')
    print(c.base01 + 'Base01' + c.reset, end=' ')
    print(c.base00 + 'Base00' + c.reset, end=' ')
    print(c.base0 + 'Base0' + c.reset, end=' ')
    print(c.base1 + 'Base1' + c.reset, end=' ')
    print(c.base2 + 'Base2' + c.reset, end=' ')
    print(c.base3 + 'Base3' + c.reset, end=' ') 
    print()

    print(c.yellow + 'Yellow' + c.reset, end=' ')
    print(c.orange + 'Orange' + c.reset, end=' ')
    print(c.red + 'Red' + c.reset, end=' ')
    print(c.magenta + 'Magenta' + c.reset, end=' ')
    print(c.violet + 'Violet' + c.reset, end=' ')
    print(c.blue + 'Blue' + c.reset, end=' ')
    print(c.cyan + 'Cyan' + c.reset, end=' ')
    print(c.green + 'Green' + c.reset, end=' ')

    print()

    for count in range(7):
        print(c.random_color() + 'Random' + c.reset, end=' ')
    print()

    print()

    print(c.multi("Multicolored"))
