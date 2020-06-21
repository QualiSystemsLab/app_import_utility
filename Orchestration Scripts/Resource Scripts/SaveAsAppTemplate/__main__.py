from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.helpers.save_workflow.save_app_utility import SaveAppUtility

import os


def save_app():
    sandbox = Sandbox()
    connectivity = helpers.get_connectivity_context_details()
    resource = helpers.get_resource_context_details()

    if 'NEWAPPNAME' in os.environ:
        new_app_name = os.environ['NEWAPPNAME']
    else:
        new_app_name = ''

    if 'DISPLAYIMAGEURL' in os.environ:
        image_url = os.environ['DISPLAYIMAGEURL']
    else:
        image_url = ''

    apputility = SaveAppUtility(sandbox, resource.name, connectivity.server_address, connectivity.admin_user,
                                connectivity.admin_pass, image_url, new_app_name, save_as=True)
    apputility.save_flow()


if __name__ == "__main__":
    save_app()
