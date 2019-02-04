try:
    import os
    path = os.path.abspath('installer.py')
    print(path)
    dath = path.split('\\')
    print(dath)
    tel = len(dath) - 1
    let = tel - 1
    if dath[let] == 'Lib' and dath[tel] == 'installer.py':
        p = True
    else:
        p = False
    print(p)
except ImportError:
    raise SystemExit
if p == True:
    #installer
    f = open('wifi.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('wifi.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('slib.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('slib.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('rekenen.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('rekenen.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('tlib.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('tlib.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('tklib.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('tklib.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('errors.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('errors.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('system.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('system.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('infunc.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('infunc.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('tijd.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('tijd.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
    #installer
    f = open('datetijd.ins', 'r')
    data = f.read()
    data = data.split('\n')
    print(data)

    w = open('datetijd.py', 'w+')

    for i in range(0, len(data)):
        w.write(data[i])
        w.write('\n')
        print(data[i])

    f.close()
    w.close()
else:
    class FileNotRightPosError(Exception):
        'FileNotRightPosError'
    raise FileNotRightPosError('be shure all the files are in the lib and out the map\
\na solution is copy the files and paste them in the python lib\
')



