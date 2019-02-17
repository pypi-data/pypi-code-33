import os
import shutil

def files(path, confirm=False):
    for root, dirs, filenames in os.walk(path):
        if root.endswith('__pycache__'):
            print(f'Removed directory {root}')
            if confirm is True:
                shutil.rmtree(root)
            continue
        for filename in filenames:
            if filename.endswith(".pyc"):
                print(f'Removed compiled file {root}/{filename}')
                if confirm is true:
                    os.remove(root + os.sep + filename)
            if filename.endswith(".pyo"):
                print(f'Removed object file {root}/{filename}')
                if confirm is true:
                    os.remove(root + os.sep + filename)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clean up python source files")
    parser.add_argument(
        "-c",
        "--confirm",
        action="store_true",
        default=False,
        help="Actually perform clean up",
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        default="./",
        action="store",
        help="folder to clean up",
    )

    args = parser.parse_args()

    #print(args)
    files(os.path.abspath('./'), args.confirm)



if __name__ == "__main__":
    main()


