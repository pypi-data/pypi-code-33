"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import json
from .jemu_button import JemuButton
from .jemu_i2c_master import JemuI2cMaster
from .jemu_i2c_slave import JemuI2cSlave
from .jemu_mem_peripheral import JemuMemPeripheral
from .jemu_bma280 import JemuBMA280
from .jemu_sudo import JemuSudo
from .jemu_bq24160 import JemuBQ24160
from .jemu_bq27421 import JemuBQ27421
from .platforms import platforms_list_upper
from .jemu_uart_json import JemuUartJson as JemuUart


class JemuBspParser:
    
    def __init__(self):
        self._EXTERNAL_PERIPHERAL = "External"

    def _get_json(self, file_path):
        if not os.path.isfile(file_path):
            raise Exception(file_path + ' is not found')
        elif not os.access(file_path, os.R_OK):
            raise Exception(file_path + ' is not readable')

        else:
            with open(file_path) as opened_file_path:
                return json.load(opened_file_path)

    def get_platform(self, config_json_path):
        config_json = self._get_json(config_json_path)
        for component in config_json["components"]:
            if 'class' in component:
                if any(component["class"] in p for p in platforms_list_upper):
                    name = component["class"].lower()
                    name = 'stm32f411' if name == 'stm32f4' else 'nrf52832' if name == 'mcu' else name  # backward compatibility
                    return name


    def get_components(self, jemu_connection, config_json_path):
        if config_json_path is None:
            return []

        components_list = []
        config_json = self._get_json(config_json_path) # bsp or board.json

        for component in config_json["components"]:
            component_name = component["name"]
            component_obj = None

            if ("config" in component) and ("generators" in component["config"]):
                generators = component["config"]["generators"]
            else:
                generators = None

            if 'class' in component:
                if component["class"] == "Button":
                    component_obj = JemuButton(jemu_connection, component_name)

                elif component["class"] == "I2cSlaveSdk":
                    component_obj = JemuI2cSlave(jemu_connection, component_name)

                elif component["class"] == "I2cMasterSdk":
                    component_obj = JemuI2cMaster(jemu_connection, component_name)

                elif component["class"] == "BME280":
                    component_obj = JemuMemPeripheral(jemu_connection, component_name, self._EXTERNAL_PERIPHERAL, generators)

                elif component["class"] == "BQ24160":
                    component_obj = JemuBQ24160(jemu_connection, component_name, self._EXTERNAL_PERIPHERAL, generators)

                elif component["class"] == "BQ27421":
                    component_obj = JemuBQ27421(jemu_connection, component_name, self._EXTERNAL_PERIPHERAL, generators)

                elif component["class"] == "BMA280":
                    component_obj = JemuBMA280(jemu_connection, component_name, self._EXTERNAL_PERIPHERAL, generators)

            elif 'type' in component:
                if component["type"] == "Peripheral":
                    component_obj = JemuMemPeripheral(jemu_connection, component_name, self._EXTERNAL_PERIPHERAL, generators)

            if component_obj is not None:
                if component["type"] == "Peripheral": # external peripheral
                    components_list.append({"obj": component_obj, "name": component["name"], "type":component["type"]})
                else: # internal peripheral - the name is the class field 
                    components_list.append({"obj": component_obj, "name": component["class"], "type":component["type"]})

        return components_list


    # Internal components can be found only in the default-board-json
    def get_internal_components(self, default_json_path, vlab, mcu_name, jemu_connection, gdb_mode):
        internal_components = []
        default_json = self._get_json(default_json_path)
        
        for component in default_json["components"]:

            if component['type'] == 'MCU': # Add internal peripherals
                if 'internal_peripherals' in component['config']:
                    internal_peripherals = component['config']["internal_peripherals"]
                    for internal_peripheral in internal_peripherals:
                        if 'type' in internal_peripheral:
                            peripheral = None
                            peripheral_type = internal_peripheral['type']
                            if (peripheral_type == 'uart'):
                                peripheral = JemuUart(vlab, internal_peripheral["class"], mcu_name)
                            elif(peripheral_type == 'sudo'):
                                peripheral = JemuSudo(jemu_connection, internal_peripheral["class"], mcu_name, gdb_mode)
                            # Add new peripherals here #
                            
                            ###

                            if peripheral != None: # In case of internal peripheral, the name is the class field
                                internal_components.append({"obj": peripheral, "name": internal_peripheral["class"], "type":peripheral_type})

        return internal_components







