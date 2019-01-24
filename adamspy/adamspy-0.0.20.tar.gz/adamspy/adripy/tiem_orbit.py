"""
--------------------------------------------------------------------------
Description
--------------------------------------------------------------------------
tiem_orbit is a set of python tools for manipulating MSC Adams Drill Tiem
Orbit files.
--------------------------------------------------------------------------
Author
--------------------------------------------------------------------------
Ben Thornton (ben.thornton@mscsofware.com)
Simulation Consultant - MSC Software
"""
import os
import re
import shutil
import jinja2
from .adripy import get_cdb_location, get_cdb_path, get_full_path

env = jinja2.Environment(
    loader=jinja2.PackageLoader('adamspy.adripy', 'templates'),
    autoescape=jinja2.select_autoescape(['evt','str']),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True
)

class DrillEvent():
    """
    Creates an object with all data necessary to write a drill event.  Once the DrillEvent is instanced
    ramp parameters must be defined before the DrillEvent is written to an event file.  
    
    All parameters in the event file can be specified when the DrillEvent is instanced 
    using **kwargs or they can be set later using: 
        
        DrillEvent.parameters[parameter] = value    
    """

    SCALAR_PARAMETERS = [
        'File_Type',
        'Units',
        'File_Version',
        'Event_Name',
        'Drive_Type',
        'Measurement_Tool',
        'Start_Depth',
        'Off_Bottom',
        'Initial_Drive_Torque',
        'Motor_Type',
        'Filter_Time_Constant',
        'Motor_Bend_Start',
        'Motor_Bend_Ramp',
        'Mud_Density',
        'Impact_Damping_Penetration',
        'Impact_Exponent',
        'MWD_Pulsing',
        'NperRev',
        'N',
        'S_threshold',
        'C_hi',
        'Plotting_4D',
        'Start_Time',
        'End_Time',
        'Plotting_Interval',
        'Start_Distance',
        'End_Distance'
    ]
    DEFAULT_PARAMETER_SCALARS = {
        'File_Type': 'event',
        'File_Version': 1.0,
        'Units': 'Imperial',
        'Drive_Type': 'WITH_MOTOR',
        'Measurement_Tool': 'TOS',
        'Initial_Drive_Torque': 0,
        'Motor_Type': '3D',
        'Filter_Time_Constant': 0.05,
        'Motor_Bend_Start': 1.0,
        'Motor_Bend_Ramp': 9.0,
        'Mud_Density': 75,
        'Impact_Damping_Penetration': 0.005,
        'Impact_Exponent': 1.05,
        'MWD_Pulsing': 'On',
        'NperRev': 'off',
        'N': 1,
        'S_threshold': 0.55,
        'C_hi': 1.05,
        'Plotting_4D': 'off',
        'Start_Time': 160,
        'End_Time': 200,
        'Plotting_Interval': 0.1,
        'Start_Distance': 2.0,
        'End_Distance': 100.0
    }

    ARRAY_PARAMETERS = [
        'TOP_DRIVE',
        'MOTOR',
        'PUMP_FLOW',
        'WOB',
        'ROP',
        'NPERREV',
        'DYNAMICS'
    ]

    DEFAULT_PARAMETER_ARRAYS = {
        'TOP_DRIVE': [[],[],[]],
        'MOTOR': [[0], [1], [1]],
        'PUMP_FLOW': [[],[],[]],
        'WOB': [[],[],[]],
        'ROP': [[],[],[]],
        'NPERREV': [[0],[1]],
        'DYNAMICS': [[], []]
    }

    CDB_TABLE = 'events.tbl'
    EXT = '.evt'

    def __init__(self, event_name, start_depth, off_bottom, **kwargs):
        self.parameters = kwargs
        self.parameters['Event_Name'] = event_name
        self.parameters['Start_Depth'] = start_depth
        self.parameters['Off_Bottom'] = off_bottom        
        
        # Apply default parameters                
        self._apply_defaults()    

        self.filename = ''

    def add_simulation_step(self, end_time, output_step_size=0.05, clear_existing=False):
        """
        Adds a dynamic simulation step.
        
        Arguments:
            end_time {float} -- End time of the step.
            output_step_size {foat} -- Output step size of the step. Defaults to 0.05.
        """
        if clear_existing:
            self.parameters['DYNAMICS'] = [[],[]]
        self.parameters['DYNAMICS'][0].append(end_time)
        self.parameters['DYNAMICS'][1].append(output_step_size)
        self.parameters['_DYNAMICS'] = zip(*self.parameters['DYNAMICS'])
    
    def add_ramp(self, parameter, start_time, ramp_duration, delta, clear_existing=False):
        """Adds a ramp to the specified ramp parameter
        
        Arguments:
            parameter {string} -- ramp parameter, options are 'TOP_DRIVE', 'WOB', 'PUMP_FLOW', of 'ROP'
            start_time {float} -- Start time of the ramp.
            ramp_duration {float} -- Duration of the ramp.
            delta {float} -- Delta of the ramp.
            clear_existing {bool} -- If true, existing ramps for the specified parameter will be deleted.
        """
        if clear_existing:
            self.parameters[parameter] = [[],[],[]]
        self.parameters[parameter][0].append(start_time)
        self.parameters[parameter][1].append(ramp_duration)
        self.parameters[parameter][2].append(delta)
        self.parameters['_' + parameter] = zip(*self.parameters[parameter])    

    def write_to_file(self, write_directory=None, filename=None, cdb=None):
        """Creates an event file from the DrillEvent object.
        
        Keyword Arguments:
            write_directory {string} -- (OPTIONAL) Directory in which to write the file. Defaults to current working directory.
            filename {string} -- (OPTIONAL) Name of the file to write.  Defaults to self.parameters['EVENT_NAME']
            cdb {string} -- (OPTIONAL) Name of the cdb in which to write the file.  This argument overrides the write_directory.
        
        Raises:
            ValueError -- Raised if not all parameters have been defined.
        """
        if not self.validate():
            raise ValueError('The parameters could not be validated.')
        
        if write_directory is None and cdb is None:
            write_directory = os.getcwd()
        elif cdb is not None:
            write_directory = get_cdb_location(cdb)        
        if filename is None:
            filename = self.parameters['Event_Name']
        if not filename.endswith(self.EXT):
            filename += self.EXT
                      
        event_template = env.get_template(f'template{self.EXT}')

        filepath = os.path.join(write_directory, self.CDB_TABLE, filename)
        
        with open(filepath, 'w') as fid:
            fid.write(event_template.render(self.parameters))

        self.filename = get_cdb_path(filepath)

    
    def validate(self):
        """
        Determines if all parameters have been set
        
        Returns:
            Bool -- True if all parameters have been set. Otherwise False
        """
        validated = True        
        # Check that all parameters exist in the self.parameters dictionary
        for param_name in self.SCALAR_PARAMETERS:
            if param_name not in self.parameters:
                validated = False        
        
        for param_name in self.ARRAY_PARAMETERS:
            if not self.parameters[param_name]:
                validated = False
            
        return validated        

    def _apply_defaults(self):
        """
        Applies defaults from class variables
        """
        # Applies normal parameter defaults
        for scalar_parameter, value in self.DEFAULT_PARAMETER_SCALARS.items():
            if scalar_parameter not in self.parameters:
                self.parameters[scalar_parameter] = value

        # Applies defaults to all ramp parameters
        for array_parameter, array in self.DEFAULT_PARAMETER_ARRAYS.items():
            self.parameters[array_parameter] = {}
            self.parameters[array_parameter] = array
            self.parameters['_' + array_parameter] = zip(*self.parameters[array_parameter])

class DrillString():

    """
    Creates an object with all data necessary to write a drill string.  Once the DrillString is instanced
    tools within the string must be defined as DrillTool objects before the string is written to an string file.  
    
    All parameters in the string file can be specified when the DrillString is instanced 
    using **kwargs or they can be set later using: 
        
        DrillEvent.parameters[parameter] = value    
    """

    SCALAR_PARAMETERS = [
        'Units',
        'ModelName',
        'OutputName',
        'Gravity',
        'Deviation_Deg',
        'Adams_Results',
        'Adams_Requests',
        'SolverDLL',
        'Hole_Property_File',
        'Contact_Method',
        'Cyl_Drag_Coeff',
        'Hole_Color',
        'Event_Property_File'
    ]
    DEFAULT_PARAMETER_SCALARS = {
        'Units': 'Imperial',
        'Gravity': 32.187,
        'Deviation_Deg': 0.0,
        'Adams_Results': 'animation',
        'Adams_Requests': 'on',
        'SolverDLL': 'adrill_solver',
        'Contact_Method': 'Subroutine',
        'Cyl_Drag_Coeff': 1.2,
        'Hole_Color': 'LtGray'
    }

    ARRAY_PARAMETERS = [
        'Distance_from_Bit'
    ]

    DEFAULT_PARAMETER_ARRAYS = {
        'Distance_from_Bit': [[]]
    }

    CDB_TABLE = 'drill_strings.tbl'
    EXT = '.str'

    def __init__(self, string_name, hole_file, event_file, **kwargs):
        self.parameters = kwargs
        self.parameters['ModelName'] = string_name
        self.parameters['OutputName'] = string_name
        self.parameters['Hole_Property_File'] = hole_file
        self.parameters['Event_Property_File'] = event_file
                        
        self._apply_defaults()

        self.tools = []
        self.top_drive = {}

    def add_tool(self, drill_tool, joints=1, measure='no', stack_order=None, color='Default'):
        """
        Adds a DrillTool object to the DrillString.
        
        Arguments:
            tool {DrillTool} -- An adripy DrillTool object.
        
        Keyword Arguments:
            joints {int} -- Number of Joints (only applies for certain tool types) (default: {1})
            measure {str} -- 'on' or 'off' (default: {'no'})
            stack_order {int} -- If an integer is given the tool will be inserted into the string at that point.  Otherwise it will be appended (default: {None})
            color {str} -- The color used to render the tool in an Adams Drill animation. (default: {'Default'})
        """
        if drill_tool.type.lower() != 'top_drive':
            # If the tool added IS NOT a top_drive
            tool = {
                'DrillTool': drill_tool,
                'Type': drill_tool.tool_type,
                'Name': drill_tool.name,
                'Property_File': drill_tool.property_file,
                'Measure': measure,
                'Color': color,
                'Number_of_Joints': joints
            }
            if stack_order is None:
                self.tools.append(tool)
            else:
                self.tools.insert(stack_order-1, tool)
            
            # Set Stack Orders equal to place in list
            for stack_order, tool in enumerate(self.tools):
                tool['Stack_Order'] = stack_order + 1
        else:
            # If the tool added IS a top_drive
            self.top_drive = {
                'DrillTool': drill_tool,
                'Type': drill_tool.tool_type,
                'Name': drill_tool.name,
                'Property_File': drill_tool.property_file
            }
    
    def add_measurement_point(self, distance):
        """
        Adds a measurement point at the given distance from the bit in feet.
        
        Arguments:
            distance {float} -- Distance from the bit (in feet) at which to place a measurement point.
        """
        self.parameters['Distance_from_Bit'][0].append(distance)
        self.parameters['Distance_from_Bit'][0].sort()
        
    def write_to_file(self, write_directory=None, filename=None, cdb=None, publish=False):
        """Creates string file from the DrillString object.
        
        Keyword Arguments:
            write_directory {string} -- (OPTIONAL) Directory in which to write the file. Defaults to current working directory.
            filename {string} -- (OPTIONAL) Name of the file to write.  Defaults to self.parameters['EVENT_NAME']
            cdb {string} -- (OPTIONAL) Name of the cdb in which to write the file.  This argument overrides the write_directory.
            publish {bool} -- (OPTIONAL) Writes all the supporting files to the same cdb.
        
        Raises:
            ValueError -- Raised if not all parameters have been defined.
        """
        # Validate the parameters
        if not self.validate():
            raise ValueError('The parameters could not be validated.')
        
        if write_directory is None and cdb is None:
            write_directory = os.getcwd()
        elif cdb is not None:
            write_directory = get_cdb_location(cdb)        
        if filename is None:
            filename = self.parameters['ModelName']
        if not filename.endswith(self.EXT):
            filename += self.EXT
                      
        # Define templates
        string_template_1 = env.get_template(f'template_1{self.EXT}')
        string_template_2 = env.get_template(f'template_2{self.EXT}')
        string_template_3 = env.get_template(f'template_3{self.EXT}')

        # Write any tools that haven't been written
        for tool in self.tools:
            if publish is True or tool.file_written is True:
                tool.write_to_file(write_directory=write_directory, filename=filename, cdb=cdb)
        
        with open(os.path.join(write_directory, self.CDB_TABLE, filename), 'w') as fid:
            # Write the top of the file
            fid.write(string_template_1.render(self.parameters))
            
            # Write the tool blocks
            for tool in self.tools:
                fid.write(string_template_2.render(tool))

            # Write the top_of_string block
            fid.write(string_template_3.render(self.top_drive))

    
    def validate(self):
        """
        Determines if all parameters have been set
        
        Returns:
            Bool -- True if all parameters have been set. Otherwise False
        """
        validated = True        
        # Check that all parameters exist in the self.parameters dictionary
        for param_name in self.SCALAR_PARAMETERS:
            if param_name not in self.parameters:
                validated = False        
        
        # Test that the DrillString has a top_drive defined
        if not self.top_drive:
            validated = False

        # Check that the DrillString has EUS
        eus_found = False
        ps_found = False
        pdc_found = False
        for tool in self.tools:
            if tool.type.lower() == 'equivalent_upper_string':
                eus_found = True
            elif tool.type.lower() == 'drillpipe':
                ps_found = True
            elif tool.type.lower() == 'pdc_bit':
                pdc_found = True
        if not all([eus_found, ps_found, pdc_found]):
            validated = False        
            
        return validated        

    def _apply_defaults(self):
        """
        Applies defaults from class variables
        """
        # Applies normal parameter defaults
        for scalar_parameter, value in self.DEFAULT_PARAMETER_SCALARS.items():
            if scalar_parameter not in self.parameters:
                self.parameters[scalar_parameter] = value

        # Applies defaults to all ramp parameters
        for array_parameter, array in self.DEFAULT_PARAMETER_ARRAYS.items():
            self.parameters[array_parameter] = {}
            self.parameters[array_parameter] = array
            self.parameters['_' + array_parameter] = zip(*self.parameters[array_parameter])

class DrillTool():
    """
    Object representing an Adams Drill tool.  Instances must be generated from a tool property file.
    
    Arguments:
        {string} -- Filepath to an Adams Drill Tool property file.
    """

    TO_PARAMETER_PATTERN = re.compile('^ [_a-zA-Z]+ += +.+')
    TO_HEADER_PATTERN = re.compile('^[[_a-zA-A]+')    
    EXTENSIONS = {
        'assembly': 'str',    
        'drillpipe': 'pip',
        'drill_collar': 'col',
        'hole': 'hol',
        'accelerator': 'acc',
        'stabilizer': 'sta',
        'short_collar': 'sco',
        'dart': 'drt',
        'jar': 'djr',
        'agitator': 'agi',
        'blade_reamer': 'bre',
        'crossover': 'crs',
        'darts': 'drt',
        'event': 'evt',
        'flex_pipe': 'flp',
        'hw_pipe': 'hwp',
        'pdc_bit': 'pdc',
        'motor': 'mot',
        'shock_sub': 'shk',
        'lwd_tool': 'lwd',
        'mfr_tool': 'mfr',
        'mwd_tool': 'mwd',
        'rss': 'rsd',
        'instrumentation_sub': 'ins',
        'generic_long': 'gnl',
        'generic_short': 'gns',
        'roller_cone_bit': 'rcb',
        'solver_setting': 'ssf',
        'plot_config': 'plt',
        'top_drive': 'tdr',
        'equivalent_upper_string': 'pip'
    }

    
    def __init__(self, property_file):
        self.property_file = get_cdb_path(property_file)
        self.name = self._get_name()
        self.tool_type = self._get_type()    
        self.extension = self._get_extension()
    
    def rename(self, new_name, remove_original=False):
        """
        Rename the tool
        
        Arguments:
            new_name {string} -- New name for the tool.
            in_place {bool} -- If True will rename the property file.  If False will create a new one.
        """
        # Determine the new filename
        current_filename = get_full_path(self.property_file)
        current_filepath = os.path.split(current_filename)[0]
        new_filename = os.path.join(current_filepath, f'{new_name}.{self.extension}')
        
        # Copy the file to the new location
        shutil.copyfile(current_filename, new_filename)
        self.property_file = get_cdb_path(new_filename)   

        # Modify the property file
        self.modify_parameter_value('Name', new_name)

        # Change the name variable
        self.name = new_name     
        
        if remove_original is True:

            # Delete the old property file
            os.remove(current_filename)

    def get_parameter_value(self, parameter_to_get):
        """
        Returns the value of the specified parameter from the property file.  NOTE: get_parameter_value cannot get parameters from the UNITS block.
        
        Arguments:
            parameter_to_get {string} -- Name of the parameter to get from the property file.
        
        Returns:
            {string or float} -- Value of the specified parameter from the property file.
        """
        # Initilize return variable as None
        value = None

        # Read the property file
        filename = get_full_path(self.property_file)
        with open(filename, 'r') as fid:
            lines = fid.readlines()

        # Initialize a boolean specifying if the for loop is at a line in the [UNITS] block
        at_units_block = False
        
        for line in lines:                
            # For each line in the property file
            
            if at_units_block and self.TO_HEADER_PATTERN.match(line):
                # If end of units block reached 
                at_units_block = False

            elif line.startswith('[UNITS]'):
                # If beginning of units block reached
                at_units_block = True

            if self.TO_PARAMETER_PATTERN.match(line) and at_units_block is False:                
                # If the line matches the pattern of a parameter definition

                # Split the line into parameter and value
                [current_parameter, current_value] = line.replace('\n','').replace(' ','').split('=')
                if current_parameter.lower() == parameter_to_get.lower():
                    # If the parameter on the current line is the parameter to get
                    
                    if "'" in current_value:
                        # If the value is a string
                        value = current_value.replace("'",'')
                    
                    else:
                        # If the value is a number
                        value = float(current_value)                    
                    break
        return value

    def modify_parameter_value(self, parameter_to_change, new_value):
        """Modifies a parameter in a DrillTool property file
        
        Arguments:
            parameter_to_change {string} -- Name of the parameter to modify.  Must match the name in the property file. (Not case sensitive). 
            new_value {float or string} -- New value of the parameter to change
        
        Keyword Arguments:
            new_filename {string} -- Filename of new property file.  If None the original property file will be overwritten (default: {None})
        """

        filename = get_full_path(self.property_file)        
            
        # Read the lines in the original file into a list
        with open(filename, 'r') as fid:
            original_lines = fid.readlines()

        # Write a new list with the correct line modified
        new_lines = []
        for line in original_lines:
                
            # For each line in the original file
            new_lines.append(line)
            if self.TO_PARAMETER_PATTERN.match(line):
                
                # If the line matches the pattern of a parameter definition
                [current_parameter, value] = line.replace('\n','').replace(' ','').split('=')
                if current_parameter.lower() == parameter_to_change.lower():

                    # If the parameter is the parameter to be changed
                    if "'" in value:

                        # If the value is a string
                        new_value = "'{}'".format(new_value)
                    
                    new_lines[-1] = ' {}  =  {}\n'.format(current_parameter, new_value)

        with open(filename, 'w') as fid:
            fid.writelines(new_lines)

    def _get_name(self):
        return self.get_parameter_value('Name')
    
    def _get_type(self):
        return self.get_parameter_value('File_Type')
    
    def _get_extension(self):
        extension = self.EXTENSIONS[self.tool_type]
        return extension


        



        





                

        

        
