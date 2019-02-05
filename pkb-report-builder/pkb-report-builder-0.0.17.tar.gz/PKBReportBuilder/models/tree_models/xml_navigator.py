import logging

#xml navigator additional params
class XmlNavigatorAdditionalParams():
    def __init__(self):
        try:

            complex_value_attribute =False
            complex_value_attribute_paths =[]



            pass
        except Exception as e:
            logging.error("Error initialization. " + str(e))



#xml tree navigator
class XmlNavigator():
    #constructor
    def __init__(self,paths,value_attribute, convert_types, style,additional_params=None):
        try:
            self.paths = paths
            self.value_attribute = value_attribute
            self.convert_types = convert_types
            self.style =style

            self.additional_params =additional_params
        except Exception as e:
            logging.error("Error initialization. " + str(e))
