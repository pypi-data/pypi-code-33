from typing import Dict, List

class TupleMap():

    def __init__(self, treatNoneAsEmpty:bool=True, *keys:str):

        self.__treatNoneAsEmpty = treatNoneAsEmpty
        self.__dict = {}

        if keys:
            for key in  keys:
                self.__dict[key.strip(' \n\r\t')] = []
            
    def get_tuple_size(self):
        
        for i, key in enumerate(self.__dict.keys()):
            return len(self.__dict[key])
        return 0

    def get_size(self):
        return len(self.__dict)

    def get_key(self, index:int):

        if len(self.__dict.keys()) > index:
            for i, key in enumerate(self.__dict.keys()):
                if index == i:
                    return key
        if self.__treatNoneAsEmpty:
            return None
        else:
            raise Exception("Key not found at index({})".format(index))

    def get_keys(self):
        return self.__dict.keys()

    def get_values(self):
        return self.__dict.values()

    def get_values_at(self, index:int):

        values = []

        for key in self.get_keys():
            values.append(self.get_item_at(key, index))

        return values

    def has_items(self, key:str):
        return key in self.__dict

    def has_item_at(self, key:str, index:int):
        if self.has_items(key) and len(self.get_items(key)) > index:
            if self.__treatNoneAsEmpty:
                return self.get_items(key)[index] != None
            return True
        return False

    def get_items(self, key:str)->List[any]:
        if self.has_items(key):
            return self.__dict[key]
        else:
            if self.__treatNoneAsEmpty:
                return None
            raise Exception("Key not found: {}".format(key))

    def get_item_at(self, key:str, index:int)->List[any]:
        if self.has_item_at(key, index):
            return self.get_items(key)[index]
        else:
            if self.__treatNoneAsEmpty:
                return None
            raise Exception("Key not found at index({}): {}".format(index, key))

    def set_items(self, key:str, *values:any):
        self.__dict[key] = []

        if values:
            for value in values:
                self.__dict[key].append(value)

    def set_item_at(self, key:str, index:int, value:any):
        if not self.has_item_at(key, index):
            raise Exception("Key not found at index({}): {}".format(index, key))
        self.get_items(key)[index] = value


    def append_stripped_strings(self, *values:str):

        if not values or len(values) != self.get_size():
            raise Exception("Length of provided value must match size of TupleMap. Expected: {}, Actual: {}".format(self.get_size(), len(values)))

        if values:
            for index, key in enumerate(self.get_keys()):
                self.__dict[key].append(values[index].strip(' \n\r\t'))

    
    def append_items(self, *values:any):

        if not values or len(values) != self.get_size():
            raise Exception("Length of provided value must match size of TupleMap. Expected: {}, Actual: {}".format(self.get_size(), len(values)))

        if values:
            for index, key in enumerate(self.get_keys()):
                self.__dict[key].append(values[index])

    def append_items_at(self, key:str, *values:any):

        if not self.has_items(key):
            self.__dict[key] = []

        if values:
            for value in values:
                self.__dict[key].append(value)

    def empty_items(self, key:str):
        self.__dict[key] = []
