class Calcer:
    def __init__(self, fun=None):
        self.fun = lambda: print("not implemented...")
        if fun and callable(fun):
            self.fun = fun

    def execute(self, *args, **kwargs):
        print('executing...')
        return self.fun(*args, **kwargs)


def main():
    x = Calcer()
    x.execute()
    y = Calcer(lambda *x: print(*x))
    y.execute(5, 7, 9)
    z = Calcer(lambda *x: max(x))
    print(z.execute(1))
    print(z.execute(1, 2, 5))
    print(z.execute(1, 2, 5, -5))


if __name__ == '__main__':
    main()
