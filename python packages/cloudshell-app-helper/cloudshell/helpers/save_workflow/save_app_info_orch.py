import json

from cloudshell.api.cloudshell_api import SandboxDataKeyValue
from cloudshell.helpers.save_workflow.deploy_info import DeployInfo


def save_app_deployment_info(sandbox, components=None):
    for app in sandbox.automation_api.GetReservationDetails(sandbox.id).ReservationDescription.Apps:
        serialized_deployment_info = json.dumps(DeployInfo(app.DeploymentPaths))

        key_value = SandboxDataKeyValue(app.Name, serialized_deployment_info)

        sandbox.automation_api.SetSandboxData(sandbox.id, [key_value])
