"""
Formatter
"""

from __future__ import absolute_import
from __future__ import unicode_literals

__author__ = 'VMware, Inc'
__copyright__ = 'Copyright (c) 2015-2018 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'

import base64
import inspect
import os
import sys  # pylint: disable=W0611
import six

try:
    from collections import OrderedDict  # for python 2.7 onwards
except ImportError:
    from ordereddict import OrderedDict

from vmware.vapi.data.value import (IntegerValue, DoubleValue,
                                    BooleanValue, StringValue,
                                    BlobValue, ListValue,
                                    StructValue, OptionalValue,
                                    SecretValue, DataValue, VoidValue)
from vmware.vapi.data.type import Type
from vmware.vapi.bindings.struct import VapiStruct
from vmware.vapi.client.dcli.util import get_console_size
from vmware.vapi.lib.constants import MAP_ENTRY


def XmlEscape(xml_str):
    """
    Xml escape: escape <, >, &

    :type  xml_str: :class:`str`
    :param xml_str: xml string to escape
    :rtype: :class:`str`
    :return: escaped xml str
    """
    escaped = xml_str.replace('&', '&amp;').replace('>', '&gt;').replace('<',
                                                                         '&lt;')
    return escaped


def check_data_value(val):
    """
    Check if data value is either a StructValue, ListValue or
    OptionalValue(StructValue()) or not.

    :type  val: :class:`object`
    :param val: Python primitive object
    :rtype: :class:`bool`
    :return: Return status
    """
    if is_map_entry(val) \
            or val.type == Type.STRUCTURE \
            or val.type == Type.LIST \
            or is_optional_struct(val):
        return False
    return True


def is_map_entry(val):
    """
    Check if data value is map entry structure

    :type  val: :class:`object`
    :param val: Python primitive object
    :rtype: :class:`bool`
    :return: Return status
    """
    if val.type == Type.OPTIONAL and (
            val.value is not None and val.value.type == Type.LIST):
        val = val.value

    if val.type == Type.LIST:
        item = next((x for x in val), None)
        if isinstance(item, StructValue) and item.name == MAP_ENTRY:
            return True
    return False


def is_optional_struct(val):
    """
    Check if data value is optional structure

    :type  val: :class:`object`
    :param val: Python primitive object
    :rtype: :class:`bool`
    :return: Return status of the check
    """
    return val.type == Type.OPTIONAL and \
        val.value is not None and \
        val.value.type == Type.STRUCTURE


def _FormatPrimitive(val):
    """
    Format primitive type value

    :type  val: :class:`object`
    :param val: python primitive object
    :rtype: :class:`str`
    :return: formatted python string
    """
    result = ''
    if val is None:
        pass
    elif isinstance(val, six.string_types):
        result = val
    elif isinstance(val, type):
        result = val.__name__
    elif isinstance(val, StringValue):
        try:
            result = str(val.value)
        except UnicodeEncodeError:
            result = repr(val.value)
    elif isinstance(val, VoidValue):
        pass
    elif isinstance(val, BlobValue):
        if six.PY3 and isinstance(val.value, str):
            result = base64.b64encode(six.b(val.value))
        else:
            result = base64.b64encode(val.value)
        if six.PY3:
            result = result.decode()
    elif isinstance(val, (BlobValue, BooleanValue, DataValue, DoubleValue, IntegerValue)):
        result = str(val.value)
    else:
        result = str(val)
    return result


class BaseVisitor(object):
    """ Base script format visitor """

    # All visit flags
    FLAG_NONE = 0x0
    FLAG_LAST_ITEM = 0x1
    FLAG_FIRST_ITEM = 0x2

    def __init__(self, fp=sys.stdout):
        """ Base script format visitor init """
        self.output_field_list = []
        self.metamodel_struct_list = []
        self.more = False
        self.should_visit_struct_el = None
        self.should_apply_structure_filter_visitor = None
        self.output_lines = []
        self.fp = fp

    def _Fn(self, fn_name):
        """
        Tempoline fn to call fn with fn_name

        :type  fn_name: :class:`function`
        :param fn_name: function name to call
        :rtype:  :class:`object` or None
        :return: whatever function returns
        """
        # TODO: Should also check if fn is callable or not
        return getattr(self, fn_name, self._NullFn)

    def _NullFn(self, *args, **kwargs):
        """ null function """
        pass

    def append(self, text):
        """
        Append text to output cache

        :type text: :class:`str`
        :param text: text to append to output cache
        """
        self.output_lines.append(text)

    def appendLines(self, lines):
        """
        Append lines to output cache

        :type lines: :class:`list` of :class:`str`
        :param lines: lines to extend output cache with
        """
        self.output_lines.extend(lines)

    def VisitDict(self, do):
        """
        Visit dictionary

        :type  do: :class:`object`
        :param do: python dict object
        """
        self._Fn('VisitDoBegin')(do)

        fnVisitDoFieldBegin = self._Fn('VisitDoFieldBegin')
        fnVisitDoFieldEnd = self._Fn('VisitDoFieldEnd')

        # Iterate through each prop and format
        len_do = len(do)
        numItems = len_do
        for name, val in six.iteritems(do):
            flags = self.FLAG_NONE
            if numItems == len_do:
                flags |= self.FLAG_FIRST_ITEM
            numItems -= 1
            if numItems == 0:
                flags |= self.FLAG_LAST_ITEM
            fnVisitDoFieldBegin(name, flags, val)
            self.Visit(val)
            fnVisitDoFieldEnd(name, flags, val)

        self._Fn('VisitDoEnd')(do)

    def VisitStruct(self, struct):
        """
        Visit vapi data value structure

        :type  struct: :class:`vmware.vapi.data.value.StructValue`
        :param struct: vapi structure object
        """
        self._Fn('VisitDoBegin')(struct)

        fnVisitDoFieldBegin = self._Fn('VisitDoFieldBegin')
        fnVisitDoFieldEnd = self._Fn('VisitDoFieldEnd')

        # Iterate through each prop and format
        output_info = next((field_info for field_info in self.output_field_list
                            if field_info.structure_id == struct.name), None)
        metamodel_info = next(
            (struct_info for struct_info in self.metamodel_struct_list
             if struct_info.name == struct.name), None)

        if self.should_apply_structure_filter_visitor is None:
            should_apply_struct_filter = True
        else:
            should_apply_struct_filter = self.should_apply_structure_filter_visitor(
                struct, metamodel_info)

        if output_info:
            len_fields = len(output_info.output_fields)
            numItems = len_fields

            for output_field in output_info.output_fields:
                flags = self.FLAG_NONE
                if numItems == len_fields:
                    flags |= self.FLAG_FIRST_ITEM
                numItems -= 1
                if numItems == 0:
                    flags |= self.FLAG_LAST_ITEM

                if not should_apply_struct_filter or \
                        self.should_visit_struct_el is None or \
                        self.should_visit_struct_el(output_field.field_name,
                                                    struct, metamodel_info):
                    val = struct.get_field(output_field.field_name)

                    disp_name = output_field.field_name
                    fnVisitDoFieldBegin(disp_name, flags, val)
                    self.Visit(val)
                    fnVisitDoFieldEnd(disp_name, flags, val)
        else:
            field_names = struct.get_field_names()
            len_fields = len(field_names)
            numItems = len_fields
            first_is_set = False
            for name in field_names:
                flags = self.FLAG_NONE
                if not first_is_set:
                    flags |= self.FLAG_FIRST_ITEM
                numItems -= 1
                if numItems == 0:
                    flags |= self.FLAG_LAST_ITEM
                if not should_apply_struct_filter or \
                    self.should_visit_struct_el is None or \
                        self.should_visit_struct_el(name, struct,
                                                    metamodel_info):
                    val = struct.get_field(name)

                    fnVisitDoFieldBegin(name, flags, val)
                    self.Visit(val)
                    fnVisitDoFieldEnd(name, flags, val)
                    first_is_set = True

        self._Fn('VisitDoEnd')(struct)

    def VisitVapiStruct(self, do):
        """
        Visit vapi binding structure

        :type  do: :class:`vmware.vapi.bindings.struct.VapiStruct`
        :param do: vapi binding structure object
        """
        self._Fn("VisitDoBegin")(do)

        fnVisitDoFieldBegin = self._Fn("VisitDoFieldBegin")
        fnVisitDoFieldEnd = self._Fn("VisitDoFieldEnd")

        # Iterate through each prop and format
        field_names = [k for k, _ in inspect.getmembers(do) if
                       not k.startswith('_')]
        len_field_names = len(field_names)
        numItems = len_field_names
        for name in field_names:
            val = do.get_field(name)
            flags = self.FLAG_NONE
            if numItems == len_field_names:
                flags |= self.FLAG_FIRST_ITEM
            numItems -= 1
            if numItems == 0:
                flags |= self.FLAG_LAST_ITEM
            fnVisitDoFieldBegin(name, flags, val)
            self.Visit(val)
            fnVisitDoFieldEnd(name, flags, val)

        self._Fn("VisitDoEnd")(do)

    def VisitList(self, lst):
        """
        Visit vapi list

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self._Fn("VisitListBegin")(lst)
        lastIdx = len(lst) - 1
        for idx, val in enumerate(lst):
            flags = self.FLAG_NONE
            if idx == 0:
                flags |= self.FLAG_FIRST_ITEM
            if idx == lastIdx:
                flags |= self.FLAG_LAST_ITEM
            self._Fn('VisitListItemBegin')(idx, flags, val)
            self.Visit(val)
            self._Fn('VisitListItemEnd')(idx, flags, val)
        self._Fn('VisitListEnd')(lst)

    def VisitOptional(self, optional):
        """
        Visit vapi optional value

        :type  optional: :class:`vmware.vapi.data.value.OptionalValue`
        :param optional: optional value
        """
        self._Fn('VisitOptionalBegin')(optional)
        self.Visit(optional.value)
        self._Fn('VisitOptionalEnd')(optional)

    def VisitRoot(self, val):
        """
        Visit object at root level

        :type  val: :class:`object`
        :param val: root object
        """
        self._Fn('VisitRootBegin')(val)
        self.Visit(val)
        self._Fn('VisitRootEnd')(val)

    def Visit(self, val):
        """
        Visit any val

        :type  val: :class:`object`
        :param val: any object
        """
        if isinstance(val, (ListValue, list)):
            self.VisitList(val)
        elif isinstance(val, StructValue):
            self.VisitStruct(val)
        elif isinstance(val, VapiStruct):
            self.VisitVapiStruct(val)
        elif isinstance(val, dict):
            self.VisitDict(val)
        elif isinstance(val, OptionalValue):
            self.VisitOptional(val)
        else:
            self._Fn('VisitPrimitive')(val)

    # Format a val
    #
    # @param  val Value to format
    def Format(self, val, more=False, output_field_list=None,
               metamodel_struct_list=None):
        """
        Format a val. Alias to VisitRoot

        :type  val: :class:`object`
        :param val: any object
        """
        self.output_field_list = output_field_list if output_field_list else []
        self.metamodel_struct_list = metamodel_struct_list if metamodel_struct_list else []
        self.more = more
        self.VisitRoot(val)
        self.output()

    def output(self):
        """
        Outputs collected cache
        """
        if self.more:
            lines_printed = 0
            height, _ = get_console_size()
            page_size = height - 1
            for i in range(0, len(self.output_lines), page_size - 1):
                self.fp.write('\n'.join(self.output_lines[i:i + page_size - 1]))
                lines_printed += page_size
                if lines_printed < len(self.output_lines):
                    self.fp.write('\n')
                    try:
                        # For Python 3 compatibility
                        input_func = raw_input  # pylint: disable=W0622
                    except NameError:
                        input_func = input
                    input_func("Press ENTER key for more")  # pylint: disable=E0602
                else:
                    self.fp.write('\n')
        else:
            self.fp.write('\n'.join(self.output_lines) + '\n')
        del self.output_lines[:]

    def structure_element_visit(self, fn):
        """
        Assign function to the should_visit_struct_el handler

        :param fn: predicate function to execute before each formatter's strucutre element visit
        :type fn: Function
        """
        self.should_visit_struct_el = fn

    def apply_structure_filter_visitor(self, fn):
        """
        Assign function to the should_apply_structure_filter_visitor handler. Function is a
        predicate which checks whether to apply the structure_element_visit handler

        :param fn: predicate function which checks whether to apply the structure_element_visit handler
        :type fn: Function
        """
        self.should_apply_structure_filter_visitor = fn


class ItemBox(object):
    """ box an item """

    def __init__(self, val=None):
        """
        box item item

        :type  val: :class:`object`
        :param val: any object
        """
        self.val = val
        self.headers = []


#
# A common pattern to not use function arguments. Disable this pylint warning
# from this point on
# pylint: disable=W0613


class TableVisitor(BaseVisitor):
    """ Table format visitor """

    def __init__(self, fp=sys.stdout):
        """
        Table format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        BaseVisitor.__init__(self, fp)
        self.stack = []

    @staticmethod
    def _FormatList(rows):
        """
        Format a list with current row / col constraints

        :type  rows: :class:`list` of :class:`str`
        :param rows: rows of lines
        :rtype:  :class:`list` of :class:`str`
        :return: formatted rows of lines
        """
        # Expand row with '\n' to multiple rows
        new_rows = []
        for row in rows:
            max_lines = 1
            for val in row:
                lines = val.count('\n') + 1
                if lines > max_lines:
                    max_lines = lines

            if max_lines > 1:
                # Expand this row into multiple rows
                expand_rows = [[] for idx in six.moves.range(0, max_lines)]  # pylint: disable=E1101
                for val in row:
                    lines = val.split('\n')
                    lines.extend([''] * (max_lines - len(lines)))
                    for exp_row, line in zip(expand_rows, lines):
                        exp_row.append(line)

                new_rows.extend(expand_rows)
            else:
                new_rows.append(row)

        rows = new_rows

        # Calculate max col width
        col_width = [len(val) for val in rows[0]]
        for row in rows[1:]:
            for idx, val in enumerate(row):
                col_width[idx] = max(col_width[idx], len(val))

        # Insert header
        separator = ['-' * size for size in col_width]
        rows.insert(0, separator)
        rows.insert(2, separator)
        rows.insert(len(rows), separator)

        pad = []
        lines = []
        for row in rows:
            line = '|'
            for idx, val in enumerate(row):
                pad = ' ' * (col_width[idx] - len(val))
                line += val + pad + '|'
            lines.append(line)
        return lines

    # Not used for now
    # def VisitRootBegin(self, val): pass

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        itembox = self.stack[-1]
        lines = []
        if itembox.val:
            if isinstance(itembox.val, (dict, OrderedDict)):
                rows = [list(itembox.val.keys()), list(itembox.val.values())]
                lines = TableVisitor._FormatList(rows)
            else:
                lines = itembox.val.split('\n')
            self.appendLines(lines)

    def VisitDoBegin(self, do):  # pylint: disable=W0613
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.stack.append(ItemBox(val=OrderedDict()))

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        # Stack top is the do_itembox
        do_itembox = self.stack[-1]
        if len(self.stack) > 1:
            parent_itembox = self.stack[-2]
            if isinstance(parent_itembox.val, list):
                # Parent is a list. Parent will do the formatting
                pass
            else:
                rows = [list(do_itembox.val.keys()),
                        list(do_itembox.val.values())]
                lines = TableVisitor._FormatList(rows)

                do_itembox.val = '\n'.join(lines)

    # Not used for now
    # def VisitDoFieldBegin(self, field_name, flags, val): pass

    def VisitDoFieldEnd(self, field_name, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        itembox = self.stack.pop()
        if field_name not in ['__vmodl_type__', 'dynamicType',
                              'dynamicProperty']:
            do_itembox = self.stack[-1]
            do_itembox.val[field_name] = itembox.val

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.stack.append(ItemBox(val=[]))

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        lst_itembox = self.stack[-1]
        if lst_itembox.val:
            if isinstance(lst_itembox.val[0], (OrderedDict, StructValue, dict)):
                # setting headers as first element
                rows = [lst_itembox.headers]
                for val in lst_itembox.val:
                    item_keys = list(val.keys())
                    item_values = []
                    for key in rows[0]:
                        if key not in item_keys:
                            item_values.append('')
                        else:
                            item_values.append(val[key])
                    rows.append(item_values)
                lines = TableVisitor._FormatList(rows)
                lst_itembox.val = '\n'.join(lines)
            else:
                val = lst_itembox.val
                if isinstance(lst_itembox.val[0], (ListValue, list)):
                    lst_itembox.val = ', '.join(val)
                else:
                    lst_itembox.val = '\n'.join(val)
        else:
            lst_itembox.val = ''

    # Not used for now
    # def VisitListItemBegin(self, idx, flags, val): pass

    def VisitListItemEnd(self, idx, flags, val):
        """
        Visit list item end

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        itembox = self.stack.pop()
        lst_itembox = self.stack[-1]
        assert len(lst_itembox.val) == idx
        lst_itembox.val.append(itembox.val)
        if isinstance(itembox.val, (OrderedDict, StructValue, dict)):
            if not lst_itembox.headers:
                lst_itembox.headers = list(itembox.val.keys())
            else:
                new_headers = [item for item in itembox.val.keys()
                               if item not in lst_itembox.headers]
                lst_itembox.headers.extend(new_headers)

    # Not used for now
    # def VisitOptionalBegin(self, optionalVal): pass
    # def VisitOptionalEnd(self, optionalVal): pass

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        formatted = _FormatPrimitive(val)
        self.stack.append(ItemBox(formatted))


# Output with indentation
#
class IndentableOutput(object):
    """ Indentable output """

    def __init__(self, output_lines, inc=3, indent_char=' '):
        """
        Indentable output init

        :type  output_lines: :class:`file`
        :param output_lines: output lines list to append to
        :type  inc: :class:`int`
        :param inc: indentation increment
        :type  indent_char: :class:`str`
        :param indent_char: indentation char
        """
        self.output_lines = output_lines
        self._inc = inc
        self._indent_char = indent_char
        self._curr_indent = 0
        self._indented = False
        self._eol = os.linesep

    def append(self, text):
        """
        write

        :type  text: :class:`str`
        :param text: text to write
        """
        self._Indent(text)

    def appendLines(self, seq):
        """
        write lines

        :type  seq: iterable of :class:`str`
        :param seq: texts to write
        """
        for val in seq:
            self._Indent(val)

    def _Indent(self, text):
        """
        Indent text

        :type  text: :class:`str`
        :param text: text to indent
        :rtype: :class:`str`
        :return: indented text
        """
        if not text or self._curr_indent <= 0:
            self.output_lines.append(text)
            return

        # Optimize for single linesep
        if text == self._eol:
            self._indented = False
            self.output_lines.append(text)
            return

        indentStr = self._indent_char * self._curr_indent
        # prevIndented = self._indented
        # if not prevIndented:
        #     text = indentStr + text

        # Check text and if there is trailing \n, reset _indented to False
        lines = text.split(self._eol)
        if lines[-1] == '':
            self.output_lines.extend([indentStr + line for line in lines[:-1]])
            self._indented = False
        else:
            self.output_lines.extend([indentStr + line for line in lines])
            self._indented = True

    def indent(self, cnt=1):
        """
        Indent current indentation counter

        :type  cnt: :class:`int`
        :param cnt: indentation amount
        """
        self._curr_indent += self._inc * cnt

    def dedent(self, cnt=1):
        """
        Dedent current indentation counter

        :type  cnt: :class:`int`
        :param cnt: dedentation amount
        """
        dedent_cnt = self._inc * cnt
        if self._curr_indent > dedent_cnt:
            self._curr_indent -= dedent_cnt
        else:
            self.reset()

    def reset(self, indent=0):
        """
        Reset indentation counter

        :type  indent: :class:`int`
        :param indent: new indentation count
        """
        curr_indent = self._curr_indent
        self._curr_indent = indent
        return curr_indent


def StructTypeName(struct_val):
    """
    get vapi struct type name

    :type  struct_val: :class:`vmware.vapi.data.value.StructValue`
    :param struct_val: vapi struct val
    :rtype: :class:`str`
    :return: vapi struct type name
    """
    if struct_val and struct_val.name:
        return ''
    return struct_val.name


def TypeName(val):
    """
    get vapi type name

    :type  val: :class:`vmware.vapi.data.value.DataValue`
    :param val: vapi data val
    :rtype: :class:`str`
    :return: vapi type name
    """
    type_name = ''
    if isinstance(val, ListValue):
        type_name = 'list'
    elif isinstance(val, StructValue):
        type_name = StructTypeName(val)
    elif isinstance(val, OptionalValue):
        type_name = 'optional'
    elif isinstance(val, (BooleanValue, bool)):
        type_name = 'bool'
    elif isinstance(val, (IntegerValue, six.integer_types)):
        type_name = 'int'
    elif isinstance(val, (DoubleValue, float)):
        type_name = 'double'
    elif isinstance(val, BlobValue):
        type_name = 'blob'
    elif isinstance(val, (StringValue, six.string_types)):
        type_name = 'string'
    elif isinstance(val, SecretValue):
        type_name = 'string'
    else:
        type_name = ''

    return type_name


# Xml format visitor
#
class XmlVisitor(BaseVisitor):
    """ Xml format visitor """

    def __init__(self, fp=sys.stdout):
        """
        Xml format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        BaseVisitor.__init__(self, fp)
        self.indentable_output = IndentableOutput(self.output_lines, inc=1)

    def VisitRootBegin(self, val):
        """
        Visit root object begin

        :type  val: :class:`object`
        :param val: root object
        """
        # Xml tag attribute
        attrs = ['version="1.0"']
        # TODO: Make sure encoding name is mappable to xml encoding
        encoding = getattr(self.indentable_output, 'encoding', None)
        if encoding:
            attrs.append('encoding="%s"' % encoding.lower().replace('_', '-'))

        # TODO: Add <meta-data> after root tag
        self.indentable_output.appendLines(
            ['<?xml %s?>' % ' '.join(attrs),
             '<output xmlns="http://www.vmware.com/Products/vapi/1.0">',
             '<root>'])
        self.indentable_output.indent()

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        self.indentable_output.dedent()
        self.indentable_output.appendLines(['</root>', '</output>'])

    def VisitDoBegin(self, do):
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        type_name = StructTypeName(do)
        if type_name:
            type_name = ' type="%s"' % XmlEscape(type_name)
        self.indentable_output.append('<structure%s>' % type_name)
        self.indentable_output.indent()

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.indentable_output.dedent()
        self.indentable_output.append('</structure>')

    def VisitDoFieldBegin(self, field_name, flags, val):
        """
        Visit data object field begin

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        self.indentable_output.append('<field name="%s">' % XmlEscape(field_name))
        self.indentable_output.indent()

    def VisitDoFieldEnd(self, field_name, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        self.indentable_output.dedent()
        self.indentable_output.append('</field>')

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        type_name = ''
        # TODO: Better way to get list def out of ListValue
        lst_def = getattr(lst, '_lstDef', None)
        if lst_def:
            item_type = lst_def.GetElementType()
            type_name = TypeName(item_type)
            if type_name:
                type_name = ' type="%s"' % XmlEscape(type_name)
        self.indentable_output.append('<list%s>' % XmlEscape(type_name))
        self.indentable_output.indent()

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.indentable_output.dedent()
        self.indentable_output.append('</list>')

    # Not used for now
    # def VisitOptionalBegin(self, optionalVal): pass
    # def VisitOptionalEnd(self, optionalVal): pass

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        if val is None:
            return

        type_name = TypeName(val)
        assert type_name
        formatted = _FormatPrimitive(val)
        self.indentable_output.append('<%s>%s</%s>' % (type_name,
                                                       XmlEscape(formatted),
                                                       type_name))


# Html format visitor
#
class HtmlVisitor(BaseVisitor):
    """ Html format visitor """
    ROOT, LIST, STRUCT = (0, 1, 2)

    def __init__(self, fp=sys.stdout):
        """
        Html format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        BaseVisitor.__init__(self, fp)
        self.indentable_output = IndentableOutput(self.output_lines, inc=1)
        self.stack = []

    def VisitRootBegin(self, val):
        """
        Visit root object begin

        :type  val: :class:`object`
        :param val: root object
        """
        # TODO: Html tag attribute
        self.stack.append(self.ROOT)

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        self.stack.pop()

    def VisitDoBegin(self, do):
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        if self.stack[-1] == self.LIST:
            # Parent emits tags
            pass
        else:
            self.indentable_output.append('<table>')
            self.indentable_output.indent()
        self.stack.append(self.STRUCT)

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.stack.pop()
        if self.stack[-1] == self.LIST:
            # Parent emits tags
            pass
        else:
            self.indentable_output.dedent()
            self.indentable_output.append('</table>')

    def VisitDoFieldBegin(self, field_name, flags, val):
        """
        Visit data object field begin

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        if self.stack[-2] == self.LIST:
            self.indentable_output.append('<td class="rc">')
        else:
            self.indentable_output.append(
                '<tr><th class="rt">%s</th><td width="90%%" class="rc">' % field_name)

    def VisitDoFieldEnd(self, field_name, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        if self.stack[-2] == self.LIST:
            self.indentable_output.append('</td>')
        else:
            self.indentable_output.append('</td></tr>')

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.indentable_output.append('<table class="sortable">')
        self.indentable_output.indent()
        self.stack.append(self.LIST)

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.stack.pop()
        self.indentable_output.dedent()
        self.indentable_output.append('</table>')

    def VisitListItemBegin(self, idx, flags, val):
        """
        Visit list item begin

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        if idx == 0 and val:
            if isinstance(val, (OrderedDict, StructValue, dict)):
                # Headers
                self.indentable_output.append('<tr>')
                headers = list(val.keys())
                for name in headers:
                    self.indentable_output.append('<th>%s</th>' % name)
                self.indentable_output.append('</tr>')
        self.indentable_output.append('<tr>')
        self.indentable_output.indent()

    def VisitListItemEnd(self, idx, flags, val):
        """
        Visit list item end

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        self.indentable_output.dedent()
        self.indentable_output.append('</tr>')

    # Not used for now
    # def VisitOptionalBegin(self, optionalVal): pass
    # def VisitOptionalEnd(self, optionalVal): pass

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        if self.stack[-1] == self.LIST:
            self.indentable_output.append('<td class="rc">')
        formatted = _FormatPrimitive(val).replace('\n', '<br/>')
        self.indentable_output.append('%s' % XmlEscape(formatted))
        if self.stack[-1] == self.LIST:
            self.indentable_output.append('</td>')


# Python format visitor
class PythonVisitor(BaseVisitor):
    """ Python format visitor """

    def __init__(self, fp=sys.stdout):
        """
        Python format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        BaseVisitor.__init__(self, fp)
        self.current_line = ''

    # Not used for now
    # def VisitRootBegin(self, val): pass

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        self.append(self.current_line)
        self.current_line = ''

    def VisitDoBegin(self, do):
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.current_line += '{'

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.current_line += '}'

    def VisitDoFieldBegin(self, field_name, flags, val):
        """
        Visit data object field begin

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        if (flags & self.FLAG_FIRST_ITEM) != 2:
            self.current_line += ', '
        self.current_line += '"%s": ' % field_name

    def VisitDoFieldEnd(self, field_name, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        pass

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.current_line += '['

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        self.current_line += ']'

    # Not used for now
    # def VisitListItemBegin(self, idx, flags, val):
    #    pass

    def VisitListItemEnd(self, idx, flags, val):
        """
        Visit list item end

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        if (flags & self.FLAG_LAST_ITEM) == 0:
            self.current_line += ', '

    @staticmethod
    def _EscapeStr(val):
        """
        Escape python string

        :type  val: :class:`str`
        :param val: string to escape
        :rtype: :class:`str`
        :return: escaped python str
        """
        return val.replace('\\', '\\\\').replace('\n', '\\n').replace('"',
                                                                      '\\"')

    def _FormatPrimitive(self, val):
        """
        Format primitive

        :type  val: :class:`object`
        :param val: primitive value
        :rtype: :class:`str`
        :return: formatted python str
        """
        result = ''
        if val is None or isinstance(val, VoidValue):
            result = 'None'
        elif isinstance(val, bool):
            result = 'True' if val else 'False'
        elif isinstance(val, BooleanValue):
            result = 'true' if val.value else 'false'
        elif isinstance(val, (SecretValue, StringValue)):
            try:
                result = self._EscapeStr(str(val.value)).join(['"', '"'])
            except UnicodeEncodeError:
                result = self._EscapeStr(repr(val.value)).join(['"', '"'])
        elif isinstance(val, BlobValue):
            result = base64.b64encode(val.value)
        elif isinstance(val, (DataValue, DoubleValue, IntegerValue, float, six.integer_types)):
            result = str(val.value)
        else:
            result = self._EscapeStr(str(val.value)).join(['"', '"'])
        return result

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        val = self._FormatPrimitive(val)
        self.current_line += val


# Json format visitor
#
# Exactly like python vistor, except
# - No trailing , for field / list item
# - true / false (vs True / False)
# - Only double quotes
# - Must escape ", \, /, \b, \f, \n, \r, \t, and no control char in string
# - null instead of None
class JsonVisitor(PythonVisitor):
    """ Json format visitor """
    _escape_lst = [('\\', '\\\\'),
                   ('/', '\/'),  # pylint: disable=W1401
                   # Not a must in python json implementation
                   ('\b', '\\b'),
                   ('\f', '\\f'),
                   ('\n', '\\n'),
                   ('\r', '\\r'),
                   ('\t', '\\t'),
                   ('"', '\\"')]

    def __init__(self, fp=sys.stdout):
        """
        Json format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        PythonVisitor.__init__(self, fp)

    @staticmethod
    def _EscapeStr(val):
        """
        Escape json string

        :type  val: :class:`str`
        :param val: string to escape
        :rtype: :class:`str`
        :return: escaped json str
        """
        # Escape known control chars
        for org, new in JsonVisitor._escape_lst:
            val = val.replace(org, new)

        # TODO: Remove all other control characters
        # return ''.join(ch for ch in val if unicodedata.category(ch)[0] != 'C')
        return val

    def _FormatPrimitive(self, val):
        """
        Format primitive

        :type  val: :class:`object`
        :param val: primitive value
        :rtype: :class:`str`
        :return: formatted json str
        """
        result = ''
        if val is None or isinstance(val, VoidValue):
            result = 'null'
        elif isinstance(val, bool):
            result = 'true' if val else 'false'
        elif isinstance(val, BooleanValue):
            result = 'true' if val.value else 'false'
        elif isinstance(val, (SecretValue, StringValue)):
            try:
                result = self._EscapeStr(str(val.value)).join(['"', '"'])
            except UnicodeEncodeError:
                result = self._EscapeStr(repr(val.value)).join(['"', '"'])
        elif isinstance(val, BlobValue):
            if six.PY3 and isinstance(val.value, str):
                result = base64.b64encode(six.b(val.value))
            else:
                result = base64.b64encode(val.value)
            if six.PY3:
                result = result.decode()
        elif isinstance(val, (DataValue, DoubleValue, IntegerValue, float, six.integer_types)):
            result = str(val.value)
        else:
            result = self._EscapeStr(str(val.value)).join(['"', '"'])

        return result


# Simple format visitor
class SimpleVisitor(BaseVisitor):
    """ Simple format visitor """

    def __init__(self, fp=sys.stdout):
        """
        Table format visitor init

        :type  fp: :class:`file`
        :param fp: output file object
        """
        BaseVisitor.__init__(self, fp)
        self.current_line = ''
        self.indentable_output = IndentableOutput(self.output_lines, inc=3)

    def VisitRootBegin(self, val):
        """
        Visit root object begin

        :type  val: :class:`object`
        :param val: root object
        """
        pass

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        is_dict = isinstance(val, (StructValue, VapiStruct, dict))
        is_list = isinstance(val, (ListValue, OrderedDict))
        if not is_dict and not is_list:
            self.indentable_output.append(self.current_line)
            self.current_line = ''

    def VisitDoBegin(self, do):
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        pass

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        pass

    def VisitDoFieldBegin(self, field_name, flags, val):
        """
        Visit data object field begin

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        self.current_line += '%s:' % field_name
        if check_data_value(val):
            self.current_line += ' '
        else:
            self.indentable_output.append(self.current_line)
            self.current_line = ''
            self.indentable_output.indent()

    def VisitDoFieldEnd(self, field_name, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        if check_data_value(val):
            self.indentable_output.append(self.current_line)
            self.current_line = ''
        else:
            self.indentable_output.dedent()

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        if isinstance(lst, StructValue):
            self.indentable_output.append('')

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        pass

    def VisitListItemBegin(self, idx, flags, val):
        """
        Visit list item begin

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        pass

    def VisitListItemEnd(self, idx, flags, val):
        """
        Visit list item end

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        is_dict = isinstance(val, (OrderedDict, StructValue, dict))
        if (flags & self.FLAG_LAST_ITEM) == 0:
            if is_dict:
                self.indentable_output.append(self.current_line)
                self.current_line = ''
            else:
                self.current_line += ', '
        if not isinstance(val, StructValue) and ((flags & self.FLAG_LAST_ITEM) == 1):
            self.indentable_output.append(self.current_line)
            self.current_line = ''

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        formatted = _FormatPrimitive(val)
        self.current_line += formatted


# CSV format visitor
#
class CsvVisitor(BaseVisitor):
    """ CSV format visitor """

    def __init__(self, fp=sys.stdout):
        BaseVisitor.__init__(self, fp)
        self.check_header = False
        self.quote_level = 0
        self.sep = ","  # Change to ';' for German csv
        self.quote = '"'
        self.current_line = ''

    def _BeginQuote(self):
        """
        Start the quote text in csv formatter
        """
        if self.quote_level > 0:
            self.current_line += self.quote * self.quote_level
        self.quote_level += 1

    def _EndQuote(self):
        """
        End the quote text in csv formatter
        """
        self.quote_level -= 1
        if self.quote_level > 0:
            self.current_line += self.quote * self.quote_level

    def VisitRootBegin(self, val):
        """
        Visit root object begin

        :type  val: :class:`object`
        :param val: root object
        """
        self.check_header = True
        if isinstance(val, (ListValue, OrderedDict)):
            self.quote_level = 0
        else:
            self.quote_level = 1

    def VisitRootEnd(self, val):
        """
        Visit root object end

        :type  val: :class:`object`
        :param val: root object
        """
        if isinstance(val, (ListValue, OrderedDict)):
            assert self.quote_level == 0
        else:
            assert self.quote_level == 1

        if self.current_line:
            self.append(self.current_line)
            self.current_line = ''

    def VisitListBegin(self, lst):
        """
        Visit list begin

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        if lst:
            self._BeginQuote()

    def VisitListEnd(self, lst):
        """
        Visit list end

        :type  lst: :class:`list` (or any iterable)
        :param lst: list object
        """
        if lst:
            self._EndQuote()

    def VisitListItemBegin(self, idx, flags, val):
        """
        Visit list item begin

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        if idx == 0:
            self.check_header = True

    def VisitListItemEnd(self, idx, flags, val):
        """
        Visit list item end

        :type  idx: :class:`int`
        :param idx: list item index
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: list item
        """
        self.check_header = False
        is_dict = isinstance(val, (StructValue, VapiStruct, dict))
        is_list = isinstance(val, (ListValue, OrderedDict))
        if not is_dict:
            if (flags & self.FLAG_LAST_ITEM) == 0:
                self.current_line += self.sep
            elif not is_list:
                self.append(self.current_line)
                self.current_line = ''

    def VisitDoBegin(self, do):
        """
        Visit data object begin

        :type  do: :class:`object`
        :param do: struct like data object
        """
        if self.check_header:
            field_names = []
            if isinstance(do, StructValue):
                output_info = next(
                    (field_info for field_info in self.output_field_list
                     if field_info.structure_id == do.name), None)
                metamodel_info = next(
                    (struct_info for struct_info in self.metamodel_struct_list
                     if struct_info.name == do.name), None)

                if self.should_apply_structure_filter_visitor is None:
                    should_apply_struct_filter = True
                else:
                    should_apply_struct_filter =\
                        self.should_apply_structure_filter_visitor(do, metamodel_info)

                if output_info:
                    field_names = [output_field.field_name for output_field in
                                   output_info.output_fields
                                   if (not should_apply_struct_filter
                                       or self.should_visit_struct_el is None
                                       or self.should_visit_struct_el(
                                           output_field.field_name, do,
                                           metamodel_info))]
                else:
                    field_names = [field for field in do.get_field_names()
                                   if (not should_apply_struct_filter
                                       or self.should_visit_struct_el is None
                                       or self.should_visit_struct_el(field, do,
                                                                      metamodel_info))]
            elif isinstance(do, VapiStruct):
                field_names = [k for k, _ in inspect.getmembers(do) if
                               not k.startswith('_')]
            elif isinstance(do, dict):
                field_names = list(do.keys())

            self.current_line += self.sep.join(field_names)
            self.append(self.current_line)
            self.current_line = ''
        self.check_header = False

    def VisitDoEnd(self, do):
        """
        Visit data object end

        :type  do: :class:`object`
        :param do: struct like data object
        """
        self.append(self.current_line)
        self.current_line = ''

    def VisitDoFieldBegin(self, fieldName, flags, val):
        """
        Visit data object field begin

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        if (flags & self.FLAG_FIRST_ITEM) != 2:
            self.current_line += self.sep
        is_dict = isinstance(val, (StructValue, VapiStruct, dict))
        if is_dict:
            self._BeginQuote()

    def VisitDoFieldEnd(self, fieldName, flags, val):
        """
        Visit data object field end

        :type  field_name: :class:`str`
        :param field_name: field name
        :type  flags: :class:`int`
        :param flags: refer to :class:`BaseVisitor` flags
        :type  val: :class:`object`
        :param val: field value
        """
        is_dict = isinstance(val, (StructValue, VapiStruct, dict))
        if is_dict:
            self._EndQuote()

    def VisitPrimitive(self, val):
        """
        Visit primitive type

        :type  val: :class:`object`
        :param val: python primitive object
        """
        # Escape multi lines output, and escape comma
        formatted = _FormatPrimitive(val)
        quote_formatted = False

        # Follow the csv wiki / RFC4180:
        # Enclosed val with double quotes if val contains , " or line break
        # Also esacpe double quotes with double quote
        if formatted.find(self.sep) >= 0:
            quote_formatted = True
        if formatted.find("\n") >= 0:
            # TODO: Use the following if \n is allowed in string value
            # quote_formatted = True

            # Escape \n in string value
            formatted = formatted.replace("\n", "\\n")
        if formatted.find(self.quote) >= 0:
            # Escape double quote
            formatted = formatted.replace(self.quote,
                                          self.quote * self.quote_level * 2)
            quote_formatted = True
        if quote_formatted:
            quotes = self.quote * self.quote_level
            self.appendLines([quotes, formatted, quotes])
        else:
            self.current_line += formatted


class Formatter(object):
    """
    Output formatter class
    """
    formatters = {
        'xml': XmlVisitor,
        'html': HtmlVisitor,
        'json': JsonVisitor,
        'table': TableVisitor,
        'csv': CsvVisitor,
        'simple': SimpleVisitor,
    }

    def __init__(self, format_, fp=sys.stdout):
        """
        Formatter class init method

        :type  format_: :class:`str`
        :param format_: formatter type
        :type  fp: :class:`file`
        :param fp: output file object
        """
        if format_ is None:
            format_ = 'simple'
        self.fp = fp
        format_method = Formatter.formatters.get(format_.lower(), SimpleVisitor)
        self.output_formatter = format_method(self.fp)
        self.should_apply_structure_filter_visitor = None
        self.should_visit_struct_el = None

    def format_output(self, output, more=False, struct_value=None,
                      metamodel_struct_list=None):
        """
        Method to format output of vAPI operation

        :type  output: :class:`vmware.vapi.data.value.DataValue`
        :param output: Output data value
        :type  struct_value: :class:`dict`
        :param struct_value: Output field mapping from CLI metadata
        """
        if isinstance(output, VoidValue):
            return

        if self.should_apply_structure_filter_visitor:
            self.output_formatter.apply_structure_filter_visitor(
                self.should_apply_structure_filter_visitor)
        if self.should_visit_struct_el:
            self.output_formatter.structure_element_visit(
                self.should_visit_struct_el)
        self.output_formatter.Format(output, more, struct_value,
                                     metamodel_struct_list)

    def structure_element_visit(self, fn):
        """
        Assing function to the should_visit_struct_el handler

        :param fn: predicate function to execute before each formatter's strucutre element visit
        :type fn: Function
        """
        self.should_visit_struct_el = fn

    def apply_structure_filter_visitor(self, fn):
        """
        Assing function to the should_apply_structure_filter_visitor handler. Function is a
        predicate which checks whether to apply the structure_element_visit handler

        :param fn: predicate function which checks whether to apply the structure_element_visit handler
        :type fn: Function
        """
        self.should_apply_structure_filter_visitor = fn
