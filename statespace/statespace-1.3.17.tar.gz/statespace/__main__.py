import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser('statespace')
    parser.add_argument('-d', '--demo', help='demo', action='store_true')
    args = parser.parse_args()
    if args.demo:
        from classical import Classical
        res = Classical('ekf2')
        print(res.log[-1])
