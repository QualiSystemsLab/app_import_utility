import json

from cloudshell.api.cloudshell_api import SandboxDataKeyValue


def create_json_string(deployment_paths):
    result = dict()
    result['deploypaths'] = []
    for deploypath in deployment_paths:
        path = dict()
        path['name'] = deploypath.Name
        path['is_default'] = deploypath.IsDefault
        path['service_name'] = deploypath.DeploymentService.Name
        path['attributes'] = dict()
        for attribute in deploypath.DeploymentService.Attributes:
            path['attributes'][attribute.Name] = attribute.Value
        result['deploypaths'].append(path)

    return json.dumps(result)


def save_app_deployment_info(sandbox, components=None):
    for app in sandbox.automation_api.GetReservationDetails(sandbox.id).ReservationDescription.Apps:
        jsonstring = create_json_string(app.DeploymentPaths)

        key_value = SandboxDataKeyValue(app.Name, jsonstring)

        sandbox.automation_api.SetSandboxData(sandbox.id, [key_value])