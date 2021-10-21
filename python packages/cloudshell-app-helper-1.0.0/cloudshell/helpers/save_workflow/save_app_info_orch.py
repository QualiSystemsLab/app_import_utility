import json

from cloudshell.api.cloudshell_api import SandboxDataKeyValue, CloudShellAPISession
from cloudshell.helpers.save_workflow.deploy_info import DeployInfo


def save_app_deployment_info(api: CloudShellAPISession, sandbox_id: str):
    for app in api.GetReservationDetails(sandbox_id).ReservationDescription.Apps:
        serialized_deployment_info = json.dumps(DeployInfo(app.DeploymentPaths))

        key_value = SandboxDataKeyValue(app.Name, serialized_deployment_info)

        api.SetSandboxData(sandbox_id, [key_value])
