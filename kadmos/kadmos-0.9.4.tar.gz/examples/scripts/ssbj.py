# Imports
import os
import logging
import unittest

import numpy as np

import OpenLEGO_dev_scripts.test_cases.ssbj.kb as kb
from kadmos.graph import FundamentalProblemGraph, load

from openlego.core.problem import LEGOProblem
from openlego.utils.general_utils import clean_dir_filtered

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['unconverged-MDA-GS',     # 0
                    'unconverged-MDA-J',      # 1
                    'converged-MDA-GS',       # 2
                    'converged-MDA-J',        # 3
                    'unconverged-DOE-GS-CT',  # 4
                    'unconverged-DOE-J-CT',   # 5
                    'converged-DOE-GS-CT',    # 6
                    'converged-DOE-J-CT',     # 7
                    'converged-DOE-GS-LH',    # 8
                    'converged-DOE-GS-MC',    # 9
                    'MDF-GS',                 # 10
                    'MDF-J',                  # 11
                    'IDF',                    # 12
                    'CO',                     # 13
                    'BLISS-2000']             # 14


def get_loop_items(analyze_mdao_definitions):
    if isinstance(analyze_mdao_definitions, int):
        mdao_defs_loop = [mdao_definitions[analyze_mdao_definitions]]
    elif isinstance(analyze_mdao_definitions, list):
        mdao_defs_loop = [mdao_definitions[i] for i in analyze_mdao_definitions]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mdao_defs_loop = mdao_definitions
        else:
            raise ValueError(
                'String value {} is not allowed for analyze_mdao_definitions.'.format(analyze_mdao_definitions))
    else:
        raise IOError(
            'Invalid input {} provided of type {}.'.format(analyze_mdao_definitions, type(analyze_mdao_definitions)))
    return mdao_defs_loop


def get_sublist(list, idxs):
    return [list[i] for i in idxs]


def add_mathematical_functions(rcg):
    # Add the objective function
    R = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/R')]
    R_label = R[0].split('/')[-1]
    R_scaler = '/dataSchema/scaledData/R/scaler'
    R_scaler_label = 'R_scaler'
    f_R = '/dataSchema/scaledData/R/value'
    rcg.add_mathematical_function([[R[0], R_label], [R_scaler, R_scaler_label]],
                                  'F[R]',
                                  [[f_R, '-{}/{}'.format(R_label, R_scaler_label), 'Python']])

    # Add the constraint functions
    # Collect constraint inputs
    sigmas = [node for node in rcg.find_all_nodes(category='variable') if 'sigma' in node]
    sigmas.sort()
    theta = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Theta')]
    dpdx = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/dpdx')]
    ESF = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/ESF')]
    DT = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/DT')]
    Temp = [node for node in rcg.find_all_nodes(category='variable') if node.endswith('/Temp')]

    # Define inputs nodes and labels
    con_inputs = sigmas + theta + dpdx + ESF + DT + Temp
    input_labels = [con_input.split('/')[-1] for con_input in con_inputs]

    # Define and create scaling nodes
    con_scalers = ['/dataSchema/scaledData/{}/scaler'.format(name) for name in input_labels]
    con_scalers_labels = ['{}_scr'.format(input_label) for input_label in input_labels]

    # Define output nodes and labels
    con_values = ['/dataSchema/scaledData/{}/value'.format(name) for name in input_labels]

    # Define mapping of the constraint functions
    function_map = {'sigmas': [0, 1, 2, 3, 4], 'Theta': [5], 'dpdx': [6], 'prop': [7, 8, 9]}

    # Add constraint functions to graph
    for f, f_idxs in function_map.items():
        f_con_inputs = get_sublist(con_inputs, f_idxs)
        f_input_labels = get_sublist(input_labels, f_idxs)
        f_con_scalers = get_sublist(con_scalers, f_idxs)
        f_con_scalers_labels = get_sublist(con_scalers_labels, f_idxs)
        f_con_values = get_sublist(con_values, f_idxs)
        rcg.add_mathematical_function([[item[0], item[1]] for item in zip(f_con_inputs, f_input_labels)] +
                                      [[item[0], item[1]] for item in zip(f_con_scalers, f_con_scalers_labels)],
                                      'C[{}]'.format(f),
                                      [[item[0], '{}/{}'.format(item[1], item[2]), 'Python']
                                       for item in zip(f_con_values, f_input_labels, f_con_scalers_labels)])

    # Add consistency constraint for lift and total weight
    rcg.add_mathematical_function([('/dataSchema/aircraft/other/L', 'L'), ('/dataSchema/aircraft/weight/WT', 'WT'),
                                   ('/dataSchema/scaledData/LWT/scaler', 'scaler')],
                                  'C[LWTbalance]',
                                  [['/dataSchema/scaledData/LWT/value', '(L-WT)/scaler', 'Python']])
    return rcg


def run_kadmos(analyze_mdao_definitions):
    # Get the MDA cases
    if isinstance(analyze_mdao_definitions, int):
        if analyze_mdao_definitions < 10:
            mda_cases = [analyze_mdao_definitions]
        else:
            mda_cases = []
    elif isinstance(analyze_mdao_definitions, list):
        mda_cases = [idx for idx in analyze_mdao_definitions if idx <10]
    else:
        raise AssertionError('Value type {} not supported.'.format(type(analyze_mdao_definitions)))

    # Run the MDA cases
    if mda_cases:
        run_kadmos_mda(mda_cases)

    # Get the MDO cases
    if isinstance(analyze_mdao_definitions, int):
        if analyze_mdao_definitions >= 10:
            mdo_cases = [analyze_mdao_definitions]
        else:
            mdo_cases = []
    elif isinstance(analyze_mdao_definitions, list):
        mdo_cases = [idx for idx in analyze_mdao_definitions if idx >= 10]
    else:
        raise AssertionError('Value type {} not supported.'.format(type(analyze_mdao_definitions)))

    # Run the MDO cases
    if mdo_cases:
        run_kadmos_mdo(mdo_cases)


def run_kadmos_mda(analyze_mdao_definitions):
    global mdao_definitions

    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    # Settings for loading and saving
    kb_dir = 'kb'
    pdf_dir = 'output_files/(X)DSM'
    cmdows_dir = 'output_files/CMDOWS'

    logging.info('Loading repository connectivity graph...')

    rcg = load(os.path.join(kb_dir, '__cmdows__SSBJ.xml'),
               check_list=['consistent_root', 'invalid_leaf_elements', 'schemas'])
    rcg.graph['name'] = 'RCG - Tool database'
    rcg.graph['description'] = 'Repository connectivity graph of the super-sonic business jet test case.'

    rcg = add_mathematical_functions(rcg)
    rcg.remove_function_nodes('C[LWTbalance]')

    # Add default values of the variables based on a reference file
    rcg.add_variable_default_values(os.path.join(kb_dir, 'SSBJ-base.xml'))

    # Define the function order
    function_order = ['StructuralAnalysis', 'AeroAnalysis', 'PropulsionAnalysis', 'PerformanceAnalysis',
                      'C[sigmas]', 'C[Theta]', 'C[dpdx]', 'C[prop]', 'F[R]']

    # Create a CMDOWS, DSM and a VISTOMS visualization of the RCG
    rcg.create_dsm('RCG_mda', include_system_vars=True, destination_folder=pdf_dir, function_order=function_order)

    # Reset FPG
    mdao_definition_fpg = mdao_definitions[0]
    architecture_type = 'MDA'
    fpg = FundamentalProblemGraph(rcg)
    fpg.graph['name'] = 'FPG - {}'.format(architecture_type)
    fpg.graph['description'] = 'Fundamental problem graph to solve the super-sonic business jet test case optimization ' \
                               'problem for the architecture type: {}'.format(architecture_type)

    # Define settings of the problem formulation
    fpg.add_problem_formulation(mdao_definition_fpg, function_order)

    # Assign objective
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/R/value')])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if 'scaledData/sigma' in nd and '/value' in nd])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/Theta/value')])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/dpdx/value')])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/ESF/value')])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/DT/value')])
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('scaledData/Temp/value')])

    # Add WE as QOI for testing with RCE
    fpg.mark_as_qois([nd for nd in rcg.find_all_nodes(category='variable') if '/aircraft/weight/WE' in nd])

    # Search for problem roles
    fpg.add_function_problem_roles()

    for mdao_definition in mdao_defs_loop:
        logging.info('Scripting {}...'.format(mdao_definition))

        # If DOE, assign design variables
        if 'DOE' in mdao_definition:
            des_vars = [('/dataSchema/aircraft/geometry/tc', 0.01, 0.05, 0.09),
                        ('/dataSchema/reference/h', 30000., 45000., 60000.),
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
                                         samples=[list(np.linspace(ds_vr[1], ds_vr[3], n_samples)) for ds_vr in
                                                  des_vars] if '-CT' in mdao_definition else None)

        # Change the problem formulation of the FPG based on the MDAO definition
        if 'DOE' in mdao_definition:
            doe_settings = dict()
            if mdao_definition.endswith('-CT'):
                doe_settings['method'] = 'Custom design table'
            elif mdao_definition.endswith('-FF'):
                doe_settings['method'] = 'Full factorial design'
                doe_settings['levels'] = 2
            elif mdao_definition.endswith('-LH'):
                doe_settings['method'] = 'Latin hypercube design'
                doe_settings['seed'] = 5
                doe_settings['runs'] = 10
            elif mdao_definition.endswith('-MC'):
                doe_settings['method'] = 'Monte Carlo design'
                doe_settings['seed'] = 9
                doe_settings['runs'] = 10
            elif mdao_definition.endswith('-BB'):
                doe_settings['method'] = 'Box-Behnken design'
                doe_settings['center_runs'] = 2
            else:
                raise AssertionError('Could not determine the doe_method.')
        else:
            doe_settings = None

        fpg.add_problem_formulation(mdao_definition, function_order,
                                    doe_settings=doe_settings)

        # Get Mdao graphs
        mdg, mpg = fpg.impose_mdao_architecture()
        mdg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mdg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)
        mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mpg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)

        # Create a DSM visualization of the Mdao
        mdg.create_dsm(file_name='Mdao_{}'.format(mdao_definition), include_system_vars=True,
                       destination_folder=pdf_dir,
                       mpg=mpg)

        # Save the Mdao as cmdows (and do an integrity check)
        mdg.save('Mdao_{}'.format(mdao_definition), file_type='cmdows', destination_folder=cmdows_dir,
                 mpg=mpg,
                 description='Mdao CMDOWS file of the super-sonic business jet test case optimization problem',
                 creator='Imco van Gent',
                 version='0.1',
                 pretty_print=True,
                 integrity=True)
        logging.info('Done!')


def run_kadmos_mdo(analyze_mdao_definitions):

    global mdao_definitions

    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    # Settings for loading and saving
    kb_dir = 'kb'
    pdf_dir = 'output_files/(X)DSM'
    cmdows_dir = 'output_files/CMDOWS'

    logging.info('Loading repository connectivity graph...')

    rcg = load(os.path.join(kb_dir, '__cmdows__SSBJ.xml'),
               check_list=['consistent_root', 'invalid_leaf_elements', 'schemas'])

    logging.info('Scripting RCG...')

    # A name and a description are added to the graph
    rcg.graph['name'] = 'RCG'
    rcg.graph['description'] = 'Repository of the super-sonic business jet test case optimization problem'

    rcg = add_mathematical_functions(rcg)

    # Define function order
    function_order = ['StructuralAnalysis', 'AeroAnalysis', 'PropulsionAnalysis', 'PerformanceAnalysis',
                      'C[sigmas]', 'C[Theta]', 'C[dpdx]', 'C[prop]', 'C[LWTbalance]', 'F[R]']

    # Create a DSM and a VISTOMS visualization of the RCG
    rcg.create_dsm('RCG_mdo', include_system_vars=True, destination_folder=pdf_dir, function_order=function_order)

    # Reset FPG
    mdao_definition_fpg = 'MDF-GS'
    architecture_type = 'MDO'
    fpg = FundamentalProblemGraph(rcg)
    fpg.graph['name'] = 'FPG - {}'.format(architecture_type)
    fpg.graph['description'] = 'Fundamental problem graph to solve the super-sonic business jet test case optimization ' \
                               'problem for the architecture type: {}'.format(architecture_type)

    # Define settings of the problem formulation
    fpg.add_problem_formulation(mdao_definition_fpg, function_order)

    # Assign design variables
    des_vars = [('/dataSchema/aircraft/geometry/tc', 0.01, 0.05, 0.09),
                ('/dataSchema/reference/h', 30000., 45000., 60000.),
                ('/dataSchema/reference/M', 1.4, 1.6, 1.8),
                ('/dataSchema/aircraft/geometry/AR', 2.475, 5.5, 7.975),
                ('/dataSchema/aircraft/geometry/Lambda', 39.6, 55., 69.85),
                ('/dataSchema/aircraft/geometry/Sref', 500., 1000., 1500.),
                ('/dataSchema/aircraft/geometry/lambda', 0.1, 0.25, 0.4),
                ('/dataSchema/aircraft/geometry/section', 0.75, 1.00, 1.25),
                ('/dataSchema/aircraft/other/Cf', 0.75, 1.00, 1.25),
                ('/dataSchema/aircraft/other/T', 0.09, 0.2, 0.905)]
    fpg.mark_as_design_variables([ds_vr[0] for ds_vr in des_vars],
                                 lower_bounds=[ds_vr[1] for ds_vr in des_vars],
                                 nominal_values=[ds_vr[2] for ds_vr in des_vars],
                                 upper_bounds=[ds_vr[3] for ds_vr in des_vars])

    # Assign objective
    fpg.mark_as_objective([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('/R/value')][0])

    # Assign constraints
    fpg.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             ('/sigma' in nd and '/value' in nd)], '<=', 1.09)
    fpg.mark_as_constraint([nd for nd in rcg.find_all_nodes(category='variable') if
                            nd.endswith('/Theta/value')][0], ['>=', '<='], [0.96, 1.04])
    fpg.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/dpdx/value')], '<=', 1.04)
    fpg.mark_as_constraint([nd for nd in rcg.find_all_nodes(category='variable') if
                           nd.endswith('/ESF/value')][0], ['>=', '<='], [0.5, 1.5])
    fpg.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/DT/value')], '<=', 0.0)
    fpg.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/Temp/value')], '<=', 1.02)
    fpg.mark_as_constraints([nd for nd in rcg.find_all_nodes(category='variable') if
                             nd.endswith('/LWT/value')], '==', 0.00)

    # Search for problem roles
    fpg.add_function_problem_roles()

    for mdao_definition in mdao_defs_loop:
        logging.info('Scripting {}...'.format(mdao_definition))

        # Add valid ranges for couplings that will become design variables
        if mdao_definition in ['IDF', 'CO']:
            root = 'dataSchema'
            geom = '/'.join(['', root, 'aircraft', 'geometry'])
            weig = '/'.join(['', root, 'aircraft', 'weight'])
            other = '/'.join(['', root, 'aircraft', 'other'])
            ref = '/'.join(['', root, 'reference'])
            special_variables = [('/'.join([other, 'D']), 1000., 15000.),
                                 ('/'.join([other, 'L']), 20000., 80000.),
                                 ('/'.join([geom, 'Theta']), 0.96, 1.04),
                                 ('/'.join([weig, 'WE']), 0., 20000.),
                                 ('/'.join([weig, 'WT']), 20000., 80000.),
                                 ('/'.join([ref, 'ESF']), 0.5, 1.5)]
            if mdao_definition == 'CO':
                special_variables.append(('/'.join([weig, 'WF']), 5000., 25000.))
                special_variables.append(('/'.join([other, 'fin']), 2., 12.))
                special_variables.append(('/'.join([other, 'SFC']), .5, 1.5))
            for sv in special_variables:
                fpg.nodes[sv[0]]['valid_ranges'] = {'limit_range': {'minimum': sv[1], 'maximum': sv[2]}}

        if mdao_definition != 'CO':
            fpg.remove_function_nodes('C[LWTbalance]')
        else:
            fpg.remove_function_nodes('C[Theta]')
            fpg.remove_node([nd for nd in rcg.find_all_nodes(category='variable') if nd.endswith('/ESF/value')][0])

        # Update problem roles
        fpg.add_function_problem_roles()


        # Change the problem formulation of the FPG based on the MDAO definition
        if mdao_definition in ['CO', 'BLISS-2000']:
            fpg.graph['problem_formulation']['coupled_functions_groups'] = [['StructuralAnalysis'], ['AeroAnalysis'],
                                                                            ['PropulsionAnalysis']]
        fpg.add_problem_formulation(mdao_definition, function_order,
                                    doe_settings=None if mdao_definition is not 'BLISS-2000' else
                                    {'method': 'Latin hypercube design', 'seed': 5, 'runs': 50})

        # Get Mdao graphs
        mdg, mpg = fpg.impose_mdao_architecture()
        mdg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mdg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)
        mpg.graph['name'] = 'XDSM - {}'.format(mdao_definition)
        mpg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization ' \
                                   'problem using the strategy: {}.'.format(mdao_definition)
        logging.info('Scripting {}...'.format(mdao_definition))

        # Create a DSM visualization of the Mdao
        mdg.create_dsm(file_name='Mdao_{}'.format(mdao_definition), include_system_vars=True, destination_folder=pdf_dir,
                       mpg=mpg)

        # Save the Mdao as cmdows (and do an integrity check)
        # TODO: Add integrity check and update writer+schema for distributed architectures
        mdg.save('Mdao_{}'.format(mdao_definition), file_type='cmdows', destination_folder=cmdows_dir,
                 mpg=mpg,
                 description='Mdao CMDOWS file of the super-sonic business jet test case optimization problem',
                 creator='Imco van Gent',
                 version='0.1',
                 pretty_print=True,
                 integrity=True)
    logging.info('Done!')


def run_openlego(analyze_mdao_definitions):
    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    for mdao_def in mdao_defs_loop:
        print('\n-----------------------------------------------')
        print('Running the OpenLEGO of Mdao_{}.xml...'.format(mdao_def))
        print('------------------------------------------------')
        """Solve the SSBJ problem using the given CMDOWS file."""

        # 1. Create Problem
        prob = LEGOProblem(cmdows_path=os.path.join('output_files', 'CMDOWS', 'Mdao_{}.xml'.format(mdao_def)),  # CMDOWS file
                           kb_path='kb',  # Knowledge base path
                           data_folder=os.path.join('output_files', 'OpenLEGO'),  # Output directory
                           base_xml_file='ssbj-output-{}.xml'.format(mdao_def))  # Output file
        #prob.driver.options['debug_print'] = ['desvars', 'nl_cons', 'ln_cons', 'objs']  # Set printing of debug info
        prob.set_solver_print(1)  # Set printing of solver information

        # 2. Initialize the Problem and export N2 chart
        prob.store_model_view(open_in_browser=False)
        prob.initialize_from_xml('SSBJ-base.xml')  # Set the initial values from an XML file

        # 3. Run the Problem
        if mdao_def == 'CO':
            prob.run_model()
        else:
            prob.run_driver()  # Run the driver (optimization, DOE, or convergence)

        # 4. Read out the case reader
        if mdao_def != 'CO':
            prob.collect_results()

        # 5. Collect test results for test assertions
        tc = prob['/dataSchema/aircraft/geometry/tc']
        h = prob['/dataSchema/reference/h']
        M = prob['/dataSchema/reference/M']
        AR = prob['/dataSchema/aircraft/geometry/AR']
        Lambda = prob['/dataSchema/aircraft/geometry/Lambda']
        Sref = prob['/dataSchema/aircraft/geometry/Sref']
        if mdao_def != 'CO':
            lambda_ = prob['/dataSchema/aircraft/geometry/lambda']
            section = prob['/dataSchema/aircraft/geometry/section']
            Cf = prob['/dataSchema/aircraft/other/Cf']
            T = prob['/dataSchema/aircraft/other/T']
            R = prob['/dataSchema/scaledData/R/value']
            extra = prob['/dataSchema/aircraft/weight/WT']
        else:
            lambda_ = prob.model.SubOptimizer0.prob['/dataSchema/aircraft/geometry/lambda']
            section = prob.model.SubOptimizer0.prob['/dataSchema/aircraft/geometry/section']
            Cf = prob.model.SubOptimizer1.prob['/dataSchema/aircraft/other/Cf']
            T = prob.model.SubOptimizer2.prob['/dataSchema/aircraft/other/T']
            R = prob['/dataSchema/scaledData/R/value']
            extra = (prob['/dataSchema/distributedArchitectures/group0/objective'],
                     prob['/dataSchema/distributedArchitectures/group1/objective'],
                     prob['/dataSchema/distributedArchitectures/group2/objective'])

        # 6. Cleanup and invalidate the Problem afterwards
        prob.invalidate()

    return tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra

#
# class TestSsbj(unittest.TestCase):
#
#     def __call__(self, *args, **kwargs):
#         kb.deploy()
#         super(TestSsbj, self).__call__(*args, **kwargs)
#
#     def assertion_mda(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .05, 2)
#         self.assertAlmostEqual(h, 45000., 2)
#         self.assertAlmostEqual(M, 1.6, 2)
#         self.assertAlmostEqual(AR, 5.5, 2)
#         self.assertAlmostEqual(Lambda, 55., 2)
#         self.assertAlmostEqual(Sref, 1000., 2)
#         self.assertAlmostEqual(lambda_, .25, 2)
#         self.assertAlmostEqual(section, 1., 2)
#         self.assertAlmostEqual(Cf, 1., 2)
#         self.assertAlmostEqual(T, .2, 2)
#         self.assertAlmostEqual(R, -.7855926, 2)
#         self.assertAlmostEqual(extra, 63609.5740869, 2)
#
#     def assertion_unc_doe_gs(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .09, 2)
#         self.assertAlmostEqual(h, 60000., 2)
#         self.assertAlmostEqual(M, 1.8, 2)
#         self.assertAlmostEqual(AR, 8.5, 2)
#         self.assertAlmostEqual(Lambda, 70., 2)
#         self.assertAlmostEqual(Sref, 1500., 2)
#         self.assertAlmostEqual(lambda_, .4, 2)
#         self.assertAlmostEqual(section, 1.25, 2)
#         self.assertAlmostEqual(Cf, 1.25, 2)
#         self.assertAlmostEqual(T, 1., 2)
#         self.assertAlmostEqual(R, -1.15528254, 2)
#         self.assertAlmostEqual(extra, 149272.433123, 2)
#
#     def assertion_unc_doe_j(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .09, 2)
#         self.assertAlmostEqual(h, 60000., 2)
#         self.assertAlmostEqual(M, 1.8, 2)
#         self.assertAlmostEqual(AR, 8.5, 2)
#         self.assertAlmostEqual(Lambda, 70., 2)
#         self.assertAlmostEqual(Sref, 1500., 2)
#         self.assertAlmostEqual(lambda_, .4, 2)
#         self.assertAlmostEqual(section, 1.25, 2)
#         self.assertAlmostEqual(Cf, 1.25, 2)
#         self.assertAlmostEqual(T, 1., 2)
#         self.assertAlmostEqual(R, -0.82379969, 2)
#         self.assertAlmostEqual(extra, 148199.575895, 2)
#
#     def assertion_con_doe(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .09, 2)
#         self.assertAlmostEqual(h, 60000., 2)
#         self.assertAlmostEqual(M, 1.8, 2)
#         self.assertAlmostEqual(AR, 8.5, 2)
#         self.assertAlmostEqual(Lambda, 70., 2)
#         self.assertAlmostEqual(Sref, 1500., 2)
#         self.assertAlmostEqual(lambda_, .4, 2)
#         self.assertAlmostEqual(section, 1.25, 2)
#         self.assertAlmostEqual(Cf, 1.25, 2)
#         self.assertAlmostEqual(T, 1., 2)
#         self.assertAlmostEqual(R, -1.13518441, 2)
#         self.assertAlmostEqual(extra, 187900.003656, 2)
#
#     def assertion_mdo(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .06, 2)
#         self.assertAlmostEqual(h, 60000., 2)
#         self.assertAlmostEqual(M, 1.4, 2)
#         self.assertAlmostEqual(AR, 2.475, 2)
#         self.assertAlmostEqual(Lambda, 69.85, 2)
#         self.assertAlmostEqual(Sref, 1500., 2)
#         self.assertAlmostEqual(lambda_, .4, 2)
#         self.assertAlmostEqual(section, .75, 2)
#         self.assertAlmostEqual(Cf, .75, 2)
#         self.assertAlmostEqual(T, .15620845, 2)
#         self.assertAlmostEqual(R, -7.40624897, 2)
#         self.assertAlmostEqual(extra, 44957.7059791, 2)
#
#     def assertion_co(self, tc, h, M, AR, Lambda, Sref, lambda_, section, Cf, T, R, extra):
#         self.assertAlmostEqual(tc, .05, 2)
#         self.assertAlmostEqual(h, 45000., 2)
#         self.assertAlmostEqual(M, 1.6, 2)
#         self.assertAlmostEqual(AR, 5.5, 2)
#         self.assertAlmostEqual(Lambda, 55., 2)
#         self.assertAlmostEqual(Sref, 1000., 2)
#         self.assertAlmostEqual(lambda_, .25, 2)
#         self.assertAlmostEqual(section, 1., 2)
#         self.assertAlmostEqual(Cf, 1., 2)
#         self.assertAlmostEqual(T, .2, 2)
#         self.assertAlmostEqual(R, -.7855926, 2)
#         for J in extra:
#             self.assertAlmostEqual(J, 0., delta=0.1)
#
#     def test_unc_mda_gs(self):
#         """Test run the SSBJ tools in sequence."""
#         self.assertion_mda(*run_openlego(0))
#
#     def test_unc_mda_j(self):
#         """Test run the SSBJ tools in parallel."""
#         self.assertion_mda(*run_openlego(1))
#
#     def test_con_mda_gs(self):
#         """Solve the SSBJ system using the Gauss-Seidel convergence scheme."""
#         self.assertion_mda(*run_openlego(2))
#
#     def test_con_mda_j(self):
#         """Solve the SSBJ system using the Jacobi convergence scheme."""
#         self.assertion_mda(*run_openlego(3))
#
#     def test_unc_doe_gs_ct(self):
#         """Solve multiple (DOE) SSBJ systems (unconverged) in sequence based on a custom design table."""
#         self.assertion_unc_doe_gs(*run_openlego(4))
#
#     def test_unc_doe_j_ct(self):
#         """Solve multiple (DOE) SSBJ systems (unconverged) in parallel based on a custom design table."""
#         self.assertion_unc_doe_j(*run_openlego(5))
#
#     def test_con_doe_gs_ct(self):
#         """Solve multiple (DOE) SSBJ systems (converged) in sequence based on a custom design table."""
#         self.assertion_con_doe(*run_openlego(6))
#
#     def test_con_doe_j_ct(self):
#         """Solve multiple (DOE) SSBJ systems (converged) in parallel based on a custom design table."""
#         self.assertion_con_doe(*run_openlego(7))
#
#     def test_con_doe_gs_lh(self):
#         """Solve multiple (DOE) SSBJ systems (converged) in sequence based on a latin hypercube sampling."""
#         run_openlego(8)
#
#     def test_con_doe_gs_mc(self):
#         """Solve multiple (DOE) SSBJ systems (converged) in sequence based on a Monte Carlo sampling."""
#         run_openlego(9)
#
#     def test_mdf_gs(self):
#         """Solve the SSBJ problem using the MDF architecture and a Gauss-Seidel convergence scheme."""
#         self.assertion_mdo(*run_openlego(10))
#
#     def test_mdf_j(self):
#         """Solve the SSBJ problem using the MDF architecture and a Jacobi converger."""
#         self.assertion_mdo(*run_openlego(11))
#
#     def test_idf(self):
#         """Solve the SSBJ problem using the IDF architecture."""
#         self.assertion_mdo(*run_openlego(12))
#
#     def test_co(self):
#         """Test run the SSBJ problem using the CO architecture."""
#         self.assertion_co(*run_openlego(13))
#
#     def __del__(self):
#         kb.clean()
#         clean_dir_filtered(os.path.dirname(__file__), ['case_reader_', 'n2_Mdao_', 'ssbj-output-', 'SLSQP.out'])
#

if __name__ == '__main__':
    """ 0: unconverged-MDA-GS
        1: unconverged-MDA-J
        2: converged-MDA-GS
        3: converged-MDA-J
        4: unconverged-DOE-GS-CT
        5: unconverged-DOE-J-CT
        6: converged-DOE-GS-CT
        7: converged-DOE-J-CT
        8: converged-DOE-GS-LH
        9: converged-DOE-GS-MC
        10: MDF-GS
        11: MDF-J
        12: IDF
        13: CO
        14: BLISS-2000
    """
    # Set options
    analyze_mdao_definitions = 13  # list of integers or single integer

    # First run KADMOS to provide the CMDOWS file(s)
    run_kadmos(analyze_mdao_definitions)

    # Then run OpenLEGO to create the model and run the analysis
    run_openlego(analyze_mdao_definitions)
