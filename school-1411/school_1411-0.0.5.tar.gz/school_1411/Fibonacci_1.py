def fib_1():
    print('Input the number:)')
    num = int(input())
    print(1, end=' ')
    a = 0
    b = 0
    c = 1
    for i in range(num - 1):
        a = b
        b = c
        c = a + b
        print(c, end=' ')
