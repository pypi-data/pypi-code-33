# -*- coding:utf-8 -*-

import json
from base import keyword


class ValidatorKeywords(object):

    # loads:json to dict
    # dumps:dict to json
    @keyword("Compare Json")
    def compare_json(self, json1, json2):
        print 'Json1: ' + json1
        print 'Json2: ' + json2
        json1 = json1.replace("\\", '').replace('"{', "{").replace('}"', "}")
        json2 = json2.replace("\\", '').replace('"{', "{").replace('}"', "}")

        json1 = json1.lower()
        json2 = json2.lower()

        # to dict
        dict1 = json.loads(json1)
        dict2 = json.loads(json2)
        # modify dict values
        dict1 = self.modify_keys(dict1)
        dict2 = self.modify_keys(dict2)

        topkey_result = self.comp_topkey(dict1, dict2)

        if topkey_result == True:
            subkey_result = self.comp_subkey(dict1, dict2)
        else:
            subkey_result = False

        return subkey_result

    def comp_subkey(self, dict1, dict2):

        ty1 = type(dict1).__name__
        ty2 = type(dict1).__name__

        if ty1 == ty2 and ty1 == "dict":
            keys = dict1.keys()
            for key in keys:
                value1 = dict1[key]
                value2 = dict2[key]

                if value1 == value2:

                    if value1 != "1":
                        subdict = value1
                        self.comp_subkey(subdict, subdict)
                else:
                    print "Wrong Key: " + key
                    return False
        elif ty1 == ty2 and ty1 == "list":
            num = len(dict1)
            dict1.sort()
            dict2.sort()
            for i in range(num):
                item = dict1[i]
                self.comp_subkey(item, item)

        elif ty1 != ty2:
            return False

        return True

    def comp_topkey(self, dict1, dict2):

        topkeys1 = []
        keys = dict1.keys()
        for key in keys:
            value = dict1[key]
            if value == "1":
                topkeys1.append(key)

        topkeys2 = []
        keys = dict2.keys()
        for key in keys:
            value = dict2[key]
            if value == "1":
                topkeys2.append(key)

        if topkeys1 == topkeys2:
            return True
        else:
            return False

    def modify_keys(self, dict):

        keys = dict.keys()
        for key in keys:
            value = dict[key]
            ty = type(value).__name__

            if ty == "dict":
                subdict = value
                self.modify_keys(subdict)
            elif ty == "str" or ty == "int":
                dict[key] = "1"
            elif ty == "list":
                while ty == "list":
                    value.sort()
                    num = len(value)
                    for i in range(num):
                        item_dic = value[i]
                        item_keys = item_dic.keys()
                        for item_key in item_keys:
                            subitem = item_dic[item_key]
                            item_ty = type(subitem).__name__
                            if item_ty == "dict":
                                subdict = subitem
                                self.modify_keys(subdict)
                                ty = "dic"
                            elif item_ty == "str" or item_ty == "int":
                                item_dic[item_key] = "1"
                                ty = "int"
                            elif item_ty == "list":
                                ty = 'list'
                                value = item_dic[item_key]
                                value.sort()
                            else:
                                item_dic[item_key] = "1"
                                ty = "int"
            else:
                dict[key] = "1"
                # print "other type: " + ty

        dict = str(dict)
        dict = dict.replace("'", '"')
        dict = eval(dict)
        return dict
