import unittest
import os
import re

# Set the ADRILL_USER_CFG and ADRILL_SHARED_CFG environment variables
os.environ['ADRILL_USER_CFG'] = os.path.join('C:\\', 'Users', 'bthornt', '.adrill.cfg')
os.environ['ADRILL_SHARED_CFG'] = os.path.join('C:\\', 'MSC.Software', 'Adams', '2018', 'adrill', 'adrill.cfg')
from adamspy import adripy

def check_file_contents(filename, expected_text):
    """Checks that the given file contains the expected text.
    
    Arguments:
        filename {string} -- Name of file to check
        expected_text {string} -- Expected contents of file
    
    Returns:
        list -- list of unexpected lines
    """

    # Read the file
    with open(filename, 'r') as fid:
        lines = fid.readlines()

    # Initialize a list of failures
    failures = []

    # Loop through lines
    for actual_line, expected_line, line_num in zip(lines, expected_text.split('\n'), range(len(lines))):
        expected_line += '\n'

        # Test if lines are equal
        if actual_line != expected_line:
            failures.append('Unexpected file contents (line {}): ACTUAL: {} -- EXPECTED: {}'.format(line_num, actual_line, expected_line))
    
    return failures

class Test_AdripyFunctions(unittest.TestCase):

    TEST_CONFIG_FILENAME = '_test_drill.cfg'

    EXISTING_CDB_NAME = '_EXISTING_DATABASE_1'
    EXISTING_CDB_PATH = os.path.join('C:\\', EXISTING_CDB_NAME + '.cdb')

    NEW_CDB_NAME = '_NEW_DATABASE'
    NEW_CDB_PATH = os.path.join('C:\\', NEW_CDB_NAME + '.cdb')
    
    CDB_TO_REMOVE_NAME = '_EXISTING_DATABASE_2'
    CDB_TO_REMOVE_PATH = os.path.join('C:\\', CDB_TO_REMOVE_NAME + '.cdb')

    EXAMPLE_STABILIZER_NAME = 'example_stabilizer'

    TEST_ORIG_CONFIG_FILE_TEXT = f'''!----------------------------------------------------------------------!
! ************  Adams Drill Private Configuration File  ************
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal environment variables
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal database directories
!            Database name     Path of Database
!----------------------------------------------------------------------!
DATABASE   {EXISTING_CDB_NAME}   {EXISTING_CDB_PATH}
DATABASE   {CDB_TO_REMOVE_NAME}   {CDB_TO_REMOVE_PATH}

DEFAULT_WRITE_DB    adrill_private
!
!----------------------------------------------------------------------!
! - List of personal tables directories
!            Type class            Name of table              Extension
!----------------------------------------------------------------------!
! Example table entry:
!TABLE        example               example.tbl                      exa
!
!----------------------------------------------------------------------!
! - List of personal default property files
!            Type class         Default property file
!----------------------------------------------------------------------!
! Example property file entry:
!PROPFILE     pdc_bit           <adrill_private>/pdc_bits.tbl/SC_Acme_Co_695b.pdc
!----------------------------------------------------------------------!
'''

    EXPECTED_CONFIG_FILE_AFTER_ADD = f'''!----------------------------------------------------------------------!
! ************  Adams Drill Private Configuration File  ************
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal environment variables
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal database directories
!            Database name     Path of Database
!----------------------------------------------------------------------!
DATABASE   {EXISTING_CDB_NAME}   {EXISTING_CDB_PATH}
DATABASE   {CDB_TO_REMOVE_NAME}   {CDB_TO_REMOVE_PATH}
DATABASE   {NEW_CDB_NAME}   {NEW_CDB_PATH}

DEFAULT_WRITE_DB    adrill_private
!
!----------------------------------------------------------------------!
! - List of personal tables directories
!            Type class            Name of table              Extension
!----------------------------------------------------------------------!
! Example table entry:
!TABLE        example               example.tbl                      exa
!
!----------------------------------------------------------------------!
! - List of personal default property files
!            Type class         Default property file
!----------------------------------------------------------------------!
! Example property file entry:
!PROPFILE     pdc_bit           <adrill_private>/pdc_bits.tbl/SC_Acme_Co_695b.pdc
!----------------------------------------------------------------------!
'''

    EXPECTED_CONFIG_FILE_AFTER_REMOVE = f'''!----------------------------------------------------------------------!
! ************  Adams Drill Private Configuration File  ************
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal environment variables
!----------------------------------------------------------------------!
!
!----------------------------------------------------------------------!
! - List of personal database directories
!            Database name     Path of Database
!----------------------------------------------------------------------!
DATABASE   {EXISTING_CDB_NAME}   {EXISTING_CDB_PATH}

DEFAULT_WRITE_DB    adrill_private
!
!----------------------------------------------------------------------!
! - List of personal tables directories
!            Type class            Name of table              Extension
!----------------------------------------------------------------------!
! Example table entry:
!TABLE        example               example.tbl                      exa
!
!----------------------------------------------------------------------!
! - List of personal default property files
!            Type class         Default property file
!----------------------------------------------------------------------!
! Example property file entry:
!PROPFILE     pdc_bit           <adrill_private>/pdc_bits.tbl/SC_Acme_Co_695b.pdc
!----------------------------------------------------------------------!
'''
    
    def setUp(self):
        # Create a test configuration file
        adripy.create_cfg_file(self.TEST_CONFIG_FILENAME, [self.EXISTING_CDB_PATH, self.CDB_TO_REMOVE_PATH])
        os.environ['ADRILL_USER_CFG'] = self.TEST_CONFIG_FILENAME
    
    def test_create_cfg_file(self):
        """Tests that create_cfg_file() creates a configuration file with the expected contents
        """

        # Check the config file contents
        failures = check_file_contents(self.TEST_CONFIG_FILENAME, self.TEST_ORIG_CONFIG_FILE_TEXT)
        
        self.assertListEqual([], failures)

    def test_add_cdb_to_cfg(self):
        """
        Tests if adripy.add_cdb_to_cfg adds the correct cdb.
        """
        # Run the function
        adripy.add_cdb_to_cfg(self.NEW_CDB_NAME, self.NEW_CDB_PATH, self.TEST_CONFIG_FILENAME)

        # Check the config file contents
        failures = check_file_contents(self.TEST_CONFIG_FILENAME, self.EXPECTED_CONFIG_FILE_AFTER_ADD)
        
        self.assertListEqual([], failures)

    def test_remove_cdb_from_cfg(self):
        """
        Tests if adripy.remove_cdb_from_cfg removes the correct cdb.
        """

        # Run the function
        adripy.remove_cdb_from_cfg(self.CDB_TO_REMOVE_NAME, self.TEST_CONFIG_FILENAME)
        
        # Check the config file contents
        failures = check_file_contents(self.TEST_CONFIG_FILENAME, self.EXPECTED_CONFIG_FILE_AFTER_REMOVE)
        
        self.assertListEqual([], failures)

    def test_get_full_path(self):
        """Test that adripy.get_full_path returns the correct path.
        """
        expected_full_path = os.path.join(self.EXISTING_CDB_PATH, 'stabilizers.tbl', self.EXAMPLE_STABILIZER_NAME + '.sta')
        example_cdb_path = os.path.join(f'<{self.EXISTING_CDB_NAME}>', 'stabilizers.tbl', self.EXAMPLE_STABILIZER_NAME + '.sta')
        full_path = adripy.get_full_path(example_cdb_path)

        self.assertEqual(full_path, expected_full_path)

        
    def tearDown(self):
        os.remove(self.TEST_CONFIG_FILENAME)

if __name__ == '__main__':
    unittest.main()
