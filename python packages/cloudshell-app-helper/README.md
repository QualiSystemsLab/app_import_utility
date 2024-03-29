# cloudshell-app-helper
## File Location: cloudshell/helpers/app_import, cloudshell/helpers/save_workflow

* **save_app_info_orch.py**
    * save_app_deployment_info
        * Creates a 'DeployInfo' object of deployment info for each App in a Sandbox and saves each to the Sandbox Data

* **deploy_info.py**
    * DeployInfo
        * Serializable Data structure to hold the app templated deployment info and is passed to the Sandbox Data

* **save_app_utility.py**
    * save_flow
        * Will verify that deployment info for this app was saved to the Sandbox Data
        * Will verify that a display image can be gathered from url or existing template, uses default image if not
        * Attempts to run the hidden 'save_app' command from the cloud provider.
        * Gather deployed app attributes
        * Create the App XML and upload

    * save_flow_just_app
        * Will verify that deployment info for this app was saved to the Sandbox Data
        * Will verify that a display image can be gathered from url or existing template, uses default image if not
        * Gather deployed app attributes
        * Create the App XML and upload

* **build_app_xml.py**
    * app_template
        * Takes app deployment info, app resource info and cloud provider info as input
        * Returns the formatted app xml

* **upload_app_xml.py**
    * upload_app_to_cloudshell
        * Creates a full blueprint package with the app xml within
        * Utilizes Quali API to upload the package