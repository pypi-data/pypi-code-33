import os
from shutil import copyfile

from kadmos.utilities.xml_utils_openlego import xml_merge

dir_path = os.path.dirname(os.path.realpath(__file__))


def add_discipline_to_cmdows(Discipline, dir_path):
    from kadmos.cmdows import CMDOWS
    # Database files
    files = os.listdir(dir_path)
    cmdows_files = [file for file in files if '__cmdows__' in file]
    assert len(cmdows_files) <= 1, 'Multiple CMDOWS files were found {}.'.format(cmdows_files)
    if cmdows_files:
        cmdows = CMDOWS(cmdows_files[0])
    else:
        cmdows_files = ['__cmdows__SSBJ.xml']
        cmdows = CMDOWS()
        cmdows.add_header(Discipline.operator, 'CMDOWS file of the SSBJ database.')
    cmdows.add_dc(Discipline.name, Discipline.name, 'main', 1, Discipline.version, Discipline.name)
    cmdows.save(cmdows_files[0], pretty_print=True)


def list_disciplines():
    from ssbjkadmos.tools.structures.Structures import Structures
    from ssbjkadmos.tools.aerodynamics.Aerodynamics import Aerodynamics
    from ssbjkadmos.tools.propulsion.Propulsion import Propulsion
    from ssbjkadmos.tools.performance.Performance import Performance
    from ssbjkadmos.tools.outputfunctions.Objective import Objective
    from ssbjkadmos.tools.outputfunctions.Constraints import Constraints
    from ssbjkadmos.tools.dpdxcalc.DpdxCalc import DpdxCalc
    return [Structures(), Aerodynamics(), Propulsion(), Performance(), Objective(), Constraints(), DpdxCalc()]


def try_to_remove(file):
    try:
        os.remove(file)
    except:
        pass


def clean(dir_path):
    for discipline in list_disciplines():
        try_to_remove('{}{}'.format(discipline.name, '-input.xml'))
        try_to_remove('{}{}'.format(discipline.name, '-output.xml'))
        try_to_remove('{}{}'.format(discipline.name, '-partials.xml'))
    base_file_path = os.path.join(dir_path, 'SSBJ-base.xml')
    try_to_remove(base_file_path)

    for file in os.listdir(dir_path):
        if '__test__' in file:
            try_to_remove(file)
        if '__run__' in file and '_output.xml' in file:
            try_to_remove(file)
        if '__cmdows__' in file:
            try_to_remove(file)


def deploy(dir_path):
    _copy = True
    for discipline in list_disciplines():
        discipline.deploy()
        base_file_path = os.path.join(dir_path, 'SSBJ-base.xml')
        if _copy:
            _copy = False
            copyfile(discipline.in_file, base_file_path)
        else:
            xml_merge(base_file_path, discipline.in_file)

        xml_merge(base_file_path, discipline.out_file)

        for file_path in [discipline.in_file, discipline.out_file, discipline.partials_file]:
            file_destination = os.path.join(dir_path, os.path.basename(file_path))
            if os.path.exists(file_destination):
                os.remove(file_destination)
            os.rename(file_path, file_destination)
