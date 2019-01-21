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

import numpy as np

class Target:

    """
    A target class for controlling the properties of the desired output

    This target class should be defined prior to building a genome
    """

    def __init__(self,
                 target,
                 val_rng = None,
                 decimals = None,
                 exception = None,
                 shape = None):

        """
        :param target: target matrix
        :param rng: lower and upper limits [min, max] of values in trgt matrix
        :param decimals: the number of decimals for seeding/mutation
        :param shape: shape of the seed matrix [x1,y1,(z1)]

        ********** eventually i would like this to include some exceptions but
        ********** thats difficult and time consuming (ie., at this posn, use
        ********** these parameters)
        """

        self.target = target


        if shape == None:
            self.seed_dim = len(self.target.shape)

            if self.seed_dim == 2:

                self.x = self.target.shape[0]
                self.y = self.target.shape[1]

            elif self.seed_dim == 3:

                self.x = self.target.shape[0]
                self.y = self.target.shape[1]
                self.z = self.target.shape[2]

            elif self.seed_dim != 2 and self.seed_dim != 3:
                print("Your target should be a 2D or 3D array")

        elif shape != None:
            self.seed_dim = len(shape)

            if self.seed_dim == 2:
                self.x = shape[0]
                self.y = shape[1]

            if self.seed_dim == 3:
                self.x = shape[0]
                self.y = shape[1]
                self.z = shape[2]

            elif self.seed_dim != 2 and self.seed_dim != 3:
                print("Your target should be a 2D or 3D array")


        if val_rng == None:
            self.val_rng = [min(np.nditer(self.target)), max(np.nditer(self.target))]

            self.val_min = self.val_rng[0]
            self.val_max = self.val_rng[1]
        else:
            self.val_rng = [val_rng[0], val_rng[1]]

            self.val_min = val_rng[0]
            self.val_max = val_rng[1]

        if decimals == None:
            self.decimals = 3
        else:
            self.decimals = decimals


    def details(self):

        """
        print properties of target class
        """

        if len(self.target.shape) == 2:
            print(("Target Size: [{},{}]".format(self.target.shape[0], self.target.shape[1])))
        elif len(self.target.shape) == 3:
            print(("Target Size: [{},{},{}]".format(self.target.shape[0], self.target.shape[1], self.target.shape[2])))

        if self.seed_dim == 2:
            print(("Seed Size: [{},{}]".format(self.x, self.y)))
        elif self.seed_dim == 3:
            print(("Seed Size: [{},{},{}]".format(self.x, self.y, self.z)))

        print(("Target Dimensions: {}".format(len(self.target.shape))))
        print(("Seed Dimensions: {}".format(self.seed_dim)))
        print(("Target Value Range: {} - {}".format(self.val_min, self.val_max)))
        print(("Decimals: {}".format(self.decimals)))


