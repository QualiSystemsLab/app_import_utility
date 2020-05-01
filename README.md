# app_import_utility

This repo contains a python package, CloudShell resource scripts and orchestration scripts to assist with Save/Save As operations on Apps in a Sandbox.


## Getting Started

1. Ensure that the latest OCI Shell is installed, this latest release will have the 'save_app' function that is used by the scripts
2. Package and load into CloudShell the Setup Script, Resource Scripts, and deployment Orchestrator. Make sure you overwrite the existing deployment orchestrator.
3. Add 'DisplayImageURL' custom parameter to all resource scripts. Add 'NewAppName' custom parameter to the 2 'SaveAs' resource Scripts.
4. Add the 4 Resource Scripts to the model of your choice, default should be 'Generic App Model'.
5. Create a new Sandbox or edit an existing one to use the new setup script.
6. Once an App is deployed using this setup script, it should have 4 additional command options functional.
7. Reach out to Danny Yeager for any assistance if encountering errors.


## Script's Functions

* Setup Scripts
    * AppSaveSetup
        * This setup script will save the App deployment information that is needed by the resource scripts to the SandboxData
        * It will still complete the other steps in the default setup

* Resource Scripts
    * **BasicAppSave**
        * This resource script will overwrite an existing App Template with the current state of the Deployed App
            * This will create a new OCI Image that the App is deploying
            * This will also overwrite any changes to the Deployed App's attributes
    * **BasicAppSaveAs**
        * This resource script will create a new App Template with the current state of the Deployed App
            * The name of this new App Template will be the required input parameter 'NewAppName'
            * This will create a new OCI Image that the App is deploying
            * This will also overwrite any changes to the Deployed App's attributes
    * **BasicJustAppSave**
        * This resource script will partially overwrite an existing App Template with the current state of the Deployed App
            * This will ONLY overwrite any changes to the Deployed App's attributes
    * **BasicJustAppSaveAs**
        * This resource script will create a new App Template with the current state of the Deployed App
            * This will ONLY overwrite any changes to the Deployed App's attributes
            * Will copy over the same deployment path as the Deployed App


# Deeper Dive


## Script's usage of python package

* Setup Scripts
    * AppSaveSetup
        * Runs the orch helper funtion, save_app_deployment_info, from save_app_info_orch_helper.py during setup

* Resource Scripts
    * Similarities
        * All Resource Scripts will have a optional custom parameter 'DisplayImageURL' for the App's icon. Default image if empty.
        * All Resource Scripts will try to get the App's name by removing the id #'s from the VM Resource Name.
            * Save operations on an App whose name was changed in the Blueprint or Sandbox will create a new App instead of overwrite.
        * All Resource Scripts will create an instance of the 'SaveAppUtility' class from save_app_utility.py

    * BasicAppSave
        * Will run the 'save_flow' method on the 'SaveAppUtility'
    * BasicAppSaveAs
        * Will have a required custom parameter 'NewAppName' which will be the newly created App's name
        * 'NewAppName' input is additional a parameter for the 'SaveAppUtility' init
        * Will run the 'save_flow' method on the 'SaveAppUtility'
    * BasicJustAppSave
        * Will run the 'save_flow_just_app' method on the 'SaveAppUtility'
    * BasicJustAppSaveAs
        * Will have a required custom parameter 'NewAppName' which will be the newly created App's name
        * 'NewAppName' input is additional a parameter for the 'SaveAppUtility' init
        * Will run the 'save_flow_just_app' method on the 'SaveAppUtility'


## Python Package
### File Location: cloudshell/helpers/apps

* **save_app_info_orch_helper.py**
    * save_app_deployment_info
        * Creates a dictionary of deployment info for each App in a Sandbox and saves each to the Sandbox Data

* **save_app_utility.py**
    * save_flow
        * Will verify that deployment info for this app was saved to the Sandbox Data
        * Will verify that the DisplayImageURL can be resolved, uses default image if not
        * Attempts to run the hidden 'save_app' command. For OCI this will create a new image
        * Gather deployed app attributes
        * Create the App XML and upload
    
    * save_flow_just_app
        * Will verify that deployment info for this app was saved to the Sandbox Data
        * Will verify that the DisplayImageURL can be resolved, uses default image if not
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


## License
[Apache License 2.0](https://github.com/QualiSystemsLab/app_import_utility/blob/master/LICENSE)
