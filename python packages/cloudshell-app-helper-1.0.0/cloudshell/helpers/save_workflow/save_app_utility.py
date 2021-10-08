import os
import json
import requests
from timeit import default_timer

from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.helpers.app_import.build_app_xml import app_template
from cloudshell.helpers.app_import.upload_app_xml import upload_app_to_cloudshell

# what I currently see in latest AWS and OCI 2G shells
CP_2G_CREATE_IMAGE_COMMAND = "save_app"
AWS_DEPLOY_PARAM_KEY = "AWS AMI Id"


class SaveAppUtility:
    def __init__(self, api: CloudShellAPISession, reservation_id: str, resource_name: str, server_address: str,
                 admin_user: str, admin_password: str, display_image_url='', new_app_name='', save_as=False,
                 revertNum=1):
        self.api = api
        self.reservation_id = reservation_id
        self.resource_name = resource_name
        self.revertNum = revertNum
        self.app_name = ''
        self.AppTemplateName = ''
        self.new_app_name = ''

        self.api_missing = False

        for vm in self.api.GetReservationDetails(self.reservation_id).ReservationDescription.Resources:
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
            raise Exception(
                "Could not locate Sandbox information on {}, App must be deployed by Setup script to use this functionality.\n".format(
                    self.resource_name))

        self.get_display_image()

    def get_deployment_info(self):
        for keyValue in self.api.GetSandboxData(self.reservation_id).SandboxDataKeyValues:
            if keyValue.Key == self.app_name:
                self.deploy_info = json.loads(keyValue.Value)
                break

    def get_display_image(self):
        self.display_image_result = self.api.GetReservationAppImage(self.reservation_id,
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
        command_search = [x.Name for x in self.api.GetResourceConnectedCommands(self.resource_name).Commands
                          if x.Name == CP_2G_CREATE_IMAGE_COMMAND]

        if not command_search:
            exc_msg = (f"Operation not supported by Cloud Provider\n"
                       f"Command f{CP_2G_CREATE_IMAGE_COMMAND} not found on resource {self.resource_name}")
            raise Exception(exc_msg)

        if delete:
            inputs = ['True', self.new_app_name, str(self.revertNum)]
        else:
            inputs = ['False', self.new_app_name, str(self.revertNum)]

        save_msg = f"Saving new AMI on AWS for app '{self.resource_name}'. This may take a few minutes..."
        self.api.WriteMessageToReservationOutput(self.reservation_id, save_msg)
        start_timer = default_timer()
        try:
            save_response = self.api.ExecuteResourceConnectedCommand(self.reservation_id,
                                                                     self.resource_name,
                                                                     CP_2G_CREATE_IMAGE_COMMAND,
                                                                     'connectivity').Output
        except Exception as e:
            exc_msg = f"Issue saving app {self.resource_name}. {type(e).__name__}: {str(e)}"
            raise Exception(exc_msg)
        total_seconds = default_timer() - start_timer
        success_msg = f"Finished saving AMI in {total_seconds:.2f} seconds:\n{save_response}"
        self.api.WriteMessageToReservationOutput(self.reservation_id, success_msg)
        self.saved_app_info = json.loads(save_response)

    def revert_app_info(self):
        command = [x.Name for x in self.api.GetResourceConnectedCommands(self.resource_name).Commands
                   if x.Name == 'revert_app_image']

        inputs = [self.new_app_name]

        if len(command) == 1:
            self.saved_app_info = json.loads(self.api.ExecuteResourceConnectedCommand(self.reservation_id,
                                                                                      self.resource_name,
                                                                                      'revert_app_image',
                                                                                      'connectivity',
                                                                                      inputs).Output)
        else:
            raise Exception("Operation not supported by Cloud Provider\n")

    def create_app_xml(self):
        self.api.WriteMessageToReservationOutput(self.reservation_id, "Creating new app template...")
        resource = self.api.GetResourceDetails(self.resource_name)

        app_attributes = dict()
        for attr in resource.ResourceAttributes:
            app_attributes[attr.Name] = attr.Value

        app_categories = ['Applications']

        if self.saved_app_info:
            for deploy_path in self.deploy_info['deploypaths']:
                if not deploy_path['is_default']:
                    continue
                service_name = deploy_path["service_name"]
                for key, value in self.saved_app_info.items():
                    # patch for AWS
                    if "AWS" in key:
                        if "2G" in service_name:
                            deploy_path["attributes"][f"{service_name}.{AWS_DEPLOY_PARAM_KEY}"] = value
                        else:
                            deploy_path['attributes'][AWS_DEPLOY_PARAM_KEY] = value
                    else:
                        deploy_path['attributes'][key] = value

        self.app_xml = app_template(self.new_app_name, self.deploy_info['deploypaths'], app_categories, app_attributes,
                                    resource.ResourceModelName, resource.DriverName,
                                    resource.VmDetails.CloudProviderFullName, self.display_image_name)

    def upload_app(self):
        self.api.WriteMessageToReservationOutput(self.reservation_id, "Uploading app template to Cloudshell...")
        result = upload_app_to_cloudshell(self.new_app_name, self.app_xml,
                                          self.server_address, self.admin_user, self.admin_password,
                                          self.display_image_result, self.display_image_name)
        succes_msg = (f"App '{self.new_app_name}' has been updated from instance '{self.resource_name}'\n"
                      f"Upload Response: {result}")
        self.api.WriteMessageToReservationOutput(self.reservation_id, succes_msg)

    def save_flow(self, delete=False):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.save_app_info(delete)  # what is delete for?
            self.create_app_xml()
            self.upload_app()
            if delete:
                self.api.RefreshAppInBlueprints(self.AppTemplateName)
            return self.saved_app_info

    def save_flow_just_app(self, update=False):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.create_app_xml()
            self.upload_app()
            if update:
                self.api.RefreshAppInBlueprints(self.AppTemplateName)

    def revert_flow(self):
        if not self.api_missing:
            self.verify_deploy_info_and_display_image()
            self.revert_app_info()
            self.create_app_xml()
            self.upload_app()
            self.api.RefreshAppInBlueprints(self.AppTemplateName)
