import json
import unittest
from classviz import *
import os

class TestClassViz(unittest.TestCase):

    def test_is_valid_svif_file(self):
        """
            Test is_valid_svif_file method
        """
        # Test files
        empty_json_file = 'tests/empty_json_file.json'
        txt_file = 'tests/text_file.txt'
        svif_file = 'tests/small_test.svif'

        # Test non-json file
        with self.assertRaises(SystemExit) as sys_exit_6:
            is_valid_svif_file(txt_file)
        self.assertEqual(sys_exit_6.exception.code, 6)

        # Test non-svif-format file
        with self.assertRaises(SystemExit) as sys_exit_7:
            is_valid_svif_file(empty_json_file)
        self.assertEqual(sys_exit_7.exception.code, 7)

        # Test correct svif-format file
        try:
            is_valid_svif_file(svif_file)
        except:
            self.fail("Validation failed.")
    
    def test_rm_file(self):
        """
            Test rm_file method
        """
        # Test file
        old_file = 'tests/test_rm.txt'
        no_file = 'tests/no_file.txt'

        # Create the file if it does not exist
        if not os.path.exists(old_file):
            fp = open(old_file, 'x')
            fp.write("A text goes here.")
            fp.close()

        # with open(old_file, 'w+') as f:
        #     f.write("A text goes here.")
        #     print('hi test')
        
        # Test remove file
        rm_file(old_file)
        self.assertFalse(os.path.exists(old_file))
        rm_file(no_file)
        self.assertFalse(os.path.exists(no_file))

    def test_copy_input_file_to_data_folder(self):
        """
            Test copy_input_file_to_data_folder method
        """
        # Test files
        input_file = 'tests/small_test.svif'
        output_file = 'tests/copied_test.svif'

        # Remove existing output file
        if os.path.exists(output_file):
            os.remove(output_file)

        # Test copy file
        copy_input_file_to_data_folder(input_file, output_file)
        self.assertTrue(os.path.exists(output_file))
        
        # Clean up
        os.remove(output_file)

    
if __name__ == 'main':
    unittest.main()
