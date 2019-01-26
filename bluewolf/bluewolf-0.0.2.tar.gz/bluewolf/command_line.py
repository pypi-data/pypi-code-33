from bluewolf.bluewolf import run
import sys
def main():
    if len(sys.argv) < 2:
        print("Invalid number of arguments!")
        print("Enter one or more hw ids to start tracking")
        print("Usage: bluewolf 00:11:22:33:44:55 [11:22:33:44:55:66]...")
        sys.exit()
    run()
