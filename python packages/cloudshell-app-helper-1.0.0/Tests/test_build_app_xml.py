import unittest
from mock import patch, Mock, call
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.helpers.app_import.build_app_xml import app_template


class BuildAppXmlTests(unittest.TestCase):

    def test_build_app_xml_empty(self):
        pass


if __name__ == '__main__':
    unittest.main()