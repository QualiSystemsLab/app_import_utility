from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.helpers.save_workflow.save_app_info_orch import save_app_deployment_info


sandbox = Sandbox()
DefaultSetupWorkflow().register(sandbox)
sandbox.workflow.add_to_preparation(save_app_deployment_info, None)
sandbox.execute_setup()
