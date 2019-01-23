import sys

from .commander import Commander


def main():
    try:
        output = Commander().handle(*sys.argv[1:])
    except (RuntimeError, ValueError) as error:
        output = f"Error: {str(error)}"
    if output:
        print(output)


if __name__ == '__main__':
    main()
