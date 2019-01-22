# coding: utf-8
import xml.dom.minidom
import re
from copy import deepcopy

"""
xml读取工具
author:CallMeE
date:2018-06-01
"""
# 定义操作符
marks = {
    'eq': '==',
    'lt': '<',
    'gt': '>',
    'le': '<=',
    'ge': '>=',
    'not': '!=',
    'has': 'HAS'
}


class Mapper:
    _data = {}

    def sortTags(self, file: str, tree, name):
        tags = tree.getElementsByTagName(name)
        data = self._data
        file_list = file.split('/')
        file_name = re.sub('\\..*', '', file_list[len(file_list) - 1])
        if file_name not in data:
            data[file_name] = {}
        file_cache = data[file_name]
        for tag in tags:
            val = []
            for node in tag.childNodes:
                if isinstance(node, xml.dom.minidom.Text):
                    if re.sub('\s', '', node.data):
                        val.append(re.sub('\n', '', node.data))
                else:
                    val.append(id(node))
            attr = tag.getAttribute("id")
            id_bind_obj = {}
            id_bind_obj['main_sql'] = val
            # 获取条件标签
            if_tags = self.sortIfTags(tag)
            id_bind_obj['if'] = if_tags
            for_tags = self.sortForTag(tag)
            id_bind_obj['for'] = for_tags
            file_cache[attr] = id_bind_obj

    def openDom(self, file):
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(file)
        tags = DOMTree.documentElement
        # 取出标签(增删查改)
        self.sortTags(file, DOMTree, 'select')
        self.sortTags(file, DOMTree, 'delete')
        self.sortTags(file, DOMTree, 'insert')
        self.sortTags(file, DOMTree, 'update')

    def getTree(self):
        return self._data

    def sortIfTags(self, tag):
        if_tags = tag.getElementsByTagName('if')
        tags_structer = {}
        for if_tag in if_tags:
            val = if_tag.childNodes[0].data
            attrs = if_tag.attributes
            attr_keys = attrs.keys()
            tag_struct = {}
            if attr_keys:
                if_key_index = 0
                for k in attr_keys:
                    if_key_struct = {}
                    attr_value = str(if_tag.getAttribute(k)).split('|')
                    attr_operator = marks.get(attr_value[0])
                    attr_operator_value = attr_value[1] if len(attr_value) > 1 else ''
                    if attr_value:
                        if_key_struct['_key'] = k
                        if_key_struct['operator'] = attr_operator
                        if_key_struct['_value'] = attr_operator_value
                        if_key_struct['add_sql'] = val
                        tag_struct[if_key_index] = if_key_struct
                        if_key_index += 1
                tags_structer[id(if_tag)] = tag_struct
        return tags_structer

    def sortForTag(self, tag):
        """
        处理循环标签(暂定使用文本元素替换标签元素)
        :param tag:
        :return:
        """
        for_tags = tag.getElementsByTagName('for')
        tags_structer = {}
        if for_tags:
            for for_tag in for_tags:
                # 获取初始化相关参数
                left_area_tag = for_tag.getAttribute('left') if for_tag.hasAttribute('left') else '('
                right_area_tag = for_tag.getAttribute('right') if for_tag.hasAttribute('right') else ')'
                sep = for_tag.getAttribute('sep') if for_tag.hasAttribute('sep') else ','

                tags_structer[id(for_tag)] = {
                    'sep': sep,
                    'left_area_tag': left_area_tag,
                    'right_area_tag': right_area_tag,
                    'arg_key': re.sub('\s*', '', re.sub('#{|}', '', for_tag.childNodes[0].data))
                }
                # new = xml.dom.minidom.Text().replaceWholeText('111')  # 创建文本节点
        return tags_structer

    def get_executable_sql(self, sql_datas: dict, method_name: str, args=None) -> str:
        """
        获取实际执行语句
        :param method_name:
        :param args:
        :return:
        """
        result_sql = deepcopy(sql_datas)[method_name]
        if isinstance(result_sql, str):
            return result_sql
        if isinstance(result_sql, dict) and args and isinstance(args, dict):
            # 如果存在参数
            # 处理条件标签
            self.check_if(result_sql, args)
            # print(result_sql)
            self.check_for(result_sql, args)
            # print(result_sql)
            return ''.join(result_sql['main_sql'])
        return ''.join(result_sql['main_sql'])

    def check_for(self, main_struct: dict, args: dict):
        """
        检查循环结构
        :param main_struct:
        :param args:
        :return:
        """
        for_struct = main_struct['for']
        if for_struct:
            # print(for_struct)
            main_struct_index = 0
            for main_struct_item in main_struct['main_sql']:
                if not isinstance(main_struct_item,str) and main_struct_item in for_struct:
                    # 遍历语句节点
                    if not isinstance(main_struct_item, str):
                        for_v = for_struct[main_struct_item]
                        arg_sequence = args.get(for_v['arg_key'], None)
                        if arg_sequence:
                            # 处理序列参数
                            index = 0
                            for i in arg_sequence:
                                if not isinstance(i, str):
                                    arg_sequence[index] = str(i)
                                index += 1
                            main_struct['main_sql'][main_struct_index] = for_v['left_area_tag'] + \
                                                                         for_v['sep'].join(arg_sequence) + \
                                                                         for_v['right_area_tag']
                        else:
                            raise KeyError('找不到对应序列:' + for_v['arg_key'])
                main_struct_index += 1

    def check_if(self, main_struct: dict, args: dict):
        """
        检查条件结构
        :param if_struct:
        :param args:
        :return:
        """
        if_struct = main_struct['if']
        if if_struct:
            main_struct_index = 0
            for main_struct_item in main_struct['main_sql']:
                if not isinstance(main_struct_item, str) and main_struct_item in if_struct:
                    # 存在条件结构数据
                    compile_result = True
                    for if_v in if_struct[main_struct_item].values():
                        # 遍历每个if标签
                        # 根据操作符进行判断
                        compile_key = if_v['_key']
                        if if_v['operator'] == marks['has']:
                            if compile_key in args:
                                # print(args.get(compile_key))
                                compile_result = compile_result and args.get(compile_key)
                            else:
                                compile_result = False
                        else:
                            # dict类型(标签属性结构)
                            if compile_key in args:
                                arg_value = args[compile_key]
                                if isinstance(arg_value, str):
                                    compile_result = (if_v['_value'] == arg_value) and compile_result
                                else:
                                    compile_result = eval(
                                        if_v['_value'] +
                                        if_v['operator'] +
                                        str(arg_value)
                                    ) and compile_result
                        if compile_result:
                            # 判断标签全属性条件是否通过
                            # 执行表达式结果
                            main_struct['main_sql'][main_struct_index] = if_v['add_sql']
                        else:
                            main_struct['main_sql'][main_struct_index] = ''
                main_struct_index += 1
