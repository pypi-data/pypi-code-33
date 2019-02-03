import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class twiss(object):
        """
        twiss class
        Author ttydecks CERN BE-OP-LHC

        a = twiss(filename)

        filename is a string with the path to the twiss file
        a will contain many different fields that are placed
        in the header of the twiss file but most prominently
        it contains a dictionary with all columns that gives
        acces to the data.

        importing:
        from twiss import twiss

        Examples:
        a = twiss('ptc.twiss')

        print(a.ENERGY)
        Out: 175

        print(a.data['BETX'][0])
        Out: 121.164

        a.plot('S','BETX')
        """

        def __init__(self, filename):
                super().__init__()
                self.data = dict()
                self._readData(filename)
                return

        def _readData(self, filename):
                try:
                        with open(filename) as f:
                                self._content = f.readlines()
                        self._content = [x.split() for x in self._content]
                        for i, line in enumerate(self._content):
                                if line[0] == '*':
                                        self._ind = i
                                        break
                                if line[2] == '%le':
                                        if '-' in self._content[i][1]:
                                                self._content[i][1] = self._content[i][1].replace('-', '_')
                                        executable = 'self.'+self._content[i][1]+' = '+self._content[i][3]
                                        exec(executable)
                                if 's' in line[2]:
                                        helpstring = ''
                                        for el in self._content[i][3:]:
                                                helpstring += el
                                        executable = 'self.'+self._content[i][1]+' = "'+helpstring+'"'
                                        exec(executable)
                        self.header = self._content[self._ind][1:]
                        self._rawData = np.array(self._content[self._ind+2:])
                        for i, element in enumerate(self._content[self._ind]):
                                if self._content[self._ind+1][i] == '%s':
                                        self.data[element] = np.array([x[1:-1] for x in self._rawData[:, i-1]])
                                if self._content[self._ind+1][i] in ['%le', '%d']:
                                        self.data[element] = np.array([float(x) for x in self._rawData[:, i-1]])
                        self.data = pd.DataFrame(self.data, columns=self.header)
                except FileNotFoundError:
                        print('cannot do anything because the filename appears to be wrong! File not found...')
                        raise(FileNotFoundError)

        def plot(self, el1, el2):
                try:
                        self.fig, self.ax = plt.subplots()
                        self.ax.plot(self.data[el1], self.data[el2])
                        self.ax.set_xlabel(el1)
                        self.ax.set_ylabel(el2)
                        plt.show()
                except KeyError:
                        print('column not found')

        def inquire(self, pos, val):
                """
                inquire the value of val column at position pos. val and pos
                must be strings. returns a list of values for all positions 
                containing the string pos.
                """
                try:
                        return [a for (a, el) in zip(self.data[val], self.data['NAME']) if pos in el]
                except KeyError:
                        print('could not resolve either pos or val, should be strings and val should correspond to existing column')
                        return []


if __name__ == '__main__':
        print('This is a test of twiss.py.')
        print('creating short dummyTwiss.file...')
        with open('dummyTwiss.file', 'w') as f:
                string = '@ val1    %le    1\n'
                string += '@ val2   %le    2\n'
                string += '@ val3   %s    asdf\n'
                string += '* col1  col2  col3\n'
                string += '$ %s   %le   %d\n'
                string += '"teststring"   1    12\n'
                string += '"anotherstring"   2   13\n'
                string += '"yetstring"    3    14\n'
                f.write(string)
        test = twiss('dummyTwiss.file')
        print('The header is:')
        print(test.header)
        print('The values before header are:')
        print(test.val1)
        print(test.val2)
        print(test.val3)
        print('The data found is:')
        print(test.data)
        print('and now a plot should appear')
        test.plot('col2', 'col3')
