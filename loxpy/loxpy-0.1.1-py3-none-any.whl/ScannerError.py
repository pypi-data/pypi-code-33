from . import ErrorState


class ScanError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message

    def report(self):
        print(f'[line {self.line}] Error: {self.message}')
        ErrorState.hadError = True
