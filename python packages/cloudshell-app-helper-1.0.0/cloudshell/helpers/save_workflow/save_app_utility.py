import os
import json
import requests

from cloudshell.helpers.app_import.build_app_xml import app_template
from cloudshell.helpers.app_import.upload_app_xml import upload_app_to_cloudshell
from cloudshell.api.cloudshell_api import InputNameValue


class SaveAppUtility:
    def __init__(self, sandbox, resource_name, server_address, admin_user, admin_password, display_image_url='', new_app_name='', save_as=False):
        self.sandbox = sandbox
        self.resource_name = resource_name
        self.app_name = ''
        self.AppTemplateName = ''
        self.new_app_name = ''

        self.api_missing = False

        for vm in self.sandbox.automation_api.GetReservationDetails(self.sandbox.id).ReservationDescription.Resources:
            if vm.Name == self.resource_name:
                self.app_name = vm.AppDetails.AppName
                try:
                    self.AppTemplateName = vm.AppTemplateName
                    if new_app_name == '':
                        if save_as:
                            if self.app_name == self.AppTemplateName:
                                self.api_missing = True
                            else:
                                self.new_app_name = self.app_name
                        else:
                            self.new_app_name = self.AppTemplateName
                    else:
                        self.new_app_name = new_app_name
                except Exception as e:
                    self.new_app_name = self.app_name
                if self.api_missing:
                    raise Exception("Stopping Save As because App's name was not changed prior to deployment.\n"
                                    "Use the 'NewAppName' custom attribute on the command to override.")

        self.server_address = server_address
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.display_image_name = 'vm.png'
        self.display_image_url = display_image_url

        self.display_image_result = None
        self.deploy_info = None
        self.saved_app_info = None
        self.app_xml = None

    def verify_deploy_info_and_display_image(self):
        self.get_deployment_info()
        if self.deploy_info is None:
            raise Exception("Could not locate Sandbox information on {}, App must be deployed by Setup script to use this functionality.\n".format(self.resource_name))

        self.get_display_image()

    def get_deployment_info(self):
        for keyValue in self.sandbox.automation_api.GetSandboxData(self.sandbox.id).SandboxDataKeyValues:
            if keyValue.Key == self.app_name:
                self.deploy_info = json.loads(keyValue.Value)
                break

    def get_display_image(self):
        self.display_image_result = self.sandbox.automation_api.GetReservationAppImage(self.sandbox.id,
                                                                                       self.resource_name).AppTemplateImage

        if self.display_image_result == '':
            try:
                if self.display_image_url != '':
                    self.display_image_result = requests.get(self.display_image_url, allow_redirects=True).content
                    self.display_image_name = os.path.basename(self.display_image_url)
                else:
                    self.display_image_result = None
                    self.display_image_name = 'vm.png'
            except:
                self.display_image_result = None
                self.display_image_name = 'vm.png'

    def save_app_info(self, delete):
        command = [x.Name for x in self.sandbox.automation_api.GetResourceConnectedCommands(self.resource_name).Commands
                   if x.Name == 'create_app_image']

        if len(command) == 1:
            if delete:
                inputs = [InputNameValue(name='delete_old_image', value='True'),
                          InputNameValue(name='app_template_name', value=self.AppTemplateName)]
            else:
                inputs = [InputNameValue(name='delete_old_image', value='False'),
                          InputNameValue(name='app_template_name', value=self.AppTemplateName)]
            self.saved_app_info = json.loads(self.sandbox.automation_api.ExecuteResourceConnectedCommand(self.sandbox.id,
                                                                                                         self.resource_name,
                                                                                                         'create_app_image',
                                                                                                         'connectivity',
                                                                                                         inputs).Output)
        else:
            raise Exception("Operation not supported by Cloud Provider\n")

    def revert_app_info(self):
        command = [x.Name for x in self.sandbox.automation_api.GetResourceConnectedCommands(self.resource_name).Commands
                   if x.Name == 'revert_app_image']

        inputs = [InputNameValue(name='app_template_name', value=self.AppTemplateName)]

        if len(command) == 1:
            self.saved_app_info = json.loads(self.sandbox.automation_api.ExecuteResourceConnectedCommand(self.sandbox.id,
                                                                                                         self.resource_name,
                                                                                                         'revert_app_image',
                                                                                                         'connectivity',
                                                                                                         inputs).Output)
        else:
            raise Exception("Operation not supported by Cloud Provider\n")

    def create_app_xml(self):
        resource = self.sandbox.automation_api.GetResourceDetails(self.resource_name)

        app_attributes = dict()
        for attr in resource.ResourceAttributes:
            app_attributes[attr.Name] = attr.Value

        app_categories = ['Applications']

        if self.saved_app_info is not None:
            for deploy_path in self.deploy_info['deploypaths']:
                if deploy_path['is_default']:
                    for key, value in self.saved_app_info.iteritems():
                        # patch for AWS
                        if 'AWS' in key:
                            deploy_path['attributes']['AWS AMI Id'] = value
                        else:
                            deploy_path['attributes'][key] = value

        self.app_xml = app_template(self.new_app_name, self.deploy_info['deploypaths'], app_categories, app_attributes,
                                    resource.ResourceModelName, resource.DriverName,
                                    resource.VmDetails.CloudProviderFullName, self.display_image_name)

    def upload_app(self):
        result = upload_app_to_cloudshell(self.sandbox.automation_api, self.sandbox.id, self.new_app_name, self.app_xml,
                                          self.server_address, self.admin_user, self.admin_password, self.display_image_result, self.display_image_name)
        if result is None:
            self.sandbox.automation_api.WriteMessageToReservationOutput(self.sandbox.id,
                                                                        "App '{}' has been updated from instance '{}'\n".format(self.new_app_name, self.resource_name))
        else:
            raise Exception("Error uploading App to CloudShell\n{}".format(result))

    def save_flow(self, delete=False):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.save_app_info(delete)
            self.create_app_xml()
            self.upload_app()
            if delete:
                self.sandbox.automation_api.RefreshAppInBlueprints(self.AppTemplateName)

    def save_flow_just_app(self, update=False):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.create_app_xml()
            self.upload_app()
            if update:
                self.sandbox.automation_api.RefreshAppInBlueprints(self.AppTemplateName)

    def revert_flow(self):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.revert_app_info()
            self.create_app_xml()
            self.upload_app()
            self.sandbox.automation_api.RefreshAppInBlueprints(self.AppTemplateName)
