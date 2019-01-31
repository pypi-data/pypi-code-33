# Imports
import os
import logging

import numpy as np

from kadmos.graph import FundamentalProblemGraph, load

# Settings for logging
from kadmos.graph.mixin_vistoms import vistoms_start

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDA definitions that can be wrapped around the problem
mdao_definitions = ['unconverged-MDA-GS',     # 0
                    'unconverged-MDA-J',      # 1
                    'converged-MDA-GS',       # 2
                    'converged-MDA-J',        # 3
                    'unconverged-DOE-GS-CT',  # 4
                    'unconverged-DOE-J-CT',   # 5
                    'converged-DOE-GS-CT',    # 6
                    'converged-DOE-J-CT',     # 7
                    'converged-DOE-GS-FF',    # 8
                    'converged-DOE-GS-LH',    # 9
                    'converged-DOE-GS-MC']    # 10
all_graphs = []

# Settings for scripting
mdao_definitions_loop_all = True   # Option for looping through all MDAO definitions
mdao_definition_id = 6             # Option for selecting a MDAO definition (in case mdao_definitions_loop_all=False)
start_interactive_vistoms = False  # Option to start an interactive VISTOMS at the end

# Settings for loading and saving
kb_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases')
pdf_dir = 'ssbj/(X)DSM'
cmdows_dir = 'ssbj/CMDOWS'
kdms_dir = 'ssbj/KDMS'
vistoms_dir = 'ssbj/VISTOMS_mda'

logging.info('Loading repository connectivity graph...')

rcg = load(os.path.join(kb_dir, 'ssbj', '__cmdows__SSBJ.xml'),
           check_list=['consistent_root', 'invalid_leaf_elements', 'schemas'])
rcg.graph['name'] = 'RCG - Tool database'
rcg.graph['description'] = 'Repository connectivity graph of the super-sonic business jet test case.'

# Add the constraint functions
# Sigmas
sigmas = [node for node in rcg.find_all_nodes(category='variable') if 'sigma' in node]
sigmas.sort()
sigma_labels = [sigma.split('/')[-1] for sigma in sigmas]
c_sigma_prefix = '/dataSchema/mdo_data/constraints/sigmas'
c_sigmas = ['{}/sigma{}'.format(c_sigma_prefix, idx+1) for (idx, _) in enumerate(sigmas)]
rcg.add_mathematical_function([[item[0], item[1]] for item in zip(sigmas, sigma_labels)],
                              'C[sigmas]',
                              [[item[0], '{}/1.0'.format(item[1]), 'Python'] for item in zip(c_sigmas, sigma_labels)])

# Theta
theta = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Theta')]
theta_label = theta[0].split('/')[-1]
c_theta = '/dataSchema/mdo_data/constraints/Theta'
rcg.add_mathematical_function([[theta[0], theta_label]],
                              'C[Theta]',
                              [[c_theta, '{}/1.0'.format(theta_label), 'Python']])

# dpdx
dpdx = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/dpdx')]
dpdx_label = dpdx[0].split('/')[-1]
c_dpdx = '/dataSchema/mdo_data/constraints/dpdx'
rcg.add_mathematical_function([[dpdx[0], dpdx_label]],
                              'C[dpdx]',
                              [[c_dpdx, '{}/1.0'.format(dpdx_label), 'Python']])

# prop
ESF = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/ESF')]
DT = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/DT')]
Temp = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Temp')]
prop_nodes = ESF + DT + Temp
prop_labels = [prop.split('/')[-1] for prop in prop_nodes]
c_prop_prefix = '/dataSchema/mdo_data/constraints/propulsion'
c_props = ['{}/{}'.format(c_prop_prefix, prop_label) for prop_label in prop_labels]
rcg.add_mathematical_function([[item[0], item[1]] for item in zip(prop_nodes, prop_labels)],
                              'C[prop]',
                              [[item[0], '{}/1.0'.format(item[1]), 'Python'] for item in zip(c_props, prop_labels)])

# Add the objective
R = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/R')]
R_label = R[0].split('/')[-1]
f_R = '/dataSchema/mdo_data/objectives/R'
rcg.add_mathematical_function([[R[0], R_label]], 'F[R]', [[f_R, '-{}'.format(R_label), 'Python']])

# Add default values of the variables based on a reference file
rcg.add_variable_default_values(os.path.join(kb_dir, 'ssbj', 'SSBJ-base.xml'))

# Define the function order
function_order = ['Structures', 'Aerodynamics', 'Propulsion', 'Performance',
                  'C[sigmas]', 'C[Theta]', 'C[dpdx]', 'C[prop]', 'F[R]']

# Create a CMDOWS, DSM and a VISTOMS visualization of the RCG
rcg.create_dsm('RCG_extended', include_system_vars=True, destination_folder=pdf_dir, function_order=function_order)
rcg.vistoms_create(vistoms_dir, function_order=function_order)

# Save CMDOWS and KDMS file
rcg.save('RCG', destination_folder=kdms_dir)
rcg.save('RCG',
         file_type='cmdows',
         description='RCG CMDOWS file of the super-sonic business jet test case optimization problem',
         creator='Lukas Mueller',
         version='0.1',
         destination_folder=cmdows_dir,
         pretty_print=True,
         integrity=True)
all_graphs.append(rcg)

# On to the wrapping of the MDAO architectures
# Get iterator (all or single one)
if not mdao_definitions_loop_all:
    mdao_definitions = [mdao_definitions[mdao_definition_id]]

# Reset FPG
mdao_definition_fpg = mdao_definitions[0]
architecture_type = 'MDA'
fpg = FundamentalProblemGraph(rcg)
fpg.graph['name'] = 'FPG - {}'.format(architecture_type)
fpg.graph['description'] = 'Fundamental problem graph to solve the super-sonic business jet test case optimization ' \
                           'problem for the architecture type: {}'.format(architecture_type)

# Define settings of the problem formulation
fpg.add_problem_formulation(mdao_definition_fpg, function_order)
#fpg.graph['problem_formulation']['coupled_functions_groups'] = [['Structures'], ['Aerodynamics'], ['Propulsion']]

# Assign objective
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('objectives/R')])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/sigmas' in nd])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/Theta' in nd])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/dpdx' in nd])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/propulsion/ESF' in nd])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/propulsion/DT' in nd])
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'mdo_data/constraints/propulsion/Temp' in nd])

# Add WE as QOI for testing with RCE
fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if '/aircraft/weight/WE' in nd])

# Search for problem roles
fpg.add_function_problem_roles()
saved_fpg_vistoms = False

for mdao_definition in mdao_definitions:
    logging.info('Scripting {}...'.format(mdao_definition))

    # If DOE, assign design variables
    if 'DOE' in mdao_definition:
        des_vars = [('/dataSchema/aircraft/geometry/tc', 0.01, 0.05, 0.09),
                    ('/dataSchema/reference/h', 30000, 45000, 60000),
                    ('/dataSchema/reference/M', 1.4, 1.6, 1.8),
                    ('/dataSchema/aircraft/geometry/AR', 2.5, 5.5, 8.5),
                    ('/dataSchema/aircraft/geometry/Lambda', 40, 55, 70),
                    ('/dataSchema/aircraft/geometry/Sref', 500, 1000, 1500),
                    ('/dataSchema/aircraft/geometry/lambda', 0.1, 0.25, 0.4),
                    ('/dataSchema/aircraft/geometry/section', 0.75, 1.00, 1.25),
                    ('/dataSchema/aircraft/other/Cf', 0.75, 1.00, 1.25),
                    ('/dataSchema/aircraft/other/T', 0.1, 0.55, 1.00)]
        n_samples = 10
        fpg.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars],
                                     lower_bounds=[ds_vr[1] for ds_vr in des_vars],
                                     nominal_values=[ds_vr[2] for ds_vr in des_vars],
                                     upper_bounds=[ds_vr[3] for ds_vr in des_vars],
                                     samples=[list(np.linspace(ds_vr[1], ds_vr[2], n_samples)) for ds_vr in
                                              des_vars] if '-CT' in mdao_definition else None)

    # Change the problem formulation of the FPG based on the MDAO definition
    if 'DOE' in mdao_definition:
        doe_settings = dict()
        # TODO: Check and update DOE settings!
        if mdao_definition.endswith('-CT'):
            doe_settings['method'] = 'Custom design table'
        elif mdao_definition.endswith('-FF'):
            doe_settings['method'] = 'Full factorial design'
            doe_settings['levels'] = 2
        elif mdao_definition.endswith('-LH'):
            doe_settings['method'] = 'Latin hypercube design'
            doe_settings['seed'] = 5
            doe_settings['runs'] = 20
        elif mdao_definition.endswith('-MC'):
            doe_settings['method'] = 'Monte Carlo design'
            doe_settings['seed'] = 9
            doe_settings['runs'] = 10
        else:
            raise AssertionError('Could not determine the doe_method.')
    else:
        doe_settings = None

    fpg.add_problem_formulation(mdao_definition, function_order,
                                doe_settings=doe_settings)

    # Create a DSM visualization of the FPG
    fpg.create_dsm(file_name='FPG_{}'.format(architecture_type), function_order=function_order,
                   include_system_vars=True, destination_folder=pdf_dir)
    # Create a VISTOMS visualization of the FPG (and add it to the existing directory)
    if not saved_fpg_vistoms:
        fpg.vistoms_add(vistoms_dir, function_order=function_order)
        saved_fpg_vistoms = True

    # Save the FPG as kdms
    fpg.save('FPG_{}'.format(architecture_type), destination_folder=kdms_dir)
    # Save the FPG as cmdows (and do an integrity check)
    fpg.save('FPG_{}'.format(architecture_type), file_type='cmdows', destination_folder=cmdows_dir,
             description='FPG CMDOWS file of the super-sonic business jet test case optimization problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True)
    all_graphs.append(fpg)

    # Get Mdao graphs
    mdg, mpg = fpg.impose_mdao_architecture()
    mdg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
    mdg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                               'problem using the strategy: {}.'.format(mdao_definition)
    mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
    mpg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                               'problem using the strategy: {}.'.format(mdao_definition)

    # Create a DSM visualization of the Mdao
    mdg.create_dsm(file_name='Mdao_{}'.format(mdao_definition), include_system_vars=True, destination_folder=pdf_dir,
                   mpg=mpg)
    # Create a VISTOMS visualization of the Mdao (and add it to the existing directory)
    mdg.vistoms_add(vistoms_dir, mpg=mpg)

    # Save the Mdao as kdms
    mdg.save('Mdao_{}'.format(mdao_definition), destination_folder=kdms_dir, mpg=mpg)
    # Save the Mdao as cmdows (and do an integrity check)
    mdg.save('Mdao_{}'.format(mdao_definition), file_type='cmdows', destination_folder=cmdows_dir,
             mpg=mpg,
             description='Mdao CMDOWS file of the super-sonic business jet test case optimization problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True)
    all_graphs.append((mdg, mpg))

logging.info('Done!')

if start_interactive_vistoms:
    vistoms_start(all_graphs, file_dir='ssbj/VISTOMS_mda_interactive')
