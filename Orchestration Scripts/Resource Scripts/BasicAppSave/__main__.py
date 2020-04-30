from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.helpers.apps.save_app_utility import SaveAppUtility

import os
import re


def save_app():
    sandbox = Sandbox()
    connectivity = helpers.get_connectivity_context_details()
    resource = helpers.get_resource_context_details()
    image_url = os.environ['DISPLAYIMAGEURL']

    if re.match('(.* ([a-z]|[0-9]){10})', resource.name):
        app_name = ' '.join(resource.name.split(' ')[:-1])
    else:
        app_name = resource.name

    apputility = SaveAppUtility(sandbox, resource.name, app_name, connectivity.server_address, connectivity.admin_user,
                               connectivity.admin_pass, image_url)
    apputility.save_flow()


if __name__ == "__main__":
    save_app()
