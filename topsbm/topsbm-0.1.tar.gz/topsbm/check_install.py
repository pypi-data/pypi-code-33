def check():
    from . import TopSBM
    TopSBM().fit([[1, 0], [0, 1]])
    print('topsbm seems to be working!')


if __name__ == '__main__':
    check()
