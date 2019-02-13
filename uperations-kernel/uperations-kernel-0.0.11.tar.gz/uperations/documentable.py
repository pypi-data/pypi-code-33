
class Documentable:

    @classmethod
    def name(cls):
        """
        Return the name of the documentable

        Return
            Documentable: The class name of the documentable
        """
        return cls

    @classmethod
    def description(cls):
        """
        Return the description of the documentable

        Return
            str: Name of the documentable
        :return:
        """
        return str(cls)