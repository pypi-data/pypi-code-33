"""External module of headerIndexer settings. Reset on each run"""
# Excessive arg passing to prevent inheritance issues and maintain doc info

from headerindexer.data_factory._z_data_docs import SettingsDocs, SettingsFactoryDocs


class Settings(SettingsDocs):

    def __init__(self,
                 raise_error,
                 return_affected,
                 check_nonindexed,
                 check_duplicates,
                 prompt_fix):

        self.reset(raise_error,
                   return_affected,
                   check_nonindexed,
                   check_duplicates,
                   prompt_fix)

    def reset(self,
              raise_error=False,
              return_affected=False,
              check_nonindexed=True,
              check_duplicates=False,
              prompt_fix=True):

        self.__setattr__('raise_error', raise_error)
        self.__setattr__('return_affected', return_affected)
        self.__setattr__('check_nonindexed', check_nonindexed)
        self.__setattr__('check_duplicates', check_duplicates)
        self.__setattr__('prompt_fix', prompt_fix)


class SettingsFactory(SettingsFactoryDocs):

    @staticmethod
    def _return_settings_obj(raise_error,
                             return_affected,
                             check_nonindexed,
                             check_duplicates,
                             prompt_fix):

        return Settings(raise_error,
                        return_affected,
                        check_nonindexed,
                        check_duplicates,
                        prompt_fix)

    def new_settings_obj(self,
                         raise_error=False,
                         return_affected=False,
                         check_nonindexed=True,
                         check_duplicates=False,
                         prompt_fix=True):

        _set_to_return = self._return_settings_obj(raise_error,
                                                   return_affected,
                                                   check_nonindexed,
                                                   check_duplicates,
                                                   prompt_fix)

        return _set_to_return
