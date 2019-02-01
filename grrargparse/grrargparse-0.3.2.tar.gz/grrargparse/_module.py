from .grr_logging import Logger
from .grr_logging import log
import abc
from ._grrargparse_helpers import query_yes_no, capture_file, capture_text, get_persistence_store

class GrrArgument(object):

    YN = 0
    YN_FILE = 1
    FILE = 2
    FOLDER = 3
    MULTI_FILE = 4
    TEXT = 5
    MULTI_TEXT = 6





    def __init__(self, type, question, var_name, default_yn="Yes", must_exist=False, must_not_exist=False, default_string=None, ask_for_titles=False, mode=102):

        self.type = type

        self.question = question
        self.var_name = var_name
        self.default_yn = default_yn
        self.must_exist = must_exist
        self.must_not_exist = must_not_exist
        self.default_string = default_string
        self.ask_for_titles = ask_for_titles
        self.mode = mode

    def ask_interactively(self, args):
        if (self.mode == 102):
            return False
        if (self.mode == 101):
            return True
        if (self.var_name not in args and self.mode == 103):
            return True

        return False


class APIModule(object):

    DEFAULT_Y = "Yes"
    DEFAULT_N = "No"

    INTERACTIVE_ALWAYS = 101
    INTERACTIVE_NEVER = 102
    INTERACTIVE_IF_NOT_SPECIFIED = 103

    def __init__(self, subparser, args=None):

        if self.name is None:
            self.name = self.__class__.__name__
        self.steps = []
        self.help = ""
        self.args = {}
        self.subparser = subparser.add_parser(self.name,help=self.help)

        if args is not None:
            self.update_args(args)

    def __eq__(self, other):
        return self.name == other.name

    def preprocess(self):
        self.add_arguments()

    # only populate if variable hasn't already been set in constructor
    def add_yn_option(self, letter,word,question, var_name,help, default_yn=DEFAULT_Y, interactive_mode=INTERACTIVE_ALWAYS):
        if default_yn==self.DEFAULT_Y:
            act = "store_false"
        else:
            act = "store_true"
        self.subparser.add_argument("-"+letter, "--"+word, action=act, dest=var_name,help=help,required=False)

        n = GrrArgument(GrrArgument.YN,question,var_name,default_yn = default_yn, mode=interactive_mode)
        self.steps.append(n)

    def add_yn_file_option(self, letter,word,question, var_name, help, default_yn=DEFAULT_Y, default_file=None, interactive_mode=INTERACTIVE_ALWAYS):
        self.subparser.add_argument("-"+letter, "--"+word, dest=var_name,metavar="<"+var_name+">",help=help,required=False)

        n = GrrArgument(GrrArgument.YN_FILE,question,var_name,default_yn = default_yn, default_string = default_file, mode=interactive_mode)
        self.steps.append(n)


    def add_single_file_option(self, letter, word, question, var_name, help, must_exist=False, must_not_exist=False, default_file=None, interactive_mode=INTERACTIVE_ALWAYS):

        self.subparser.add_argument("-"+letter, "--"+word, dest=var_name,help=help,required=False)

        n = GrrArgument(GrrArgument.FILE,question,var_name,must_exist=must_exist,must_not_exist=must_not_exist, default_string = default_file, mode=interactive_mode)
        self.steps.append(n)


    def add_folder_option(self, letter, word, question, var_name, help, must_exist=False, must_not_exist=False, default_folder=None, interactive_mode=INTERACTIVE_ALWAYS):
        self.subparser.add_argument("-"+letter, "--"+word, dest=var_name,help=help, required=False)

        n = GrrArgument(GrrArgument.FOLDER, question, var_name, must_exist=must_exist, must_not_exist=must_not_exist, default_string = default_folder, mode=interactive_mode)
        self.steps.append(n)


    def add_multi_file_option(self, letter, word,  question, var_name, help, default_yn=DEFAULT_Y, must_exist=False, must_not_exist=False, ask_for_titles=False, interactive_mode=INTERACTIVE_ALWAYS):
        if ask_for_titles:
            self.subparser.add_argument("-" + letter, "--" + word, dest=var_name, nargs=2, metavar=('<name>','<title>'),
                                        help=help, action='append', required=False)
        else:
            self.subparser.add_argument("-"+letter, "--"+word, dest=var_name, metavar="<"+var_name+">", help=help,action='append', required=False)

        n = GrrArgument(GrrArgument.MULTI_FILE, question, var_name, default_yn=default_yn, must_exist=must_exist, must_not_exist=must_not_exist, ask_for_titles=ask_for_titles, mode=interactive_mode)
        self.steps.append(n)


    def add_text_option(self, letter, word, question, var_name, help, default_text=None, interactive_mode=INTERACTIVE_ALWAYS):
        self.subparser.add_argument("-"+letter, "--"+word, dest=var_name, metavar="<"+var_name+">",help=help, required=False)

        n = GrrArgument(GrrArgument.TEXT, question, var_name, default_string=default_text, mode=interactive_mode)
        self.steps.append(n)




    def add_multi_text_option(self, letter, word, question, var_name, help, default_yn=DEFAULT_N, interactive_mode=INTERACTIVE_ALWAYS):
        self.subparser.add_argument("-" + letter, "--" + word, dest=var_name, metavar="<" + var_name + ">", help=help,
                                    action='append', required=False)

        n = GrrArgument(GrrArgument.MULTI_TEXT, question, var_name, default_yn=default_yn, mode=interactive_mode)
        self.steps.append(n)

    def update_args(self, args):
        assert isinstance(args,dict)
        self.args.update(args)

    def _populate(self):


        for l in self.steps:

            assert isinstance(l, GrrArgument)

            # only process if args doesn't already have the key
            if l.var_name+"_global" not in self.args.keys():

                if(l.ask_interactively(self.args)):


                    ######## YN OPTION ###########
                    if l.type==GrrArgument.YN:
                        a = query_yes_no(l.question,l.default_yn)
                        self.args[l.var_name] = a



                    ######## YN FILE OPTION ###########
                    elif l.type==GrrArgument.YN_FILE:
                        if query_yes_no(l.question, l.default_yn):
                            q = "Enter filename for "+l.question+": "
                            print(q)
                            f = capture_file(must_exist=True, must_be_file=True)
                            self.args[l.var_name] = f
                        else:
                            self.args[l.var_name] = None



                    ######## FILE OPTION ###########
                    elif l.type==GrrArgument.FILE:
                        question = "Enter a "+l.question
                        print(question)
                        f = capture_file(must_exist=l.must_exist, must_not_exist=l.must_not_exist, must_be_file=True, default=l.default_string)
                        self.args[l.var_name] = f



                    ######## FOLDER OPTION ###########
                    elif l.type==GrrArgument.FOLDER:
                        question = "Enter a "+l.question
                        print(question)
                        f = capture_file(must_exist=l.must_exist, must_not_exist=l.must_not_exist, must_be_folder=True, default=l.default_string)
                        self.args[l.var_name] = f



                    ######## MULTI FILE OPTION ###########
                    elif l.type==GrrArgument.MULTI_FILE:
                        q1 = "Add "+l.question+"?"
                        a = query_yes_no(q1,l.default_yn)
                        files = []
                        while a:
                            ff = capture_file(must_exist=l.must_exist, must_not_exist=l.must_not_exist, must_be_file=True)
                            if l.ask_for_titles:
                                t = capture_text("Enter a title for \""+str(ff)+"\"")
                                fff = (ff,t)
                                files.append(fff)
                            else:
                                files.append(ff)

                            a = query_yes_no("Add another "+l.question+"?",default="No")
                        self.args[l.var_name] = files



                    ######## TEXT OPTION ###########
                    elif l.type==GrrArgument.TEXT:
                        q = "Specify a value for "+l.question
                        t = capture_text(q,l.default_string)
                        self.args[l.var_name] = t






                    ######## MULTI TEXT OPTION ###########
                    elif l.type == GrrArgument.MULTI_TEXT:
                        q1 = "Add " + l.question + "?"
                        a = query_yes_no(q1, l.default_yn)
                        texts = []
                        while a:
                            t = capture_text(q)
                            texts.append(t)

                            a = query_yes_no("Add another "+l.question+"?",default="No")
                        self.args[l.var_name] = texts

                    else:
                        log("Invalid type specified in command line parser: "+ str(l.type),Logger.FATAL)




    def get_var(self, name):
        if name+"_global" in self.args:
            return self.args[name+"_global"]
        elif name in self.args:
            return self.args[name]
        else:
            log("Got a key error when trying to retrieve: " + name + " from args: " + str(
                self.args) + " \n i.e. you called get_var() with a non-existent argument name", Logger.DEBUG)
            return None
        #try:
        #    return self.args[name]
        #except KeyError:
        #    log("Got a key error when trying to retrieve: "+name+" from args: "+str(self.args) +" \n i.e. you called get_var() with a non-existent argument name",Logger.FATAL)


    def set_var(self, name, value, overwrite=True):

        if name in self.args and not overwrite:
            log("Attempting to overwrite variable "+ str(name)+" with the overwrite option disabled")
        else:
            self.args[name] = value


    def persist_object(self,var_name,object):
        store = get_persistence_store()
        store[var_name] = object

    def retrieve_persistent_object(self,var_name,must_exist=True):
        store = get_persistence_store()
        if (var_name not in store) and must_exist:
            log("Attempted to retrieve non-existent object",Logger.WARNING)

        else:
            return store[var_name]

    def proc(self, ask=False):
        if ask:
            question = "Would you like to run "+self.name+"?"
            if not query_yes_no(question,default="yes"):
                return

        # otherwise go ahead with actions

        self._populate()
        log("Running "+ self.name,Logger.TITLE)
        self.do()

    @abc.abstractmethod
    def do(self):
        # do nothing - will overload this in subclasses
        """Implement do() in subclass!"""

    @abc.abstractmethod
    def add_arguments(self):
        # do nothing - will overload this in subclasses
        """Implement add_arguments() in subclass!"""

    def set_help(self, help):
        self.help = help

    def set_name(self, name):
        self.name = name

    def get_args(self):
        return self.args