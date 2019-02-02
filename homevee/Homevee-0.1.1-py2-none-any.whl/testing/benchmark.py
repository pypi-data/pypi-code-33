import os
import time
import matplotlib.pyplot as plt

from Functions import gps_data, sensor_data, room_data
from Functions.system_info import get_system_info
from homevee.db_utils import get_database_con

class LineChart():
    def __init__(self, value_map):
        self.value_map = value_map

    def plot(self, save_plot=False, file_name='plot.png'):
        fig, ax = plt.subplots()  # create figure & 1 axis

        xVals = []
        yVals = []

        for x in self.value_map:
            xVals.append(x)
            y =self.value_map[x]
            print x, y
            yVals.append(y)

        ax.scatter(xVals, yVals)

        plt.show()

        if save_plot:
            fig.savefig(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name))

def run_benchmark(function, args, num, name):
    results = {}

    total_time = 0

    print "running: "+name

    for i in range(0, num):
        start_time = time.time()
        function(*args)
        end_time = time.time()

        run_time = float(end_time - start_time)*1000*1000

        results[i+1] = run_time

        total_time += run_time

    LineChart(results).plot(False)

    avg_time = float(total_time)/num

    print name+": " + str(avg_time) + " nanoseconds"

    return avg_time

def do_benchmarks():
    print "running benchmarks..."

    db = get_database_con()

    run_time = run_benchmark(get_system_info, [], 1000, "get_system_info()")

    run_time = run_benchmark(gps_data.get_gps_locations, ["sascha", db], 1000, "get_gps_locations()")

    run_time = run_benchmark(sensor_data.get_sensor_data, ["sascha", "all", "", "", "", db], 1000, "get_sensor_data()")

    run_time = run_benchmark(room_data.get_rooms, ["sascha", db], 1000, "get_rooms()")

if __name__ == "__main__":
    do_benchmarks()