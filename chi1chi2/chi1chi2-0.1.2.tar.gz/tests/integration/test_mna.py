from tests.integration.test_runner import ITTests, _get_options, _get_from_cif_options, _get_from_crystal_options, \
    _get_input_preparator_options, _get_main_options


class ITMNATests(ITTests):
    def test_from_cif_MNA(self):
        params = {}
        params["case"] = "mna_input"
        params["options"] = _get_options(_get_from_cif_options("mna.cif"))
        params["module-method"] = ["chi1chi2.from_cif", "run"]
        self._run_it(params)

    def test_from_crystal_MNA(self):
        params = {}
        params["case"] = "mna_crystal"
        params["options"] = _get_options(_get_from_crystal_options("mna.inp", "opt.out", "opt.SCFLOG"))
        params["module-method"] = ["chi1chi2.from_crystal", "run"]
        self._run_it(params)

    def test_input_preparator_MNA(self):
        params = {}
        params["case"] = "mna_input_preparator"
        params["options"] = _get_options(_get_input_preparator_options("mna.inp", "100."))
        params["module-method"] = ["chi1chi2.input_preparator", "run"]
        self._run_it(params)

    def test_lft_MNA(self):
        params = {}
        params["case"] = "mna_lft"
        params["options"] = _get_options(_get_main_options("mna.inp", "L.dat", "bchf", None))
        params["module-method"] = ["chi1chi2.main", "run"]
        self._run_it(params)

    def test_lft_qlft__MNA(self):
        params = {}
        params["case"] = "mna_lft_qlft"
        params["options"] = _get_options(_get_main_options("mna.inp", "L.dat", "bchf", None, "bp"))
        params["module-method"] = ["chi1chi2.main", "run"]
        self._run_it(params)
