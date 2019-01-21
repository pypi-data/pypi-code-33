# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

from fsc.export import export
from pymatgen.io.cif import CifWriter

from aiida_tools import get_input_validator

from aiida.orm import JobCalculation, DataFactory
from aiida.orm.code import Code
from aiida.common.utils import classproperty
from aiida.common.datastructures import CalcInfo, CodeInfo


@export
class FilterSymmetriesCalculation(JobCalculation):
    """
    Calculation class to run the ``symmetry-repr filter_symmetries`` command.

    Arguments
    ---------
    symmetries : aiida.orm.data.singlefile.SinglefileData
        Set of all symmetries which are tested, in ``symmetry-representation`` HDF5 format.
    structure : aiida.orm.data.structure.StructureData
        Structure for which the compatibility of the symmetries is tested.
    """

    def _init_internal_params(self):
        super(FilterSymmetriesCalculation, self)._init_internal_params()

        self._OUTPUT_FILE_NAME = 'symmetries_out.hdf5'
        self._default_parser = 'symmetry_representation.symmetry'

    @classproperty
    def _use_methods(cls):
        retdict = super(cls, cls)._use_methods
        retdict['symmetries'] = dict(
            valid_types=DataFactory('singlefile'),
            additional_parameter=None,
            linkname='symmetries',
            docstring="File containing the symmetries (in HDF5 format)."
        )
        retdict['structure'] = dict(
            valid_types=DataFactory('structure'),
            additional_parameter=None,
            linkname='structure',
            docstring=
            "Structure with which the filtered symmetries should be compatible."
        )
        return retdict

    def _prepare_for_submission(self, tempfolder, inputdict):
        validate = get_input_validator(inputdict)

        struc_filename = 'lattice.cif'
        struc_file = tempfolder.get_abs_path(struc_filename)
        structure = validate('structure', valid_types=DataFactory('structure'))
        CifWriter(struct=structure.get_pymatgen()).write_file(struc_file)

        symmetries_filename = 'symmetries.hdf5'
        local_symmetries_file = validate(
            'symmetries', valid_types=DataFactory('singlefile')
        )

        code = validate('code', valid_types=Code)
        if inputdict:
            raise ValidationError(
                'Cannot add other nodes. Remaining input: {}'.
                format(inputdict)
            )

        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.remote_copy_list = []
        calcinfo.local_copy_list = [
            (local_symmetries_file.get_file_abs_path(), symmetries_filename)
        ]
        calcinfo.retrieve_list = [self._OUTPUT_FILE_NAME]

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = [
            'filter_symmetries', '-s', symmetries_filename, '-l',
            struc_filename, '-o', self._OUTPUT_FILE_NAME
        ]
        codeinfo.stdout_name = self._OUTPUT_FILE_NAME
        codeinfo.code_uuid = code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
