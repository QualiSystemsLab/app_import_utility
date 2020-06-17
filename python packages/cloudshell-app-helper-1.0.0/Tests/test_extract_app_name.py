import unittest
from mock import patch, Mock, call
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.helpers.save_workflow.extract_app_name import extract_app_name


class ExtractAppNameTests(unittest.TestCase):

    def test_extract_app_name_no_spaces(self):
        test_app_name = 'TestApp a6t57j3io0'
        app_name = extract_app_name(test_app_name)
        self.assertEquals(app_name, 'TestApp')

    def test_extract_app_name_spaces(self):
        test_app_name = 'Test App a6t57j3io0'
        app_name = extract_app_name(test_app_name)
        self.assertEquals(app_name, 'Test App')

    def test_extract_app_name_multiple_spaces(self):
        test_app_name = 'T e s t App a6t57j3io0'
        app_name = extract_app_name(test_app_name)
        self.assertEquals(app_name, 'T e s t App')

    def test_extract_app_name_no_gap(self):
        test_app_name = 'TestAppa6t57j3io0'
        app_name = extract_app_name(test_app_name)
        self.assertEquals(app_name, 'TestAppa6t57j3io0')

    def test_extract_app_name_underscore(self):
        test_app_name = 'TestApp_a6t57j3io0'
        app_name = extract_app_name(test_app_name)
        self.assertEquals(app_name, 'TestApp_a6t57j3io0')

if __name__ == '__main__':
    unittest.main()
