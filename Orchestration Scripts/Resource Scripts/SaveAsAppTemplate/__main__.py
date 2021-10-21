from cloudshell.helpers.scripts import cloudshell_scripts_helpers as helpers
from cloudshell.helpers.save_workflow.save_app_utility import SaveAppUtility
import os

NEW_APP_PARAM = "NEWAPPNAME"
IMAGE_URL_PARAM = "DISPLAYIMAGEURL"


def save_app():
    connectivity = helpers.get_connectivity_context_details()
    resource = helpers.get_resource_context_details()
    reservation_details = helpers.get_reservation_context_details()
    sandbox_id = reservation_details.id
    api = helpers.get_api_session()

    new_app_name = os.environ.get(NEW_APP_PARAM, "")
    image_url = os.environ.get(IMAGE_URL_PARAM, "")

    app_utility = SaveAppUtility(api, sandbox_id, resource.name, connectivity.server_address, connectivity.admin_user,
                                 connectivity.admin_pass, image_url, new_app_name, save_as=True)
    saved_app_info = app_utility.save_flow()
    print(saved_app_info)


if __name__ == "__main__":
    save_app()
