import os
import yaml
from urllib.request import urlopen

from django.core.exceptions import ObjectDoesNotExist
from ..models import ComputationalToolInputType, ComputationalToolInput, ComputationalWF
from ..models import ComputationalWFStep, ComputationalWFStepInput

from ..models import ComputationalTool, ComputationalToolCWLImport


def create_computationaltool(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalTool.objects.create(**defaults)


def create_computationaltoolcwlimport(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalToolCWLImport.objects.create(**defaults)


def create_computationalWF(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalWF.objects.create(**defaults)


def get_type(type_dict):
    t = ''
    o = False
    a = False
    if 'type' in type_dict:
        t = type_dict['type']
        if '?' in t:
            t = t[:-1]
            o = True
        if '[]' in t:
            t = t[:-2]
            a = True
    return t, o, a


def insert_computationaltool_input_types(cwl):
    types = {}
    for name in cwl['inputs']:
        t, o, a = get_type(cwl['inputs'][name])
        if t:
            try:
                tt = ComputationalToolInputType.objects.get(type=t)
            except ObjectDoesNotExist:
                tt = ComputationalToolInputType.objects.create(type=t)
            types[tt.type] = tt.id
    return types


def insert_computationaltool_inputs(comptool):
    cwl = yaml.load(urlopen(comptool.cwl))
    types = insert_computationaltool_input_types(cwl)
    objects = []
    for name in cwl['inputs']:
        option = ''
        if 'inputBinding' in cwl['inputs'][name] and 'prefix' in \
                cwl['inputs'][name]['inputBinding']:
            option = cwl['inputs'][name]['inputBinding']['prefix']
        d = ''
        if 'doc' in cwl['inputs'][name]:
            d = cwl['inputs'][name]['doc'].replace('\n', ' ').strip()
        t, o, a = get_type(cwl['inputs'][name])
        if t in types:
            t = types[t]
        else:
            tt = ComputationalToolInputType.objects.create(type=t)
            types[tt.type] = tt.id
            t = tt.id
        objects.append(
            ComputationalToolInput(
                name=name,
                option=option,
                array=a,
                optional=o,
                doc=d,
                computationaltool=comptool,
                computationaltoolinputtype_id=t
            )
        )
    ComputationalToolInput.objects.bulk_create(objects)


def insert_computationaltool(gl_factory):
    for t in gl_factory.tools.keys():
        tool_license = None if 's:license' not in gl_factory.tools[t]['cwl'] \
            else gl_factory.tools[t]['cwl']['s:license']
        tool_codeRepository = None if 's:codeRepository' not in gl_factory.tools[t]['cwl'] \
            else gl_factory.tools[t]['cwl']['s:codeRepository']
        tool_author = None
        tool_identifier = None
        tool_email = None
        if 's:author' in gl_factory.tools[t]['cwl']:
            tool_author = gl_factory.tools[t]['cwl']['s:author'][0]['s:name']
            tool_identifier = gl_factory.tools[t]['cwl']['s:author'][0]['s:identifier']
            tool_email = gl_factory.tools[t]['cwl']['s:author'][0]['s:email']
        comptool = create_computationaltool(name=t,
                                            description=gl_factory.tools[t]['cwl']['doc'],
                                            cwl=gl_factory.tools[t]['cwl_url'],
                                            author_name=tool_author,
                                            author_identifier=tool_identifier,
                                            author_email=tool_email,
                                            codeRepository=tool_codeRepository,
                                            license=tool_license)
        for i in gl_factory.tools[t]['imports']:
            version = None if 'version' not in gl_factory.tools[t]['imports'][i] \
                else gl_factory.tools[t]['imports'][i][
                'version']
            create_computationaltoolcwlimport(
                name=i,
                cwl=gl_factory.tools[t]['imports'][i]['cwl_url'],
                version=version,
                computationaltool=comptool)
        insert_computationaltool_inputs(comptool)


def insert_computationalwfsteps(gl_factory, t, compwf):
    missing_options = {}
    order = 0
    for s in gl_factory.workflows[t]['cwl']['steps']:
        cwl_tool = None
        if gl_factory.workflows[t]['cwl']['steps'][s]['run'].startswith('http'):
            cwl_tool = ComputationalTool.objects.filter(
                cwl=gl_factory.workflows[t]['cwl']['steps'][s]['run'])
        else:
            cwl_tool = os.path.basename(gl_factory.workflows[t]['cwl']['steps'][s]['run'])
            cwl_tool = ComputationalTool.objects.filter(cwl__endswith='/' + cwl_tool)
        order += 1
        if cwl_tool:
            cwl_tool = cwl_tool[0]
            d = '' if 'doc' not in gl_factory.workflows[t]['cwl']['steps'][s] else \
                gl_factory.workflows[t]['cwl']['steps'][s]['doc'].replace('\n', ' ').strip()
            step = ComputationalWFStep.objects.create(name=s,
                                                      order=order,
                                                      description=d,
                                                      computationaltool_id=cwl_tool.id,
                                                      computationalwf=compwf)
            for i in gl_factory.workflows[t]['cwl']['steps'][s]['in']:
                cwl_tool_input = ComputationalToolInput.objects.get(
                    name=i, computationaltool=cwl_tool)
                value = None
                if type(gl_factory.workflows[t]['cwl']['steps'][s]['in'][i]) == dict:
                    if 'default' in gl_factory.workflows[t]['cwl']['steps'][s]['in'][i]:
                        value = \
                            str(gl_factory.workflows[t]['cwl']['steps'][s]['in'][i]['default'])
                if value:
                    ComputationalWFStepInput.objects.create(
                        value=value,
                        computationalwfstep=step,
                        computationaltoolinput=cwl_tool_input)
        else:
            if t not in missing_options:
                missing_options[t] = []
            d = '' if 'doc' not in gl_factory.workflows[t]['cwl']['steps'][s] else \
                gl_factory.workflows[t]['cwl']['steps'][s]['doc'].replace('\n', ' ').strip()
            missing_options[t].append({
                'order': order,
                'step': s,
                'd': d,
                'cwl': gl_factory.workflows[t]['cwl']['steps'][s]['run']})
    return missing_options


def insert_computationalwf(gl_factory):
    missing_options = {}
    for t in gl_factory.workflows.keys():
        tool_license = None if 's:license' not in gl_factory.workflows[t]['cwl'] \
            else gl_factory.workflows[t]['cwl']['s:license']
        tool_author = None
        tool_identifier = None
        tool_email = None
        if 's:author' in gl_factory.workflows[t]['cwl']:
            tool_author = gl_factory.workflows[t]['cwl']['s:author'][0]['s:name']
            tool_identifier = gl_factory.workflows[t]['cwl']['s:author'][0]['s:identifier']
            tool_email = gl_factory.workflows[t]['cwl']['s:author'][0]['s:email']
        compwf = create_computationalWF(name=t,
                                        description=gl_factory.workflows[t]['cwl']['doc'],
                                        cwl=gl_factory.workflows[t]['cwl_url'],
                                        author_name=tool_author,
                                        author_identifier=tool_identifier,
                                        author_email=tool_email,
                                        license=tool_license)
        missing_options.update(insert_computationalwfsteps(gl_factory, t, compwf))
    for m in missing_options:
        compwf = ComputationalWF.objects.get(name=m)
        for i in missing_options[m]:
            compwf_as_step = None
            if i['cwl'].startswith('http'):
                compwf_as_step = ComputationalWF.objects.get(cwl=i['cwl'])
            else:
                compwf_as_step = ComputationalWF.objects.get(
                    cwl__endswith='/' + os.path.basename(i['cwl']))
            if compwf_as_step:
                ComputationalWFStep.objects.create(
                    name=i['step'],
                    order=i['order'],
                    description=i['d'],
                    computationalwfstep_id=compwf_as_step.id,
                    computationalwf=compwf)
