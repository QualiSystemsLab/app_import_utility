# Utility Usage Guide

## Setup Script

The Setup script contained in this repo will simply extend the CloudShell default Sandbox Setup to support App Save/Save As.
You can add the same support to your own custom setup by the next steps.
* In your scripts requirements.txt add:
```
cloudshell-app-helper
```
* In your scripts main.py import 'save_app_deployment_info'.
* The 'add_to_preparation' line needs to go somewhere between registering the sandbox and executing the setup:
```
from cloudshell.helpers.save_workflow.save_app_info_orch import save_app_deployment_info


sandbox = Sandbox()
DefaultSetupWorkflow().register(sandbox)

sandbox.workflow.add_to_preparation(save_app_deployment_info, None)

sandbox.execute_setup()
```

## Orchestration Scripts: Which ones do I need?

There are 4 different default resource scripts that can be utilized. Each can help support a different App Development Flow.

You should only use the scripts that fit your expected flow.

* SaveAppTemplate
    * Updates the base App Template from which the Deployed App was created.
        * Will create a new VM Image/Template/etc... on the Cloud Provider for this App Template
        * Will update any changes to the deployed app's attributes

* SaveAsAppTemplate
    * Creates a new App Template
        * Will create a new VM Image/Template/etc... on the Cloud Provider for this App Template
        * Will save the deployed app's current attributes

* SaveAppAttributes
    * Updates the base App Template from which the Deployed App was created.
        * Does not create a new VM Image/Template/etc... on the Cloud Provider for this App Template
        * Will ONLY update any changes to the deployed app's attributes

* SaveAsAppAttributes
    * Creates a new App Template
        * Does not create a new VM Image/Template/etc... on the Cloud Provider for this App Template
        * Will save the deployed app's current attributes



