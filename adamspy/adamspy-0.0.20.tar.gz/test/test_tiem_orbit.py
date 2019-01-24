import unittest
import os
os.environ['ADRILL_SHARED_CFG'] = os.path.join('C:\\', 'MSC.Software', 'Adams', '2018', 'adrill', 'adrill.cfg')
os.environ['ADRILL_USER_CFG'] = os.path.join(os.environ['USERPROFILE'], '.adrill.cfg')
from adamspy import adripy

TEST_CONFIG_FILENAME = '_test_drill.cfg'
TEST_CONFIG_FILEPATH = os.path.join(os.getcwd(), 'test', TEST_CONFIG_FILENAME)
TEST_DATABASE_NAME = 'example_database'
TEST_DATABASE_PATH = os.path.join(os.getcwd(), 'test', TEST_DATABASE_NAME + '.cdb')

class Test_EventFile(unittest.TestCase):
    """
    Tests that adripy can correctly write an event file
    """
    
    TEST_EVENT_NAME = '_test_event_'
    EVENT_FILENAME = os.path.join(TEST_DATABASE_PATH,'events.tbl', f'{TEST_EVENT_NAME}.evt')

    EXPECTED_EVENT_FILE_TEXT = """$ ==================================================================
$ This is the Adams Drill Event file which contains
$ the following data blocks:
$   [UNITS]
$   [DRIVE]
$   [MISC]
$ 
$  NOTA BENE: block and subblock titles MUST begin in column 1.
$  Comments also must begin in column 1.
$  ==================================================================
$-------------------------------------------------------------ADAMS_DRILL_HEADER
[ADAMS_DRILL_HEADER]
 File_Type  =  'event'
 File_Version  =  1.0
$--------------------------------------------------------------------------UNITS
[UNITS]
$  Adams Drill currently supports one units set: 
$  'Imperial' (foot, degree, pound force, pound mass, second)
 Units  =  'Imperial'
$--------------------------------------------------------------------------DRIVE
[DRIVE]
(GENERAL)
 Event_Name  =  '_test_event_'
$ Valid Drive Types: 'WITH_MOTOR', 'TOP_ONLY'
 Drive_Type  =  'WITH_MOTOR'
$ Either 'TOS' (default) or user-selected tool from drill string
 Measurement_Tool  =  'TOS'
 Start_Depth  =  4000
 Off_Bottom  =  4
$ 
 Initial_Drive_Torque  =  0
$ 
(TOP_DRIVE)
{Start_Time  Ramp_Duration  Delta_RPM}
10   15   60
$ 
$ MOTOR valid only for DRIVE_TYPE = WITH_MOTOR
(MOTOR)
 Motor_Type  =  '3D'
$ 
$ No user control of this parameter.
 Filter_Time_Constant  =  0.05
$ 
$ Note that the motor starts out straight for simulation purposes and
$ builds up to the full bend over the ramp time.  The bend is defined
$ in the tool description.  These values allow the static simulation to
$ proceed better.  *They should not be changed by the user.*
 Motor_Bend_Start  =  1.0
 Motor_Bend_Ramp  =  9.0
$ 
{Start_Time  Ramp_Duration  Delta_RPM}
0   1   1
$ 
$ PUMP_FLOW applies only to 3D motors; valid only for DRIVE_TYPE = WITH_MOTOR
$ Gallons/minute in imperial units; Liters/minute in metric units
(PUMP_FLOW)
{Start_Time  Ramp_Duration  Delta_Flow_Rate}
1   10   500
$ 
(WOB)
{Start_Time  Ramp_Duration  Delta_WOB}
30   10   50
$ 
(ROP)
{Start_Time  Ramp_Duration  Delta_ROP}
35   10   100
$---------------------------------------------------------------------------MISC
[MISC]
$ Enter MUD_DENSITY in pounds-mass per cubic foot for IMPERIAL units
$ Enter MUD_DENSITY in kilograms per cubic meter for METRIC units
 Mud_Density  =  75
 Impact_Damping_Penetration  =  0.005
 Impact_Exponent  =  1.05
 MWD_Pulsing  =  'On'
$ 
(NPERREV)
$ See Adams Drill documentation prior to switching NperRev 'on'
 NperRev  =  'off'
 N  =  1
 S_threshold  =  0.55
 C_hi  =  1.05
{Start_Time  Ramp_Duration}
0   1
$-----------------------------------------------------------------------DYNAMICS
[DYNAMICS]
$ Specify the simulation time and output rate in seconds
{End_Time  Output_Step_Size}
10   0.05
100   0.05
$------------------------------------------------------------------------PLOT_4D
[PLOT_4D]
$ Select if 3D and 4D plotting is to be enabled (on/off).
$ If 3D/4D plotting is turned on, set time range and time increment at which
$ to take measurements ('Plotting_Interval'). Also specify where along the
$ string to measure (Start Distance and End Distance are relative to bit at 0).
$ One (1) contiguous block of not more than a 400 time measurements during the
$ simulation can be specified, for not more than one 5000ft (1500m) section
$ of the physically modeled string. (Equivalent Upper String not allowed.)
 Plotting_4D  =  'off'
 Start_Time  =  160
 End_Time  =  200
 Plotting_Interval  =  0.1
 Start_Distance  =  2.0
 End_Distance  =  100.0
    """

    def setUp(self):
        
        # Create a configuration file for testing
        adripy.create_cfg_file(TEST_CONFIG_FILENAME, [TEST_DATABASE_PATH])

        # Create event file object
        self.event_file = adripy.tiem_orbit.DrillEvent(self.TEST_EVENT_NAME, 4000, 4)
        
        # Add ramp parameters to event file object
        self.event_file.add_ramp('PUMP_FLOW', 1, 10, 500)
        self.event_file.add_ramp('TOP_DRIVE', 10, 15, 60)
        self.event_file.add_ramp('WOB', 30, 10, 50)
        self.event_file.add_ramp('ROP', 35, 10, 100)   

        # Add simulation steps to event file object
        self.event_file.add_simulation_step(10)
        self.event_file.add_simulation_step(100)     

        # Write an event file from the event file object
        self.event_file.write_to_file(cdb=TEST_DATABASE_NAME)
    
    def test_write_event_file(self):
        """
        Tests if the event file was written correctly.
        """
        # Read the event file
        with open(self.EVENT_FILENAME, 'r') as fid:
            lines = fid.readlines()
        
        # Initialize a list of failures
        failures = []

        # Loop through lines
        for actual_line, expected_line, line_num in zip(lines, self.EXPECTED_EVENT_FILE_TEXT.split('\n'), range(len(lines))):
            expected_line += '\n'
            
            # Test if lines are equal
            if actual_line != expected_line:
                failures.append('Event file mismatch (line {}): {} -- {}'.format(line_num, actual_line, expected_line))
            
        self.assertListEqual([], failures)

    def tearDown(self):

        # Delete test config file
        os.remove(TEST_CONFIG_FILENAME)
        os.environ['ADRILL_USER_CFG'] = os.path.join(os.environ['USERPROFILE'], '.adrill.cfg')

        # Delete the test event file
        os.remove(self.EVENT_FILENAME)

class Test_DrillTool(unittest.TestCase):
    """Tests the methods in adamspy.adripy.tiem_orbit.DrillTool
    """
    TEST_STABILZIER_NAME = 'example_stabilizer'
    NEW_STABILIZER_NAME = 'modified_stabilizer'
    STABILIZER_PARAM_TO_MODIFY = 'Stabilizer_ID'
    STABILIZER_NEW_PARAM_VALUE = 0.3

    def setUp(self):
        
        # Create a test config file containing the test database
        adripy.create_cfg_file(TEST_CONFIG_FILENAME, [TEST_DATABASE_PATH])
        
        # Create a DrillTool object from a stabilizer property file
        filename = os.path.join(f'<{TEST_DATABASE_NAME}>', 'stabilizers.tbl', self.TEST_STABILZIER_NAME + '.sta')
        self.stabilizer = adripy.tiem_orbit.DrillTool(filename)
        
        # Create an identical DrillTool object that will be modified later
        self.stabilizer_to_modify = adripy.tiem_orbit.DrillTool(os.path.join(f'<{TEST_DATABASE_NAME}>', 'stabilizers.tbl', self.TEST_STABILZIER_NAME + '.sta'))
        self.stabilizer_to_modify.rename(self.NEW_STABILIZER_NAME)

    def test_stabilizer_name(self):
        """Test that DrillTool.name is correct.
        """
        self.assertEqual(self.stabilizer.name, self.TEST_STABILZIER_NAME)

    def test_stabilizer_filename(self):
        """Test that DrillTool.property_file is correct
        """
        expected_filename = os.path.join(f'<{TEST_DATABASE_NAME}>', 'stabilizers.tbl', self.TEST_STABILZIER_NAME + '.sta')
        self.assertEqual(self.stabilizer.property_file, expected_filename)        
    
    def test_get_mass_value(self):
        """Test that DrillTool.get_parameter_value returns the mass of the stabilizer and not the mass unit.
        """
        mass = self.stabilizer.get_parameter_value('Mass')
        self.assertEqual(mass, 0)
    
    def test_get_string_parameter(self):
        """Test that DrillTool.get_parameter_value can return a parameter that has a string as its value.
        """
        tool_name = self.stabilizer.get_parameter_value('Tool_Name')
        self.assertEqual(tool_name, self.TEST_STABILZIER_NAME)

    def test_rename_name(self):
        """Tests that DrillTool.name was is changed correctly after DrillTool.rename().
        """
        self.assertEqual(self.stabilizer_to_modify.name, self.NEW_STABILIZER_NAME)
    
    def test_rename_property_file(self):
        """Tests that DrillTool.property_file is changed correctly after DrillTool.rename().
        """
        expected_filename = os.path.join(f'<{TEST_DATABASE_NAME}>', 'stabilizers.tbl', self.NEW_STABILIZER_NAME + '.sta')
        self.assertEqual(self.stabilizer_to_modify.property_file, expected_filename)
  
    def test_modify_parameter_value(self):
        """Modify a parameter value then get the parameter value and test the expected value is returned.
        """
        self.stabilizer_to_modify.modify_parameter_value(self.STABILIZER_PARAM_TO_MODIFY, self.STABILIZER_NEW_PARAM_VALUE)
        new_value = self.stabilizer_to_modify.get_parameter_value(self.STABILIZER_PARAM_TO_MODIFY)
        self.assertEqual(new_value, self.STABILIZER_NEW_PARAM_VALUE)    

    def tearDown(self):
        # Remove the stabilizer property file that was created
        modified_stabilizer_file = os.path.join(TEST_DATABASE_PATH, 'stabilizers.tbl', self.NEW_STABILIZER_NAME + '.sta')
        os.remove(modified_stabilizer_file)

        # Delete test config file
        os.remove(TEST_CONFIG_FILENAME)
        os.environ['ADRILL_USER_CFG'] = os.path.join(os.environ['USERPROFILE'], '.adrill.cfg')

if __name__ == '__main__':
    unittest.main()
