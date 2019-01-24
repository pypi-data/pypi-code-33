
class Curve:
    """
    Object representing a noise curve

    You can unpack it as a tuple via:
    f, asd = curve

    You can unpack it directly into an argument list:
    plt.loglog(*curve)
    """

    def __init__(self, f, asd):
        """
        Initialize a new Curve object from the frequency range and amplitude spectral density
        :param f: np array representing frequency range
        :param asd: np array representing amplitude spectral density
        """
        self.f = f
        self.asd = asd
        pass

    def __iter__(self):
        return iter((self.f, self.asd))
