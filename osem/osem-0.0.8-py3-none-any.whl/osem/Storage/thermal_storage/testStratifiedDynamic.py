import unittest

from Ener.Storage.ThermalStorage.StratifiedDynamic import StratifiedDynamic

from Ener.common import DomainException


class TestStratifiedDynamic(unittest.TestCase):
    def test_if_all_arguments_are_here_no_exception_should_be_raised(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 2]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 1, 1]}
                             },
                "ports_out": {"port_1": {"height": 1.0, "flow_out": [1, 1, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 2]}
                              }
                }

        StratifiedDynamic(args)

    def test_if_any_required_argument_is_missing_an_exception_should_be_raised(self):
        args = {"height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_if_any_required_port_argument_is_missing_an_exception_should_be_raised(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_if_a_required_argument_has_an_incorrect_value_an_exception_should_be_raised(self):
        args = {"diameter": -1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": -2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": -5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 2.5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": -35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 25, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_if_a_required_port_argument_has_an_incorrect_value_an_exception_should_be_raised(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 2.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, -70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, -2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": -0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, -1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_if_an_optional_argument_has_an_incorrect_value_an_exception_should_be_raised(self):

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "inlet_water_temp": -10,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "rho_fluid": -1000,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "cp_mass_fluid": -1400,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "time_step": -2,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "nb_points_by_step": -2,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "U_tot": -12,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "wall_thick": -0.01,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "lambda_wall": -12,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "lambda_fluid": -0.6,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_if_a_port_list_argument_has_an_incorrect_length_an_exception_should_be_raised(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2]},
                              "port_2": {"height": 0.1, "flow_out": [2, 2, 1]}
                              }
                }
        with self.assertRaises(DomainException):
            StratifiedDynamic(args)

    def test_algorithm_should_work_with_all_up_down_configurations(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 0.9, "temp_in": [72, 70, 70], "flow_in": [1, 1, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [2, 2, 2]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [2, 2, 2]},
                              "port_2": {"height": 0.1, "flow_out": [1, 1, 1]}
                              }
                }

        StratifiedDynamic(args).calculate()

    def test_algorithm_should_work_with_a_temperature_inversion_for_the_bottom_level(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [1, 1, 1]},
                             "port_2": {"height": 0.1, "temp_in": [60, 60, 60], "flow_in": [2, 2, 2]}
                             },
                "ports_out": {"port_1": {"height": 1.0, "flow_out": [2, 2, 2]},
                              "port_2": {"height": 0.3, "flow_out": [1, 1, 1]}
                              }
                }

        StratifiedDynamic(args).calculate()

    def test_algorithm_should_work_with_negative_injected_flow(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [2, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.7, "flow_out": [2, 2, 1]}
                              }
                }

        StratifiedDynamic(args).calculate()

    def test_algorithm_should_work_with_positive_injected_flow(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 5, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 1.0, "temp_in": [72, 70, 70], "flow_in": [1, 2, 1]},
                             "port_2": {"height": 0.1, "temp_in": [25, 25, 25], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.9, "flow_out": [1, 2, 1]},
                              "port_2": {"height": 0.7, "flow_out": [2, 2, 1]}
                              }
                }

        StratifiedDynamic(args).calculate()

    def test_algorithm_should_work_if_two_ports_in_at_the_same_height(self):
        args = {"diameter": 1, "height": 2, "nb_of_layers": 10, "temp_init_max": 70, "temp_init_min": 35,
                "ports_in": {"port_1": {"height": 0.95, "temp_in": [72, 70, 70], "flow_in": [2, 2, 1]},
                             "port_2": {"height": 0.95, "temp_in": [65, 65, 67], "flow_in": [1, 2, 1]}
                             },
                "ports_out": {"port_1": {"height": 0.05, "flow_out": [2, 2, 1]},
                              "port_2": {"height": 0.05, "flow_out": [1, 2, 1]}
                              }
                }

        StratifiedDynamic(args).calculate()
