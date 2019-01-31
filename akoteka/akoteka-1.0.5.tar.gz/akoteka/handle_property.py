import os
import configparser
from pathlib import Path

class Property(object):
       
    def __init__(self, file, writable=False, folder=None):
        self.writable = writable
        self.file = file
        self.folder = folder
        self.parser = configparser.RawConfigParser()
        
        # !!! make it CASE SENSITIVE !!! otherwise it duplicates the hit if there was a key with upper and lower cases. Now it throws an exception
        self.parser.optionxform = str

    def __write_file(self):
        
        if self.folder:
            Path(self.folder).mkdir(parents=True, exist_ok=True)
        
        with open(self.file, 'w') as configfile:
            self.parser.write(configfile)

    def get(self, section, key, default_value):

        # if not existing file
        if not os.path.exists(self.file):
            print("GET", "No file: ", self.file)
            
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.get(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print("GET", e, 'in ', self.file)
            if self.writable:
                self.update(section, key, default_value)
                result=self.parser.get(section,key)
            else:
                result = default_value
        return result

    def getBoolean(self, section, key, default_value):
        if not os.path.exists(self.file):
            self.parser[section]={key: default_value}
            self.__write_file()
        self.parser.read(self.file)

        try:
            result=self.parser.getboolean(section,key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if self.writable:
                self.update(section, key, default_value)
                # It is strange how it works with get/getboolean
                # Sometimes it reads boolean sometimes it reads string
                # I could not find out what is the problem
                #result=self.parser.get(section,key)
            result=default_value

        return result

    def update(self, section, key, value, source=None):
        if not os.path.exists(self.file):
            print("UPDATE", "No file: ", self.file, " Source: " + source if source else "")
            self.parser[section]={key: value}        
        else:
            self.parser.read(self.file)
            try:
                # if no section -> NoSectionError | if no key -> Create it
                self.parser.set(section, key, value)
            except configparser.NoSectionError as e:
                print("UPDATE", e, "in ", self.file, " Source: ", source )

                self.parser[section]={key: value}

        self.__write_file()


# ====================
#
# Handle dictionary
#
# ====================
class Dict( Property ):
    
    DICT_FILE_PRE = "resources"
    DICT_FILE_EXT = "properties"
    DICT_FOLDER = "dict"
    DICT_SECTION = "dict"

    __instance = None

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls, lng):
        inst = cls.__new__(cls)
        cls.__init__(cls.__instance, lng)     
        return inst
        
    def __init__(self, lng):
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.__class__.DICT_FOLDER, self.__class__.DICT_FILE_PRE + "_" + lng + "." + self.__class__.DICT_FILE_EXT)
        super().__init__( file )
    
    def _(self, key):
        return self.get(self.__class__.DICT_SECTION, key,  "[" + key + "]")


# =====================
#
# Handle config.ini
#
# =====================
class ConfigIni( Property ):
    HOME = str(Path.home())
    CONFIG_FOLDER = '.akoteka'
    INI_FILE_NAME="config.ini"

    # (section, key, default)
    DEFAULT_LANGUAGE = ("general", "language", "hu")
    DEFAULT_MEDIA_PATH = ("media", "media-path", ".")
    DEFAULT_MEDIA_PLAYER_VIDEO = ("media", "player-video", "mplayer")
    DEFAULT_MEDIA_PLAYER_VIDEO_PARAM = ("media", "player-video-param", "-zoom -fs -framedrop")
    DEFAULT_MEDIA_PLAYER_VIDEO_EXT = ("media", "player-video-ext", "divx,mkv,avi,mp4")
    DEFAULT_MEDIA_PLAYER_AUDIO = ("media", "player-audio", "rhythmbox")
    DEFAULT_MEDIA_PLAYER_AUDIO_PARAM = ("media", "player-audio-param", "")
    DEFAULT_MEDIA_PLAYER_AUDIO_EXT = ("media", "player-audio-ext", "mp3,ogg")
    
    
    __instance = None    

    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(cls):
        inst = cls.__new__(cls)
        cls.__init__(cls.__instance)
        return inst
        
    def __init__(self):
        folder = os.path.join(ConfigIni.HOME, ConfigIni.CONFIG_FOLDER)
        file = os.path.join(folder, ConfigIni.INI_FILE_NAME)
        super().__init__( file, True, folder )

    def get_language(self):
        return self.get(self.DEFAULT_LANGUAGE[0], self.DEFAULT_LANGUAGE[1], self.DEFAULT_LANGUAGE[2])

    def get_media_path(self):
        return self.get(self.DEFAULT_MEDIA_PATH[0], self.DEFAULT_MEDIA_PATH[1], self.DEFAULT_MEDIA_PATH[2])

    def get_media_player_video(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO[0], self.DEFAULT_MEDIA_PLAYER_VIDEO[1], self.DEFAULT_MEDIA_PLAYER_VIDEO[2])

    def get_media_player_video_param(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[1], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[2])

    def get_media_player_video_ext(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[1], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[2])

    def get_media_player_audio(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO[0], self.DEFAULT_MEDIA_PLAYER_AUDIO[1], self.DEFAULT_MEDIA_PLAYER_AUDIO[2])

    def get_media_player_audio_param(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[1], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[2])

    def get_media_player_audio_ext(self):
        return self.get(self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[1], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[2])


    def set_language(self, lang):
        self.update(self.DEFAULT_LANGUAGE[0], self.DEFAULT_LANGUAGE[1], lang)

    def set_media_path(self, path):
        self.update(self.DEFAULT_MEDIA_PATH[0], self.DEFAULT_MEDIA_PATH[1], path)

    def set_media_player_video(self, player):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO[0], self.DEFAULT_MEDIA_PLAYER_VIDEO[1], player)

    def set_media_player_video_param(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_PARAM[1], param)

    def set_media_player_video_ext(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[0], self.DEFAULT_MEDIA_PLAYER_VIDEO_EXT[1], param)

    def set_media_player_audio(self, player):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO[0], self.DEFAULT_MEDIA_PLAYER_AUDIO[1], player)

    def set_media_player_audio_param(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_PARAM[1], param)

    def set_media_player_audio_ext(self, param):
        self.update(self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[0], self.DEFAULT_MEDIA_PLAYER_AUDIO_EXT[1], param)


config_ini = {}

def get_config_ini():
    return ConfigIni.get_instance()

def re_read_config_ini():
    global config_ini
    global dic
    
    ci = get_config_ini()
    
    # Read config.ini    
    config_ini['language'] = ci.get_language()
    config_ini['media_path'] = ci.get_media_path()
    config_ini['media_player_video'] = ci.get_media_player_video()
    config_ini['media_player_video_param'] = ci.get_media_player_video_param()
    config_ini['media_player_video_ext'] = ci.get_media_player_video_ext()
    config_ini['media_player_audio'] = ci.get_media_player_audio()
    config_ini['media_player_audio_param'] = ci.get_media_player_audio_param()
    config_ini['media_player_audio_ext'] = ci.get_media_player_audio_ext()

    # Get the dictionary
    dic = Dict.get_instance( config_ini['language'] )
    
re_read_config_ini()

# --------------------------------------------------------
# --------------------------------------------------------
#
# Gives back the translation of the word
#
# word      word which should be translated
#
# --------------------------------------------------------
# --------------------------------------------------------
def _(word):
    return dic._(word)
