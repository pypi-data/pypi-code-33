import math


def solve_help():
    inp = input()
    if inp.count(' ') >= 1:
        return inp.split()
    else:
        return [inp[:] for i in range(1)]


def solve():
    sp_1 = solve_help()
    sp = []
    for elem in sp_1:
        sp.append(float(elem))
    if len(sp) == 0 or len(sp) > 3:
        print('incorrect input')
        return
    elif len(sp) == 1:
        if sp[0] == 0:
            result = 'all'
            print(result)
            return
        else:
            result = 'None'
            print(result)
            return
    elif len(sp) == 2:
        b = sp[0]
        c = sp[1]
        if c == 0:
            result = 0.0
            print(result)
            return
        result = (c / b) * -1
        print(result)
        return
    b = sp[1]
    a = sp[0]
    c = sp[2]
    D_1 = b ** 2 - 4 * a * c
    if D_1 < 0:
        print('None')
        return
    D = math.sqrt(D_1)
    result_1 = (-b + D) / (2 * a)
    result_2 = (-b - D) / (2 * a)
    if result_1 == result_2:
        print(result_1)
        return
    print(result_1, result_2)
    return

