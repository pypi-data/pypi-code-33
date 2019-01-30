import os
import json
import configparser

from .FileFormatException import FileFormatException

class Config():
    """docstring for ConfigJsonEnv."""

    def __init__(self, file = None):
        self._config = dict()
        self._configCache = dict()
        if file is not None:
            self.addFile(file)

    def addFile(self,file):
        """
            Permet d'ajouter un fichier

            Args:
            file (string): path d'un fichier json

            Returns:
            type: None

            Raises:
            FileFormatException: Erreur du format de fichier
        """
        mylambda= lambda adict : { key.upper() : mylambda(adict[key]) if isinstance(adict[key],dict) else adict[key] for key in adict.keys() }
        if file.endswith('.json') :
            with open(file, 'r') as f:
                fileContent = mylambda(json.load(f))

        elif file.endswith('.ini') :
            parser  = configparser.ConfigParser()
            parser.read(file)
            fileContent = { section : { conflist[0].upper() : conflist[1] for conflist in parser.items(section) } for section in parser.sections() }
        else :
            raise FileFormatException()

        self._config = {**self._config, **mylambda(fileContent)}

    def get(self,path):
        """
            permet de récupérer une config

            Args:
            path (String): Nom d'une config

            Returns:
            type: String
            la valeur de la config ou None
        """
        path = path.upper()
        if path in self._configCache:
            return self._configCache[path]
        else :
            return self._findConfig(path)

    def clearCache(self):
        """
            permet de netoyer le cache

            Returns:
            type: None
        """
        self._configCache =  dict()


    def _findConfig(self,path):
        if path in os.environ:
            config = os.environ[path]
        else :
            splited = path.split("_")
            config = self._recursiveRoute(self._config,splited)
        self._setCache(path,config)
        return config

    def _setCache(self,path,config):
        self._configCache[path] = config

    def _recursiveRoute(self,context,left):
        search = ""
        for index in range(len(left)):
            search += left.pop(0) if len(search) == 0 else "_"+left.pop(0)
            if search in [ key.upper() for key in context ] and isinstance(context[search],dict):
                return self._recursiveRoute(context[search],left)
            elif search in context:
                # print(search,context[search])
                return context[search]
