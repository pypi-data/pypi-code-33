from typing import List
import math
import os
import datetime

# Global variables for the class
_M: int = 2147483647
_A: int = 16807
_B: int = 127773
_C: int = 2836
_outputDirectory: str = "output/instances"
_now = datetime.datetime.now()
_todayFolder = f"{_now.year}{_now.month}{_now.day}"

class ProblemGenerator:
    """Generate instances of JSSP"""
    def __init__(self, nb_machines: int, nb_jobs: int, mseed: int, tseed: int):
        self.Times: List[List[int]] = [[0]*nb_machines for _ in range(nb_jobs)]
        self.Machines: List[List[int]] = [[0]*nb_machines for _ in range(nb_jobs)]
        self.machine_seed: List[int] = [mseed]
        self.time_seed: List[int] = [tseed]
        self.mseed: int = mseed
        self.tseed: int = tseed

        for i in range(0, nb_jobs):
            for j in range(0, nb_machines):
                self.Times[i][j] = self.unif(self.time_seed, 1, 99)

        for i in range(0, nb_jobs):
            for j in range(0, nb_machines):
                self.Machines[i][j] = j+1

        for i in range(0, nb_jobs):
            for j in range(0, nb_machines):
                k2: int = self.unif(self.machine_seed, j, nb_machines-1)
                # Swap of variables
                self.Machines[i][j], self.Machines[i][k2] = self.Machines[i][k2], self.Machines[i][j]

    def save(self) -> None:
        """
        Save file with the params of the object.
        :return:
        """
        content:str = f"{self.mseed},{self.tseed}\n" \
                        f"{len(self.Times)},{len(self.Times[0])},{len(self.Machines[0])}\n"

        content += self.fillContentByMatrix(self.Times)
        content += f"MACHINES\r\n"
        content += self.fillContentByMatrix(self.Machines)

        self.saveFile(content, f"{len(self.Times)}{len(self.Times)}-{self.mseed}-{self.tseed}")

    @staticmethod
    def fillContentByMatrix(matrixOfElements: List[List[int]]) -> str:
        """
            Fill the string in the argument with the values in the matrix
            :param self:
            :param matrixOfElements:
            :param content:
            :return:
        """
        content: str = ""
        for i in range(0, len(matrixOfElements)):
            for j in range(0, len(matrixOfElements[0])):
                content += f"{matrixOfElements[i][j]} "
            content += "\r\n"
        return content

    @staticmethod
    def unif(seed: List[int], low: int, high: int) -> int:
        """
            :param seed: Array of ints
            :param low: lower-bound
            :param high: upper-bound
            :return:
        """
        value01: float
        k = seed[0] // _B
        seed[0] = (_A * (seed[0] % _B)) - (k * _C)

        if seed[0] < 0:
            seed[0] = seed[0] + _M
        value01 = seed[0] / float(_M)

        return int(low + math.floor(value01 * (high - low + 1)))

    @staticmethod
    def saveFile(content: str, fileName: str):
        """
        Save the given content with the specified fileName parameter
        :param content:
        :param fileName:
        :return:
        """
        if not os.path.exists(_outputDirectory):
            os.makedirs(_outputDirectory)

        if not os.path.exists(f"{_outputDirectory}/{_todayFolder}"):
            os.makedirs(f"{_outputDirectory}/{_todayFolder}")

        file = open(f"./{_outputDirectory}/{_todayFolder}/{fileName}.txt","w+")
        file.write(content)
        file.close()

# 15, 15, 735213678,2847575160
def createInstance(nb_machines: int, nb_jobs: int, mseed: int, tseed: int):
    temp = ProblemGenerator(nb_machines, nb_jobs, mseed, tseed)
    temp.save()

def createInstances(list: List):
    for i in list:
        temp = ProblemGenerator(i[0], i[1], i[2], i[3])
        temp.save()
