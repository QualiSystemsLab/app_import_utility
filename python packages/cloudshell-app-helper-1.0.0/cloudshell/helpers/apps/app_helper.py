import os
import json
import requests

from cloudshell.api.cloudshell_api import SandboxDataKeyValue

from build_app_xml import app_template
from upload_app_xml import upload_app_to_cloudshell


def create_json_string(deployment_paths):
    result = dict()
    result['deploypaths'] = []
    for deploypath in deployment_paths:
        path = dict()
        path['name'] = deploypath.Name
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


class AppHelper:
    def __init__(self, sandbox, resource_name, app_name, server_address, admin_user, admin_password, image_url='', new_app_name=''):
        self.sandbox = sandbox
        self.resource_name = resource_name
        self.app_name = app_name
        self.server_address = server_address
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.image_name = 'vm.png'
        self.image_url = image_url

        if new_app_name == '':
            self.new_app_name = app_name
        else:
            self.new_app_name = new_app_name

        self.image_result = None
        self.deploy_info = None
        self.saved_app_info = None
        self.app_xml = None

    def initialize(self):
        self.get_deployment_info()
        if self.deploy_info is None:
            raise Exception("Could not locate Sandbox information on {}, App must be deployed by Setup script to use this functionality.\n".format(self.resource_name))

        self.get_image_from_url()

    def get_deployment_info(self):
        for keyValue in self.sandbox.automation_api.GetSandboxData(self.sandbox.id).SandboxDataKeyValues:
            if keyValue.Key == self.app_name:
                self.deploy_info = json.loads(keyValue.Value)
                break

    def get_image_from_url(self):
        if self.image_url != '':
            try:
                self.image_result = requests.get(self.image_url, allow_redirects=True).content
                self.image_name = os.path.basename(self.image_url)
            except Exception:
                self.sandbox.automation_api.WriteMessageToReservationOutput(self.sandbox.id,
                                                                            'Issue downloading from Image URL... Using Default Image.')
                self.image_result = None
                self.image_name = 'vm.png'

    def save_app_info(self):
        command = [x.Name for x in self.sandbox.automation_api.GetResourceConnectedCommands(self.resource_name).Commands
                   if x.Name == 'save_app']

        if len(command) == 1:
            self.saved_app_info = json.loads(self.sandbox.automation_api.ExecuteResourceConnectedCommand(self.sandbox.id,
                                                                                                         self.resource_name,
                                                                                                         'save_app',
                                                                                                         'connectivity',
                                                                                                         []).Output)
        else:
            raise Exception("Operation not supported by Cloud Provider\n")

    def create_app_xml(self):
        resource = self.sandbox.automation_api.GetResourceDetails(self.resource_name)

        app_attributes = dict()
        for attr in resource.ResourceAttributes:
            app_attributes[attr.Name] = attr.Value

        app_categories = ['Applications']
        deploy_attributes = self.deploy_info['deploypaths'][0]['attributes']
        deploy_name = self.deploy_info['deploypaths'][0]['name']
        deploy_service_name = self.deploy_info['deploypaths'][0]['service_name']

        if self.saved_app_info is not None:
            for key, value in self.saved_app_info.iteritems():
                deploy_attributes[key] = value

        self.app_xml = app_template(self.new_app_name, deploy_name, deploy_service_name, app_categories, app_attributes,
                                    resource.ResourceModelName, resource.DriverName, deploy_attributes,
                                    resource.VmDetails.CloudProviderFullName, self.image_name)

    def upload_app_to_cloudshell(self):
        result = upload_app_to_cloudshell(self.sandbox.automation_api, self.sandbox.id, self.new_app_name, self.app_xml,
                                          self.server_address, self.admin_user, self.admin_password, self.image_result, self.image_name)
        if result is None:
            self.sandbox.automation_api.WriteMessageToReservationOutput(self.sandbox.id,
                                                                        "App '{}' has been updated from instance '{}'\n".format(self.new_app_name, self.resource_name))
        else:
            raise Exception("Error uploading App to CloudShell\n{}".format(result))

    def save_flow(self):
        self.initialize()
        self.save_app_info()
        self.create_app_xml()
        self.upload_app_to_cloudshell()

    def save_flow_just_app(self):
        self.initialize()
        self.create_app_xml()
        self.upload_app_to_cloudshell()
