import unittest
from mock import patch, Mock, call
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.helpers.save_workflow.save_app_info_orch import save_app_deployment_info


class SaveAppInfoTests(unittest.TestCase):

    @patch('cloudshell.api.cloudshell_api.CloudShellAPISession')
    def test_save_app_info_no_app(self, mock_api):

        reservation_details_mock = Mock()
        reservation_description_mock = Mock()
        reservation_description_mock.Apps = []

        reservation_details_mock.ReservationDescription = reservation_description_mock

        mock_api.return_value.GetReservationDetails = Mock(return_value=reservation_details_mock)

        sandbox_mock = Mock()
        sandbox_mock.automation_api = mock_api

        save_app_deployment_info(sandbox_mock)

        mock_api.SetSandboxData.assert_not_called()

    @patch('json.dumps')
    @patch('cloudshell.helpers.save_workflow.deploy_info.DeployInfo.__init__')
    @patch('cloudshell.api.cloudshell_api.CloudShellAPISession')
    def test_save_app_info_with_app(self, mock_api, mock_deploy_info, mock_json):
        reservation_details_mock = Mock()
        reservation_description_mock = Mock()

        reservation_app = Mock()
        reservation_app.DeploymentPaths = 'Test'
        reservation_app.Name = 'Test App'

        reservation_description_mock.Apps = [reservation_app]

        reservation_details_mock.ReservationDescription = reservation_description_mock

        mock_api.GetReservationDetails = lambda x: reservation_details_mock

        sandbox_mock = Mock()
        sandbox_mock.automation_api = mock_api

        mock_deploy_info.return_value = None
        mock_json.return_value = 'Test json'

        save_app_deployment_info(sandbox_mock)

        mock_api.SetSandboxData.assert_called()

    @patch('json.dumps')
    @patch('cloudshell.helpers.save_workflow.deploy_info.DeployInfo.__init__')
    @patch('cloudshell.api.cloudshell_api.CloudShellAPISession')
    def test_save_app_info_with_multiple_app(self, mock_api, mock_deploy_info, mock_json):
        reservation_details_mock = Mock()
        reservation_description_mock = Mock()

        reservation_app = Mock()
        reservation_app.DeploymentPaths = 'Test'
        reservation_app.Name = 'Test App'

        reservation_description_mock.Apps = [reservation_app, reservation_app, reservation_app]

        reservation_details_mock.ReservationDescription = reservation_description_mock

        mock_api.GetReservationDetails = lambda x: reservation_details_mock

        sandbox_mock = Mock()
        sandbox_mock.automation_api = mock_api

        mock_deploy_info.return_value = None
        mock_json.return_value = 'Test json'

        save_app_deployment_info(sandbox_mock)

        self.assertEquals(mock_api.SetSandboxData.call_count, 3)


if __name__ == '__main__':
    unittest.main()