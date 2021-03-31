import tempfile
import os
import zipfile
import requests
import shutil

from images import vm_image


def upload_app_to_cloudshell(cs_api, reservation_id, app_name, app_xml_content, server, user="admin", password="admin",
                             display_image_result=None, display_image_name='vm.png'):
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
    if display_image_result is not None:
        fh.write(display_image_result.decode('base64'))
    else:
        fh.write(vm_image.decode('base64'))
    fh.close()

    zip_file = zipfile.ZipFile(blueprint_zip_file, "w")
    zip_file.write(app_template_file, arcname=os.path.join("App Templates", "{}.xml".format(app_name)))

    zip_file.write(display_image_file, arcname=os.path.join("App Templates", "{}".format(display_image_name)))

    open(metadata_file, "w").write(metadata)
    zip_file.write(metadata_file, arcname="metadata.xml")
    zip_file.close()
    zip_content = open(blueprint_zip_file, "rb").read()
    shutil.rmtree(working_dir)
    authentication_code = requests.put("http://{}:9000/Api/Auth/Login".format(server),
                                       {"username": user, "password": password, "domain": "Global"}).content

    result = requests.post("http://{}:9000/API/Package/ImportPackage".format(server),
                           headers={"Authorization": "Basic {}".format(authentication_code[1:-1])},
                           files={"QualiPackage": zip_content})
    if 'false' in result.content:
        raise Exception('Issue importing App XML into Cloudshell: ' + result.content)
    if result.status_code >= 300:
        return result.content
    else:
        return None
