from enum import Enum, unique


@unique
class Sex(Enum):
    '''
    Sex:

        >>> from eggit.enums import Sex
        >>> Sex.male
        <Sex.male: (1,)>
        >>> Sex.male.value
        (1,)
        >>> Sex.male.name
        'male'
        >>>

    '''

    unknown = 0
    male = 1
    female = 2
