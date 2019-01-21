__author__ = "Trey Guest"
__license__ = "GNU"
__version__ = "1.0.0"
__maintainer__ = "Trey Guest"
__email__ = "twguest@students.latrobe.edu.au"
__status__ = "Production"

#    Chromosome is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    Chromosome is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with Chromosome. If not, see <http://www.gnu.org/licenses/>.

import pandas as pd

from matplotlib import pyplot as plt

class Darwin():

    """
    Darwin is an evolutionary companion for streamlined analysis of the
    an evolutionary algorithm
    :param genome: the genome object for analysis
    """

    def __init__(self, genome):

        self.genome = genome

        self.log = pd.DataFrame()
        self.log['Generation'] = genome.stats_generation
        self.log['Strongest'] = genome.stats_strongest
        self.log['Winner'] = genome.stats_winner
        self.log['Mean Cost'] = genome.stats_cost
        self.log['Process Count'] = genome.stats_processes
        self.log['Time'] = genome.stats_time


    def get_log(self):
        """
        Return log dataframe
        """
        return self.log


    def get_ancestors(self, generation = None):

        """
        Returns a past population
        :param generation: generation to return past population from
        """

        if generation == None:
            generation = max(self.genome.log_generation)

        if generation > max(self.genome.log_generation):
            print("Generation Should be in the range: 0-{}".format(max(self.genome.log_generation)))

        elif generation <= max(self.genome.log_generation):
            ancestors = self.genome.log_ancestors[generation]

        return ancestors



    def get_lineage(self):

        """
        Get all past populations
        """

        lineage = self.genome.stats_ancestors

        return lineage

    def plot_cost(self, save = None, save_dir = None):

        """
        A one line plot module to return the cost optimisation function
        :param save: (Bool)
        :param save_dir: desired save_dir w/ file extension
        """

        fig, ax = plt.subplots()

        plt.plot(self.log["Generation"], self.log["Strongest"], 'b')
        plt.plot(self.log["Generation"], self.log["Mean Cost"], '--b')


        ax.set_title("Cost Optimisation")

        ax.set_xlabel("Generations")
        ax.set_ylabel("Cost")

        ax.legend(["Minimum Cost", "Mean Cost"])

        if save == True:
            if save_dir == None:
                plt.savefig("ProcessControl.png")
            elif save_dir != None:
                plt.savefig(save_dir)
            elif save == False:
                pass

    def plot_processes(self, save = None, save_dir = None):

        """
        A one line plot module to return the process optimisation function
        :param save: (Bool)
        :param save_dir: desired save_dir w/ file extension
        """

        fig, ax = plt.subplots(1, 3, figsize = [29,7])

        fig.suptitle("Process Report", fontsize = 18)

        plt.subplot(131)
        plt.plot(self.log["Generation"], self.log["Process Count"])
        plt.title("Generation")
        plt.xlabel("Generations")
        plt.ylabel("Processes")

        plt.subplot(132)
        plt.plot(self.log["Process Count"], self.log["Strongest"], 'b')
        plt.plot(self.log["Process Count"], self.log["Mean Cost"], '--b')
        plt.title("Cost Optimisation")
        plt.xlabel("Processes")
        plt.ylabel("Cost")
        plt.legend(["Minimum Cost", "Maximum Cost"])

        plt.subplot(133)
        plt.plot(self.log["Time"], self.log["Process Count"])
        plt.title("Time of Operation")
        plt.xlabel("Time (s)")
        plt.ylabel("Processes")

        if save == True:
            if save_dir == None:
                plt.savefig("ProcessControl.png")
            elif save_dir != None:
                plt.savefig(save_dir)
            elif save == False:
                pass

if __name__ == "__main__":
    pass
