import conftest
from asaprog.simulator import Simulator

if __name__ == "__main__":
    sim = Simulator('COM1')
    sim.run()
