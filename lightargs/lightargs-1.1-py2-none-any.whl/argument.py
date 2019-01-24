from .unknown_argument import UnknownArgument
from .wrong_parameters import WrongParameters



class _Argument:

    
    def __init__(self,
                 command,
                 function,
                 nb_args=0,
                 args_label=None,
                 defaults=None,
                 man="",
                 category=None):

        if defaults is not None and len(defaults) > nb_args:
            raise Exception(
                str(command) +
                ": number of default argument higher than number of arguments")
        
        self.command = command
        self._function = function
        self._nb_args = nb_args
        self._defaults = defaults
        self.man = man
        self.category = category
        self.args_label = args_label

        
    def min_nb_arguments(self):

        if self._defaults is None:
            return self._nb_args
        return self._nb_args - len(self._defaults)

    
    def max_nb_arguments(self):

        return self._nb_args

    
    def accepted_nb_of_arguments(self, nb):
        return (nb >= self.min_nb_arguments()
                and nb <= self.max_nb_arguments())

    
    def execute(self, args):

        if not self.accepted_nb_of_arguments(len(args)):
            error = "incorrect number of arguments. " + str(self.command)
            min_, max_ = self.min_nb_arguments(), self.max_nb_arguments()
            if min_ != max_:
                error + " accepts between " + \
                    str(min_) + " and " + str(max_) + " arguments"
            elif min_ == 0:
                error += " takes no arguments"
            else:
                error += " takes " + str(min_) + " argument(s)"
            if self._defaults:
                error += " (defaults : " + \
                    ",".join([str(d) for d in self._defaults]) + ")"
            raise WrongParameters(error)
        
        passing_args = args
        if len(passing_args) < self._nb_args:
            for d in self._defaults:
                passing_args.append(d)
                if len(passing_args) == self._nb_args:
                    break
        return self._function(*passing_args)
