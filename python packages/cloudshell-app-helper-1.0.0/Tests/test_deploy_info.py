import unittest
from mock import patch, Mock, call
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.helpers.save_workflow.deploy_info import DeployInfo


class DeployInfoTests(unittest.TestCase):

    def test_deploy_info_no_attributes(self):

        deployment_path = Mock()
        deployment_path.Name = 'Deployment Path Name'
        deployment_path.IsDefault = True

        deployment_service = Mock()
        deployment_service.Name = 'Deployment Service Name'
        deployment_service.Attributes = []

        deployment_path.DeploymentService = deployment_service

        deployment_paths = [deployment_path]

        info_block = DeployInfo(deployment_paths)
        self.assertEquals(info_block, {'deploypaths': [{'is_default': True,
                                                        'service_name': 'Deployment Service Name',
                                                        'name': 'Deployment Path Name',
                                                        'attributes': {}}]})

    def test_deploy_info_one_attribute(self):

        deployment_path = Mock()
        deployment_path.Name = 'Deployment Path Name'
        deployment_path.IsDefault = True

        deployment_service = Mock()
        deployment_service.Name = 'Deployment Service Name'

        deployment_attribute = Mock()
        deployment_attribute.Name = 'Attribute 1'
        deployment_attribute.Value = 'Value 1'

        deployment_service.Attributes = [deployment_attribute]

        deployment_path.DeploymentService = deployment_service

        deployment_paths = [deployment_path]

        info_block = DeployInfo(deployment_paths)
        self.assertEquals(info_block, {'deploypaths': [{'is_default': True,
                                                        'service_name': 'Deployment Service Name',
                                                        'name': 'Deployment Path Name',
                                                        'attributes': {'Attribute 1': 'Value 1'}}]})

    def test_deploy_info_few_attributes(self):

        deployment_path = Mock()
        deployment_path.Name = 'Deployment Path Name'
        deployment_path.IsDefault = True

        deployment_service = Mock()
        deployment_service.Name = 'Deployment Service Name'

        deployment_attribute = Mock()
        deployment_attribute.Name = 'Attribute 1'
        deployment_attribute.Value = 'Value 1'

        deployment_attribute2 = Mock()
        deployment_attribute2.Name = 'Attribute 2'
        deployment_attribute2.Value = 'Value 2'

        deployment_attribute3 = Mock()
        deployment_attribute3.Name = 'Attribute 3'
        deployment_attribute3.Value = 'Value 3'

        deployment_service.Attributes = [deployment_attribute, deployment_attribute2, deployment_attribute3]

        deployment_path.DeploymentService = deployment_service

        deployment_paths = [deployment_path]

        info_block = DeployInfo(deployment_paths)
        self.assertEquals(info_block, {'deploypaths': [{'is_default': True,
                                                        'service_name': 'Deployment Service Name',
                                                        'name': 'Deployment Path Name',
                                                        'attributes': {'Attribute 1': 'Value 1',
                                                                       'Attribute 2': 'Value 2',
                                                                       'Attribute 3': 'Value 3'}}]})

    def test_deploy_info_multiple_deployment_paths(self):

        deployment_path = Mock()
        deployment_path.Name = 'Deployment Path Name'
        deployment_path.IsDefault = True

        deployment_service = Mock()
        deployment_service.Name = 'Deployment Service Name'
        deployment_service.Attributes = []

        deployment_path.DeploymentService = deployment_service

        deployment_path2 = Mock()
        deployment_path2.Name = 'Deployment Path Name 2'
        deployment_path2.IsDefault = False

        deployment_service2 = Mock()
        deployment_service2.Name = 'Deployment Service Name 2'
        deployment_service2.Attributes = []

        deployment_path2.DeploymentService = deployment_service2


        deployment_paths = [deployment_path, deployment_path2]

        info_block = DeployInfo(deployment_paths)
        self.assertEquals(info_block, {'deploypaths': [{'is_default': True,
                                                        'service_name': 'Deployment Service Name',
                                                        'name': 'Deployment Path Name',
                                                        'attributes': {}},
                                                       {'is_default': False,
                                                        'service_name': 'Deployment Service Name 2',
                                                        'name': 'Deployment Path Name 2',
                                                        'attributes': {}}]})


if __name__ == '__main__':
    unittest.main()
