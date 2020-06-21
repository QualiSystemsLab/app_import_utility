# Script's Functions

* Setup Scripts
    * **AppSaveSetup**
        * This setup script will save the App deployment information that is needed by the resource scripts to the SandboxData
        * It will still complete the other steps in the default setup

* Resource Scripts
    * **SaveAppTemplate**
        * This resource script will overwrite an existing App Template with the current state of the Deployed App
            * This will create a new VM Image that the App is deploying
            * This will also overwrite any changes to the Deployed App's attributes
    * **SaveAsAppTemplate**
        * This resource script will create a new App Template with the current state of the Deployed App
            * The name of this new App Template will be the required input parameter 'NewAppName'
            * This will create a new VM Image that the App is deploying
            * This will also overwrite any changes to the Deployed App's attributes
    * **SaveAppAttributes**
        * This resource script will partially overwrite an existing App Template with the current state of the Deployed App
            * This will ONLY overwrite any changes to the Deployed App's attributes
    * **SaveAsAppAttributes**
        * This resource script will create a new App Template with the current state of the Deployed App
            * This will ONLY overwrite any changes to the Deployed App's attributes
            * Will copy over the same deployment path as the Deployed App


# Deeper Dive: cloudshell-app-helper usage

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