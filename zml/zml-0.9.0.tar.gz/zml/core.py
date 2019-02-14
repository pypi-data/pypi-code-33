from copy import deepcopy
import os
from zml.exceptions import (TemplateNotDefinedException,
                            IndentationException,
                            VariableNotDefinedException,
                            TranslationNotDefinedException)
from zml.util import load_file, find_file_in_dirs
from zml.semantic import *
from pprint import pprint
import math


base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)


num_spaces_per_indent = 2


def deb(obj):
    pprint(obj.asDict())


class Path(object):

    def __init__(self, template):
        self.template = template

    def execute(self, context, *args, **kwargs):
        action = context['context']['action']
        if action in self.template.router['routes']:
            route = self.template.router['routes'][action]
            url = ''
            for item in route:
                if 'path_segment' in item:
                    url += '/' + item[1][0]

                elif 'path_variable' in item:
                    path_variable = item[1][0]
                    if path_variable in context['context']:
                        url += '/' + context['context'][path_variable]
            return url


framework_components = {
    'path': Path,
    'sin': math.sin,
    'pi': math.pi
}


class RenderingContext(object):

    def get_var(self, variable_descriptor):
        if variable_descriptor in self.local_context:
            return self.local_context[variable_descriptor]
        if variable_descriptor in self.global_context:
            return self.global_context[variable_descriptor]
        raise VariableNotDefinedException

    def set_var(self, variable_descriptor, value):
        self.local_context[variable_descriptor] = value


class NodeRenderingContext(RenderingContext):
    pass


class TemplateRenderingContext(RenderingContext):

    def __init__(self, global_context={}, local_context={}):
        self.local_context = local_context
        self.router = dict()
        self.global_context = dict()
        self.global_context['_resources'] = dict()
        self.global_context['_translations'] = dict()
        self.global_context['_models'] = dict()
        if global_context is not None:
            self.global_context.update(global_context)
        self.namespaces = dict()
        self.namespaces['_default'] = dict()
        self.translations = dict()

    def get_translation(self, variable_descriptor, language=None):
        if language is None:
            try:
                language = next(iter(self.translations))
            except Exception:
                raise TranslationNotDefinedException
        if variable_descriptor in self.translations[language]:
            return self.translations[language][variable_descriptor]
        raise TranslationNotDefinedException

    def set_translation(self, language, variable_descriptor, value):
        if language not in self.translations:
            self.translations[language] = dict()
        self.translations[language][variable_descriptor] = value


class TreeNode:

    def __init__(self, line='', is_root=False, is_ancestor=False, ancestor=None, base_indent=0):
        self.line = line
        self.base_indent = base_indent
        self.children = []
        self.value = None
        self.is_root = is_root
        self.is_ancestor = is_ancestor
        if ancestor is None:
            # explicitly state logic here to be clear that in both cases ancestor is set to self
            if self.is_ancestor:
                self.ancestor = self
            else:
                self.ancestor = self
        else:
            self.ancestor = ancestor
        indentation = len(line) - len(line.lstrip())
        if indentation % num_spaces_per_indent != 0:
            raise IndentationException
        self.level = int(indentation / num_spaces_per_indent)
        self.render_level = 0
        self.base_render_level = 0

    def __repr__(self):
        # return '{}\n{}'.format(self.line, json.dumps(self.local_context, indent=2))
        return "{}({})\n".format(self.__class__.__name__, self.line)

    def add_children(self, nodes):
        childlevel = nodes[0].level
        while nodes:
            node = nodes.pop(0)
            node.ancestor = self
            if node.level == childlevel:
                if self.is_ancestor:
                    node.ancestor = self
                    node.local_context = {}
                # add node as a child
                self.children.append(node)
            elif node.level > childlevel:
                # add nodes as grandchildren of the last child
                # if self.children[-1].is_ancestor:
                #     node.ancestor = self.children[-1]
                #     node.local_context = self.children[-1].local_context
                nodes.insert(0, node)
                self.children[-1].add_children(nodes)
            elif node.level <= self.level:
                # this node is a sibling, no more children
                nodes.insert(0, node)
                return

    def is_data(self):
        if self.is_root:
            return False
        else:
            return self.parent.is_data()


class Egg(TreeNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Operator(object):
    pass


def get_meta_data(obj, property_descriptor):
    if property_descriptor == 'descriptor':
        value = obj.descriptor
    elif property_descriptor == 'label':
        value = obj.label
    elif property_descriptor == 'type':
        value = obj.type
    return value


def get_property(obj, property_descriptor):
    value = obj[property_descriptor]
    return value


def get_combined_properties(value, properties):
    for property_item in properties:
        # currently we only handle dict properties. future implementations will handle
        # list item accessors with dot-number syntax (.0 for first element, .1 for second etc.)
        property_descriptor = property_item[1][0]
        if property_item[0] == 'property':
            value = get_property(value, property_descriptor)
        elif property_item[0] == 'meta_data':
            value = get_meta_data(value, property_descriptor)
    return value


def eval_context_item(res, node):
    if 'context_item' in res:
        value = node.get_var(res['context_item'])
        if isinstance(value, Model):
            value = value
    elif 'model_descriptor' in res:
        value = node.template.models[res['model_descriptor']].fields
    if 'properties' in res:
        properties = res['properties']
        value = get_combined_properties(value, properties)
    return value


def eval_model(res, node):
    if 'model_descriptor' in res:
        return node.template.models[res['model_descriptor']]


def render_context_item(res, node):
    return str(eval_context_item(res, node))


def eval_translation(res, node):
    translation_descriptor = res['translation_descriptor']
    if 'properties' in res:
        value = node.template.get_translation(translation_descriptor, node.template.language)
        for property_item in res['properties']:
            property_descriptor = property_item[1][0]
            value = value[property_descriptor]
    else:
        value = node.template.get_translation(translation_descriptor, node.template.language)
    return value


def render_translation(res, node):
    return str(eval_translation(res, node))


class Processor(Operator):

    def __init__(self, render=False, lazy=False):
        self.lazy = lazy

    def subtree_handler_default(self, node):
        for child in node.children:
            child.process_subtree(self)
        return ''

    def process(self, node):
        node.process(lazy=self.lazy)
        self.subtree_handler_default(node)

    def subtree_handler_for_loop(self, node):
        # prepare
        # iterator_descriptor = node.tokens['iterator']
        variable_descriptor = node.tokens['variable']
        if not self.lazy:
            iterator = eval_context_item(node.tokens, node)
            if isinstance(iterator, Model):
                iterator = iterator.values()
            for item in iterator:
                node.set_var(variable_descriptor, item)
                # execute
                self.subtree_handler_default(node)
#        else:
#            self.subtree_handler_default(node)

    def subtree_handler_if_statement(self, node):
        # prepare
        condition = eval_context_item(node.tokens, node)
        if not self.lazy:
            if condition:
                # execute
                self.subtree_handler_default(node)
        else:
            self.subtree_handler_default(node)


class Renderer(Operator):

    def __init__(self, render=False, lazy=False, base_render_level=0):
        self.base_render_level = base_render_level
        self.lazy = lazy

    def subtree_handler_default(self, node):
        out = ''
        for child in node.children:
            out += child.render_subtree(self)
        return out

    def render(self, node):
        node.render()
        out = ''
        out += node.leading
        out += self.subtree_handler_default(node)
        out += node.trailing
        return out

    def subtree_handler_for_loop(self, node):
        # prepare
        out = ''
        if not self.lazy:
            variable_descriptor = node.tokens['variable']
            iterator = eval_context_item(node.tokens, node)
            if isinstance(iterator, Model):
                iterator = iterator.fields.values()
            for item in iterator:
                node.set_var(variable_descriptor, item)
                # execute
                out += self.subtree_handler_default(node)
        else:
            out += self.subtree_handler_default(node)
        return out

    def subtree_handler_if_statement(self, node):
        # prepare
        out = ''
        if not self.lazy:
            condition = eval_context_item(node.tokens, node)
            if condition:
                # execute
                out += self.subtree_handler_default(node)
        else:
            out += self.subtree_handler_default(node)
        return out


class Node(TreeNode, NodeRenderingContext):

    expression = ELEMENT

    def __init__(self, line, template=None, expression=None, global_context={}, local_context={},
                 descriptor=None, base_indent=0, *args, **kwargs):
        super().__init__(line, *args, **kwargs)
        self.line = line
        self.descriptor = descriptor
        self.local_context = local_context
        self.global_context = global_context
        self.minimise = False
        self.leading = ''
        self.trailing = ''
        self.is_component = False
        self.is_code = False
        self.has_list_items = False
        self.line = line.strip()
        self.template = template
        self.out = ()
        if self.is_root:
            self.level = -1

    def process(self, lazy=False):
        if not lazy and self.is_root is False:
            self.expression.setParseAction(self.parse)
            res = self.expression.parseString(self.line)
            self.render_parts(res)

    def render(self):
        if self.is_root is False:
            self.expression.setParseAction(self.parse)
            res = self.expression.parseString(self.line)
            self.render_parts(res)
        else:
            return ''

    def is_list(self):
        return self.has_list_items

    def parse(self, s, l, t):
        return t

    def render_parts(self, res):
        self.leading = self.render_leading(res)
        self.trailing = self.render_trailing(res)

    def render_indent(self):
        render_level = (self.ancestor.base_render_level + self.render_level)
        indent = ' ' * self.base_indent + ' ' * render_level * 2
        return indent

    def render_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        attributes = self.render_attributes(res)
        id_classes = self.render_id_classes(res)
        out = '<{}{}{}>'.format(descriptor, id_classes, attributes)
        return out

    def render_inline_start_tag(self, res):
        descriptor = self.render_descriptor(res)
        attributes = self.render_attributes(res)
        id_classes = self.render_id_classes(res)
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        out = '<{}{}{}>{}'.format(descriptor, id_classes, attributes, value)
        return out

    def render_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = ''
        if descriptor in void_elements:
            out += ''
        else:
            if not self.minimise and descriptor not in inline_elements:
                render_level = (self.ancestor.base_render_level + self.render_level)
                out += ' ' * self.base_indent + ' ' * render_level * 2
            out += '</{}>'.format(descriptor)
            if not self.minimise:
                out += '\n'
        return out

    def render_inline_end_tag(self, res):
        descriptor = self.render_descriptor(res)
        out = '</{}>'.format(descriptor)
        return out

    def render_inline_semantics(self, res):
        out = ''
        out += self.render_inline_start_tag(res)
        out += res['inline_semantic_content_words']
        out += self.render_inline_end_tag(res)
        return out

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        start_tag = self.render_start_tag(res)
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + value
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading

    def render_trailing(self, res):
        return self.render_end_tag(res)

    def render_descriptor(self, res):
        if 'descriptor' in res:
            return res['descriptor']
        else:
            return ''

    def eval_arith_expression(self, res):
        expr = ''.join(res['arith_expression'])
        del exprStack[:]
        ARITH_EXPRESSION.parseString(expr, parseAll=True)
        return evaluateStack(exprStack)

    def eval_boolean(self, res):
        if res['boolean'] == 'True':
            return True
        elif res['boolean'] == 'False':
            return False

    def render_boolean(self, res):
        return str(self.eval_boolean(res))

    def eval_literal(self, res):
        # note that this works by using addParseAction(removeQuotes) in LITERAL
        value = res['literal']
        return value

    def render_literal(self, res):
        return str(self.eval_literal(res))

    def eval_expression(self, res):
        if 'arith_expression' in res:
            return self.eval_arith_expression(res)
        elif 'boolean' in res:
            return self.eval_boolean(res)
        elif 'literal' in res:
            return self.eval_literal(res)
        elif 'framework_component' in res:
            return self.eval_framework_component(res)
        elif 'component_descriptor' in res:
            return self.eval_component(res)
        elif 'value_accessor' in res:
            # might lead to endless loop ?
            return self.eval_value_accessor(res)
        elif 'context_item' in res or 'context_item_with_property' in res:
            return eval_context_item(res, self)
        elif 'translation_accessor' in res:
            return eval_translation(res, self)

    def eval_attribute_value(self, attribute):
        if 'moustache' in attribute:
            attribute_value = self.render_moustache(attribute)
        elif 'quoted_string' in attribute:
            attribute_value = attribute['quoted_string']
        elif 'number' in attribute:
            attribute_value = attribute['number']
        elif 'literal' in attribute:
            attribute_value = attribute['literal']
        elif 'context_item' in attribute:
            return eval_context_item(attribute, self)
        elif 'model_descriptor' in attribute:
            return eval_model(attribute, self)
        return attribute_value

    def render_attribute(self, attribute):
        out = ' '
        out += attribute['attribute_key']
        if 'attribute_value' in attribute:
            out += '="{}"'.format(self.eval_attribute_value(attribute))
        return out

    def render_attributes(self, res):
        if 'attributes' in res:
            return ' '.join(
                [''.join(
                    [self.render_attribute(attribute) for attribute in res['attributes']]
                )]
            )
        else:
            return ''

    def render_id_classes(self, res):
        out = ''
        if 'id_classes' in res:
            if 'uid' in res:
                out += ' id="{}"'.format(res['uid'][0])
            if 'classes' in res:
                out += ' class="{}"'.format(' '.join(res['classes']))
        return out

    def render_inline_content(self, res):
        out = ''
        if 'inline_content' in res:
            inline_content_items = res['inline_content']
            for item in inline_content_items:
                itemtype = item[0]
                if itemtype == 'inline_content_words':
                    out += self.render_words(item[1][0])
                if itemtype == 'inline_semantics':
                    out += self.render_inline_semantics(item[1])
                if itemtype == 'moustache':
                    out += self.render_moustache(item[1])
#                if itemtype == 'translation_accessor':
#                    out += render_translation(item[1], self)
        return out

    def render_words(self, res):
        out = res
        return out

    def eval_value_accessor(self, res):
        return self.get_var('_value')

    def render_value_accessor(self, res):
        return self.eval_value_accessor(res)

    def render_component(self, res):
        # prepend local indent on each line
        namespace = self.template.namespace
        component_descriptor = res['component_descriptor']
        component = None
        # rendered_view_source = local_indent
        rendered_view_source = ''
        if component_descriptor in self.template.namespaces[namespace]:
            component = self.template.namespaces[namespace][component_descriptor]
        elif component_descriptor in self.inherited_template.namespaces[namespace]:
            component = self.inherited_template.namespaces[namespace][component_descriptor]
        if component:
            component_node = deepcopy(component)
            component_node.parent = self
            # component_node.ancestor = self.ancestor
            component_node.base_render_level = self.render_level
            if not self.parent.is_component and not self.parent.is_code:
                component_node.base_render_level += 1

            component_node.render_level = component_node.base_render_level
            # local_indent = ' ' * self.render_level * 2
            renderer = Renderer(base_render_level=self.render_level)
            rendered_component = component_node.render_subtree(renderer)
            rendered_view_source += rendered_component
        # strip last newline, as it would double with the inline content's trailing newline
        rendered_view_source = rendered_view_source.rstrip()
        # prepend newline, because view will be included in inline content,
        # which is missing a leading newline
        return '\n' + rendered_view_source

    def eval_framework_component(self, res):
        framework_component = res['framework_component']
        if 'moustache_attributes' in res:
            params = dict()
            for attribute in res['moustache_attributes']:
                key = attribute['moustache_attribute_key']
                value = attribute['moustache_attribute_value']
                if value == '_context':
                    value = self.local_context
                params[key] = value
            return framework_components[framework_component](self.template).execute(params)

    def render_framework_component(self, res):
        return self.eval_framework_component(res)

    def render_moustache(self, res):
        out = ''
        if 'framework_component' in res:
            out += self.render_framework_component(res)
        elif 'component_descriptor' in res:
            out += self.render_component(res)
        elif 'value_accessor' in res:
            out += self.render_value_accessor(res)
        elif 'context_item' in res:
            out += render_context_item(res, self)
        elif 'translation_accessor' in res:
            out += render_translation(res, self)
        return out

    def process_subtree(self, processor=None):
        if processor is None:
            processor = Processor(lazy=True)
        processor.process(self)

    def render_subtree(self, renderer=None):
        if renderer is None:
            renderer = Renderer()
        out = renderer.render(self)
        return out

    def get_children_type(self):
        return None


class EmptyNode(Node):

    def render_leading(self, res):
        descriptor = self.render_descriptor(res)
        start_tag = ''
        inline_content = self.render_inline_content(res)
        leading = ''
        if not self.minimise:
            leading += self.render_indent()
        leading += start_tag + inline_content
        if not self.minimise and descriptor not in inline_elements:
            leading += '\n'
        return leading


class ComponentNode(Node):

    expression = LINE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_component = True
        self.caller_inline_content = None
        self.caller_children = None

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        descriptor = self.tokens['descriptor']
        # self.local_context[descriptor] = self.childsource
        if self.template.namespace not in self.template.namespaces:
            self.template.namespaces[self.template.namespace] = dict()
        self.template.namespaces[self.template.namespace][descriptor] = self

    def render(self):
        self.process()


class ComponentCallNode(Node):

    expression = COMPONENT_CALL

    def process(self, lazy=False):
        if not lazy:
            self.expression.setParseAction(self.parse)
            self.tokens = self.expression.parseString(self.line)

    def render(self):
        self.process()
        namespace = self.tokens['namespace']
        descriptor = self.tokens['component_descriptor']
        component_node = deepcopy(self.template.namespaces[namespace][descriptor])
        component_node.parent = self.parent
        component_node.ancestor = self.ancestor
        # the component call inherits the total render_level of parent and the parent's ancestor to the component
        component_node.base_render_level = self.parent.render_level + self.parent.ancestor.base_render_level
        if 'inline_content' in self.tokens:
            component_node.caller_inline_content = self.tokens['inline_content']
        component_node.caller_children = self.children
        renderer = Renderer(base_render_level=self.render_level)
        if not self.parent.is_component and not self.parent.is_code:
            component_node.base_render_level += 1
        if 'attributes' in self.tokens:
            for attribute in self.tokens['attributes']:
                attribute_key = attribute['attribute_key']
                attribute_value = self.eval_attribute_value(attribute)
                component_node.set_var(attribute_key, attribute_value)
        if 'inline_content' in self.tokens:
            value = self.render_inline_content(self.tokens)
            component_node.set_var('_value', value)
        children = []
        for child in self.children:
            children.append(child.render_subtree(renderer))
        component_node.set_var('_children', children)
        out = ''
        out += component_node.render_subtree(renderer)
        self.leading = out
        return out


class ListItemNode(Node):

    expression = LIST_ITEM

    def process(self):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        self.parent.has_list_items = True
        # if self.parent.descriptor not in self.local_context:
        #    self.set_var(self.parent.descriptor, list())
        if not isinstance(self.parent.value, list):
            self.parent.value = list()
        if isinstance(self.parent, DataNode):
            # self.template.local_context[self.parent.descriptor] = self.parent.value
            self.local_context[self.parent.descriptor] = self.parent.value
        self.value = dict()
        self.parent.value.append(self.value)

    def render(self):
        self.process()


class TranslationNode(Node):

    expression = TRANSLATION

    def process(self, lazy=False):
        self.value = dict()
        self.template.translations[self.descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return AssignmentNode


class AssignmentNode(Node):

    expression = ASSIGNMENT

    def process(self):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        value = ''
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        self.parent.set_var(descriptor, value)
        if isinstance(self.parent, AssignmentNode) or isinstance(self.parent, ListItemNode) or isinstance(self.parent,
                                                                                                          TranslationNode):
            if self.parent.value is None:
                self.parent.value = dict()
            if value:
                self.parent.value[descriptor] = value
            else:
                self.value = dict()
                self.parent.value[descriptor] = self.value
        elif isinstance(self.parent, DataNode):
            if self.local_context[self.parent.descriptor] is None:
                self.local_context[self.parent.descriptor] = dict()
            if value:
                self.local_context[self.parent.descriptor][descriptor] = value
            else:
                self.value = dict()
                self.local_context[self.parent.descriptor][descriptor] = self.value

    def render(self):
        self.process()


class FieldPropertyNode(Node):

    expression = ASSIGNMENT

    def process(self, lazy=True):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        glyph = res['glyph']
        if 'inline_content' in res:
            value = self.render_inline_content(res)
        elif 'expression' in res:
            value = self.eval_expression(res)
        if glyph == '@':
            # define meta data
            if descriptor == 'type':
                self.parent.value.type = value
            if descriptor == 'label':
                self.parent.value.label = value

    def render(self):
        self.process()


class Field:

    def __init__(self, descriptor):
        self.descriptor = descriptor
        self.type = None
        self.label = ''


class FieldNode(Node):

    expression = FIELD

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['field_descriptor']
        self.value = Field(descriptor)
        self.parent.value.fields[descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return FieldPropertyNode


class Model:

    def __init__(self, descriptor):
        self.descriptor = descriptor
        self.fields = dict()


class ModelNode(Node):

    expression = MODEL

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['model_descriptor']
        self.value = Model(descriptor)
        self.template.models[self.descriptor] = self.value

    def render(self):
        self.process()

    def get_children_type(self):
        return FieldNode


class ResourceNode(Node):

    def process(self, lazy=False):
        pass


class RouteNode(Node):

    expression = ROUTE

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        res = self.expression.parseString(self.line)
        router_descriptor = self.parent.descriptor
        route_descriptor = res['descriptor']
        # currently also nodes have a global_context and a local_context
        # todo design decision for rendering contexts (see module's render_source function)
        router = self.template.router
        if router_descriptor not in router:
            router[router_descriptor] = dict()
        router[router_descriptor][route_descriptor] = res['route_path']

    def render(self):
        self.process()


class RouterNode(Node):

    expression = LINE

    def process(self, lazy=False):
        pass

    def get_children_type(self):
        return RouteNode


class DataNode(Node):

    expression = LINE

    def is_data(self):
        return True

    def process(self, lazy=False):
        res = self.expression.parseString(self.line)
        descriptor = res['descriptor']
        self.local_context[descriptor] = self.value

    def render(self):
        self.process()


class CodeNode(Node):

    expression = CODE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_code = True

    def process_subtree(self, processor):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        if 'for_loop' in self.tokens:
            processor.subtree_handler_for_loop(self)
        elif 'if_statement' in self.tokens:
            processor.subtree_handler_if_statement(self)

    def render_subtree(self, renderer):
        self.expression.setParseAction(self.parse)
        self.tokens = self.expression.parseString(self.line)
        out = ''
        if 'for_loop' in self.tokens:
            out += renderer.subtree_handler_for_loop(self)
        elif 'if_statement' in self.tokens:
            out += renderer.subtree_handler_if_statement(self)
        return out


class InstructionNode(Node):

    expression = INSTRUCTION

    def process_inherit(self, res):
        templatefile = res['templatefile']
        if not templatefile.endswith('.zml'):
            templatefile += '.zml'
        self.template.inheriting_template = templatefile

    def process_import(self, res):
        templatefile = res['templatefile']
        if not templatefile.endswith('.zml'):
            templatefile += '.zml'
        root = self.template.import_template(templatefile)
        return root

    def process_include(self, res):
        out = render(filename,
                     local_context=self.template.local_context,
                     base_indent=base_indent)
        return out

    def process_namespace(self, res):
        namespace = res['namespace']
        self.template.namespace = namespace

    def process(self, lazy=False):
        self.expression.setParseAction(self.parse)
        res = self.expression.parseString(self.line)
        instruction = res['instruction']
        if instruction == 'inherit':
            self.process_inherit(res)
        elif instruction == 'import':
            self.process_import(res)
        elif instruction == 'include':
            self.process_include(res)
        elif instruction == 'namespace':
            self.process_namespace(res)

    def render(self, lazy=False):
        self.process(lazy)
        return ''


type_mapping = {
    '*': ComponentNode,
    '&': ResourceNode,
    '+': ModelNode,
    '~': RouterNode,
    '!': TranslationNode,
    '$': DataNode,
    '%': CodeNode,
    '#': InstructionNode,
    '-': ListItemNode
}


def get_data_node(line, template, base_indent=0):
    res = LINE.parseString(line)
    if 'list_item_glyph' in res:
        return ListItemNode(line, template=template, global_context=template.global_context, base_indent=base_indent)
    else:
        res = ASSIGNMENT.parseString(line)
        if 'descriptor' in res:
            return AssignmentNode(line, template=template, global_context=template.global_context, base_indent=base_indent)


def get_template_node(line, template, base_indent=0):
    res = LINE.parseString(line)
    if 'descriptor' in res:
        if 'glyph' in res:
            glyph = res['glyph']
            if glyph in type_mapping:
                descriptor = res['descriptor']
                return type_mapping[glyph](line, template=template, is_ancestor=True, descriptor=descriptor,
                                           global_context=template.global_context, base_indent=base_indent)
        else:
            return Node(line, template=template, global_context=template.global_context, base_indent=base_indent)
    elif 'namespace_descriptor' in res:
        return ComponentCallNode(line, template=template, global_context=template.global_context, base_indent=base_indent)
    else:
        return EmptyNode(line, template=template, global_context=template.global_context, base_indent=base_indent)


def set_base_path(base_path):
    os.chdir(base_path)


def render(tempsource, local_context={}, path=None,
           global_context=None, getparams={}, postparams={}, base_indent=0):
    if tempsource.endswith('.zml'):
        return render_template(tempsource, local_context=local_context, global_context=global_context)
    else:
        return render_source(tempsource, local_context, global_context=global_context, base_indent=base_indent)


def render_template(templatefile, local_context={}, path=None,
           global_context=None, getparams={}, postparams={}, base_indent=0):
    lookup = TemplateLookup(['.'])
    t = lookup.get_template(templatefile, local_context=local_context, global_context=global_context)
    out = t.render(path=path,
                   getparams=getparams, postparams=postparams, base_indent=base_indent)
    return out


def render_source(source,
                local_context={},
                indent_global='',
                source_indent_level=0,
                local_context_item='_root',
                global_context=None,
                path=None,
                getparams={},
                postparams={},
                base_indent=0):
    template = Template(source=source, local_context=local_context, global_context=global_context)
    root = template.source_to_tree(source)
    out = root.render_subtree()
    if template.inheriting_template:
        # here we set local_context of inheriting template to local_context of inherited template
        # todo: decide how we design the scopes of contexts
        inheriting_template = Template(template.inheriting_template, inherited_template=template)
        out = inheriting_template.render(local_context=template.local_context,
                                         base_indent=base_indent)
    return out


class Template(TemplateRenderingContext):

    def __init__(self, filename=None, source=None, lookup=None,
                 viewhelperdir=None, base_indent=0, namespaces={},
                 inherited_template=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.source = source
        self.lookup = lookup
        self.base_indent = base_indent
        self.namespace = '_default'
        self.namespaces = namespaces
        self.models = dict()
        self.inheriting_template = None
        self.inherited_template = inherited_template
        self.viewhelperdir = viewhelperdir
        self.localpage = dict()
        self.namespacemode = False
        self.language = None
        self.request = dict()
        self.request['get'] = dict()
        self.request['post'] = dict()
        self.raw_mode = False

    def render(
            self,
            filename=None,
            source=None,
            local_context={},
            path=None,
            getparams={},
            postparams={},
            base_indent=None
    ):
        if base_indent is None:
            base_indent = self.base_indent
        zmlsource = None
        if filename:
            template_path = self.get_absolute_path(filename)
            zmlsource = load_file(template_path)
        elif source:
            zmlsource = source
        elif self.filename:
            template_path = self.get_absolute_path(self.filename)
            zmlsource = load_file(template_path)
        elif self.source:
            zmlsource = self.source
        if zmlsource:
            result = self.render_source(zmlsource, self.local_context,
                                 path=path, getparams=getparams,
                                 postparams=postparams, base_indent=base_indent)
            return result
        else:
            raise TemplateNotDefinedException

    # todo: eventually rename to load, design loading concept for zml
    def import_template(
            self,
            filename=None,
            source=None,
            path=None,
            getparams={},
            postparams={},
            base_indent=None
    ):
        if base_indent is None:
            base_indent = self.base_indent
        zmlsource = None
        if filename:
            template_path = self.get_absolute_path(filename)
            zmlsource = load_file(template_path)
        elif source:
            zmlsource = source
        elif self.filename:
            template_path = self.get_absolute_path(self.filename)
            zmlsource = load_file(template_path)
        elif self.source:
            zmlsource = self.source
        imported_template = Template(source=zmlsource, local_context=self.local_context,
                                     global_context=self.global_context)
        imported_template.router = self.router

        if zmlsource:
            imported_template.translations = self.translations
            imported_template.import_source(zmlsource,
                                        path=path, getparams=getparams,
                                        postparams=postparams, base_indent=base_indent)
            self.namespaces.update(imported_template.namespaces)
        else:
            raise TemplateNotDefinedException

    def get_absolute_path(self, filename):
        if filename is None:
            raise TemplateNotDefinedException
        if self.lookup is None:
            self.lookup = TemplateLookup(['.'])
        absolute_path = self.lookup.get_absolute_path(filename)
        return absolute_path

    def create_node_from_egg(self, egg, parent):
        # set parent, so is_data can check data context
        egg.parent = parent
        # check if parent forces children type, otherwise set type by parsing line
        if parent.get_children_type():
            node = parent.get_children_type()(egg.line, template=self)
        else:
            if parent.is_data() or isinstance(parent, AssignmentNode):
                node = get_data_node(egg.line, template=self)
            else:
                node = get_template_node(egg.line, template=self)
        node.children = egg.children
        return node

    def set_relations(self, node, ancestor, render_level=-1):
        node.render_level = render_level
        if not node.line.startswith('%') and not node.line.startswith('*'):
            render_level += 1
        if node.line.startswith('*'):
            node.is_ancestor = True
            node.local_context = node.local_context = node.template.local_context
            ancestor = node
        elif node.line.startswith('$'):
            node.local_context = node.ancestor.local_context
            node.value = None
            node.template.local_context[node.descriptor] = node.value
            ancestor = node.ancestor
        else:
            ancestor = node.ancestor
            node.local_context = node.ancestor.local_context
        for i, child in enumerate(node.children):
            node.children[i] = self.create_node_from_egg(child, node)
            node.children[i].parent = node
            node.children[i].ancestor = ancestor
            node.children[i].minimise = node.minimise
            self.set_relations(node.children[i], ancestor=node, render_level=render_level)

    def source_to_tree(self, source, base_indent=0):
        root = Node('root', local_context=self.local_context, is_root=True, is_ancestor=True, base_indent=base_indent)
        root.template = self
        root.add_children([Egg(line, base_indent) for line in source.splitlines() if line.strip()])
        self.set_relations(root, ancestor=root)
        return root

    def render_source(self, source=None,
                    local_context={},
                    indent_global='',
                    source_indent_level=0,
                    local_context_item='_root',
                    global_context=None,
                    path=None,
                    getparams={},
                    postparams={},
                    base_indent=None):
        if base_indent is None:
            base_indent = self.base_indent
        root = self.source_to_tree(source, base_indent=base_indent)
        out = root.render_subtree()
        return out

    def import_source(self, source=None,
                    indent_global='',
                    source_indent_level=0,
                    local_context_item='_root',
                    path=None,
                    getparams={},
                    postparams={},
                    base_indent=None):
        if base_indent is None:
            base_indent = self.base_indent
        root = self.source_to_tree(source, base_indent=base_indent)
        root.process_subtree()
        return root

    def get_language(self, language):
        return self.language

    def set_language(self, language):
        self.language = language


class TemplateLookup(object):

    def __init__(self, directories=None,
                 module_directory=None, input_encoding=None):
        self.directories = directories

    def get_template(self, filename, local_context={}, global_context={}):
        find_file_in_dirs(filename, self.directories)
        return Template(filename=filename, lookup=self,
                        local_context=local_context, global_context=global_context)

    def get_absolute_path(self, filename):
        find_file_in_dirs(filename, self.directories)
        return filename
