import tempfile
import os
import zipfile
import requests
import shutil
import base64

from cloudshell.helpers.app_import.images import vm_image


def upload_app_to_cloudshell(app_name, app_xml_content, server, user="admin", password="admin",
                             display_image_result="", display_image_name='vm.png'):
    """
    :param CloudShellAPISession cs_api:
    :param string reservation_id:
    :param string app_name:
    :param string app_xml_content:
    :param string server:
    :param string user:
    :param string password:
    :param image display_image_result
    :param string display_image_name
    :return:
    """
    metadata = """<?xml version="1.0" encoding="utf-8"?>
<Metadata xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.qualisystems.com/PackageMetadataSchema.xsd">
<CreationDate>9/13/2019 4:45:59 PM</CreationDate>
<ServerVersion>9.2.0</ServerVersion>
<PackageType>CloudShellPackage</PackageType>
</Metadata>
    """

    # script_working_dir = os.path.dirname(os.path.abspath(__file__))
    working_dir = tempfile.mkdtemp()
    app_template_file = os.path.join(working_dir, app_name)
    blueprint_zip_file = os.path.join(working_dir, "Blueprint.zip")
    display_image_file = os.path.join(working_dir, display_image_name)

    metadata_file = os.path.join(working_dir, "metadata.xml")
    with open(app_template_file, "w") as app_xml:
        app_xml.write(app_xml_content)

    if os.path.exists(blueprint_zip_file):
        os.remove(blueprint_zip_file)

    if os.path.exists(display_image_file):
        os.remove(display_image_file)

    fh = open(display_image_file, "wb")
    if not display_image_result:
        fh.write(base64.b64decode(display_image_result))
    else:
        fh.write(base64.b64decode(vm_image))
    fh.close()

    zip_file = zipfile.ZipFile(blueprint_zip_file, "w")
    zip_file.write(app_template_file, arcname=os.path.join("App Templates", "{}.xml".format(app_name)))

    zip_file.write(display_image_file, arcname=os.path.join("App Templates", "{}".format(display_image_name)))

    open(metadata_file, "w").write(metadata)
    zip_file.write(metadata_file, arcname="metadata.xml")
    zip_file.close()
    zip_content = open(blueprint_zip_file, "rb").read()
    shutil.rmtree(working_dir)

    server_url = "http://{}:9000/Api/Auth/Login".format(server)

    login_response = requests.put(server_url,
                                  data={"username": user, "password": password, "domain": "Global"})
    if not login_response.ok:
        raise Exception(f"Failed login to Quali API trying to import App Package.\n"
                        f"Status Code: {login_response.status_code}. Reason: {login_response.reason}")
    token = login_response.text[1:-1]
    upload_response = requests.post("http://{}:9000/API/Package/ImportPackage".format(server),
                                    headers={"Authorization": f"Basic {token}"},
                                    files={"QualiPackage": zip_content})
    if not upload_response.ok:
        raise Exception("Failed upload of app XML into cloudshell.\n"
                        f"Status Code: {upload_response.status_code}, Reason: {upload_response.reason}")
    if 'false' in upload_response.text.lower():
        raise Exception('Issue importing App XML into Cloudshell: ' + upload_response.text)

    return upload_response.text
