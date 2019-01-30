class ContinentLoader(object):
    def __init__(self):
        self.continents = []

    def load_continents(self, path="../../res/continents.txt"):
        file = open(path, 'r')
        lines = []
        line = file.readline()
        while len(line) > 0:
            lines.append(line)
            line = file.readline()
        file.close()

        continents = []
        continent = []
        for line in lines:
            continent_string = line.split(",")
            for country in continent_string:
                continent.append(int(float(country)))
            continents.append(continent)
            continent = []

        return continents


if __name__ == '__main__':
    print(ContinentLoader().load_continents())
