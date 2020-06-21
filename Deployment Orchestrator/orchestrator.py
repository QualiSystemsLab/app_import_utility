import json

from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.api.cloudshell_api import SandboxDataKeyValue
from cloudshell.api.cloudshell_api import InputNameValue, AppConfiguration
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.helpers.save_workflow.deploy_info import DeployInfo

from auto_events import AutoEvents


class DeployAppOrchestrationDriver(object):
    NO_DRIVER_ERR = "129"
    DRIVER_FUNCTION_ERROR = "151"

    def __init__(self):
        pass
    
    def deploy(self, context):
        """
        Deploys app from template
        :type context: cloudshell.shell.core.context.ResourceCommandContext
        """
        logger = self._get_logger(context)

        reservation_id = context.reservation.reservation_id
        resource_details = context.resource
        app_name = resource_details.name
        app_data = json.loads(resource_details.app_context.app_request_json)
        deployment_service = app_data["deploymentService"]
        deployment_attributes = deployment_service["attributes"]
        deployment_service_name = deployment_service["name"]

        # init auto events
        events = AutoEvents(deployment_attributes)

        # Start api session
        session = self._get_cloudshell_api(context, logger)

        # Create Sandbox Data for App Save/Save As
        app_resource_info = session.GetAppsDetailsInReservation(reservation_id, [app_name]).Apps[0]

        serialized_deployment_info = json.dumps(DeployInfo(app_resource_info.DeploymentPaths))
        key_value = SandboxDataKeyValue(app_resource_info.Name, serialized_deployment_info)
        session.SetSandboxData(reservation_id, [key_value])
        # End Block for App Save/Save As

        self._write_message(app_name, reservation_id, session, 'deployment started')
        deployment_result = self._deploy_app(session, app_name, deployment_service_name, reservation_id, logger)
        deployed_app_name = deployment_result.LogicalResourceName
        #  self._write_message(deployed_app_name, reservation_id, session, 'Deployment ended successfully')

        # if autoload fails we still want to continue so 'success message' moved inside '_try_exeucte_autoload'
        if events.autoload:
            self._try_execute_autoload(session, reservation_id, deployed_app_name, logger)

        self._write_message(deployed_app_name, reservation_id, session, 'connecting routes started')
        # if visual connector endpoints contains service with attribute "Virtual Network" execute connect command

        connection_results = \
            self._connect_routes_on_deployed_app(session, reservation_id, deployment_result.LogicalResourceName, logger)

        self._write_message(deployed_app_name, reservation_id, session, 'connecting routes ended successfully')

        if events.power_on:
            self._write_message(deployed_app_name, reservation_id, session, 'is powering on...')
            self._power_on_deployed_app(session, deployed_app_name, deployment_result, reservation_id, logger)
            self._write_message(deployed_app_name, reservation_id, session, 'powered on successfully')

        if events.wait_for_ip:
            self._write_message(deployed_app_name, reservation_id, session,
                                'is waiting for IP address, this may take a while...')
            ip = self._refresh_ip(session, deployment_result, reservation_id, logger)
            self._write_message(deployed_app_name, reservation_id, session,
                                'IP address is {0}'.format(ip) if ip else 'IP address not found')

        if events.wait_for_ip or self._was_connected(connection_results):
            session.RefreshVMDetails(reservation_id, [deployed_app_name])

        self._configure_app(session, deployment_result, reservation_id, logger)

        # Set live status - deployment done
        self._set_live_status(deployment_result, events.power_on, session)

        success_msg = self._format_message(deployed_app_name, 'deployed successfully')
        logger.info(success_msg)
        return success_msg

    def _get_logger(self, context):
        with LoggingSessionContext(context) as new_logger:
            logger = new_logger
        return logger

    def _get_cloudshell_api(self, context, logger):
        logger.info("Creating api session")
        with ErrorHandlingContext(logger):
            with CloudShellSessionContext(context) as cloudshell_session:
                session = cloudshell_session
        return session

    def _set_live_status(self, deployment_result, power_on, session):
        if power_on:
            session.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Online", "Active")
        else:
            session.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Offline", "Powered Off")

    def _write_message(self, app_name, reservation_id, session, message):
        session.WriteMessageToReservationOutput(reservationId=reservation_id,
                                                message=self._format_message(app_name, message))

    def _format_message(self, app_name, message):
        if ' ' in app_name:
            app_name = '"{0}"'.format(app_name)
        return '{0} {1}'.format(app_name, message)

    @staticmethod
    def _connected_to_deployed_app(resource_name, connector):
        return resource_name in connector.Source.split('/') or resource_name in connector.Target.split('/')

    def _connect_routes_on_deployed_app(self, api, reservation_id, resource_name, logger):
        try:
            reservation = api.GetReservationDetails(reservation_id)
            connectors = [connector for connector in reservation.ReservationDescription.Connectors
                          if connector.State in ['Disconnected', 'PartiallyConnected', 'ConnectionFailed'] and
                          self._connected_to_deployed_app(resource_name, connector)]
            endpoints = []
            for endpoint in connectors:
                endpoints.append(endpoint.Target)
                endpoints.append(endpoint.Source)

            if len(endpoints) == 0:
                logger.info("No routes to connect for app {0}".format(resource_name))
                return

            logger.info("Executing connect for app {0}".format(resource_name))
            return api.ConnectRoutesInReservation(reservation_id, endpoints, 'bi')

        except CloudShellAPIError as exc:
            print "Error executing connect all. Error: {0}".format(exc.rawxml)
            logger.error("Error executing connect all. Error: {0}".format(exc.rawxml))
            raise
        except Exception as exc:
            print "Error executing connect all. Error: {0}".format(str(exc))
            logger.error("Error executing connect all. Error: {0}".format(str(exc)))
            raise

    def _refresh_ip(self, api, deployment_result, reservation_id, logger):
        logger.info(
            "Waiting to get IP for deployed app resource {0}...".format(deployment_result.LogicalResourceName))
        try:
            res = api.ExecuteResourceConnectedCommand(reservation_id,
                                                      deployment_result.LogicalResourceName,
                                                      "remote_refresh_ip",
                                                      "remote_connectivity")
            ip = getattr(res, 'Output', None)
            if not ip:
                return ip
            return ip.replace('command_json_result="', '').replace('"=command_json_result_end', '')

        except CloudShellAPIError as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                exc.rawxml)
            logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, exc.rawxml))
            api.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Error", "Refreshing ip has failed")
            raise exc
        except Exception as exc:
            print "Error refreshing ip for deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                str(exc))
            logger.error("Error refreshing ip for deployed app {0}. Error: {1}"
                         .format(deployment_result.LogicalResourceName, str(exc)))
            api.SetResourceLiveStatus(deployment_result.LogicalResourceName, "Error", "Refreshing ip has failed")
            raise exc

    def _configure_app(self, api, deployment_result, reservation_id, logger):

        logger.info('App {0} is being configured ...'.format(deployment_result.LogicalResourceName))

        try:
            conf = [AppConfiguration(deployment_result.LogicalResourceName, [])]
            configuration_result = api.ConfigureApps(reservationId=reservation_id, appConfigurations=conf, printOutput=True)

            if not configuration_result.ResultItems:
                self._write_message(deployment_result.LogicalResourceName, reservation_id, api, 'No apps to configure')
                return

            failed_apps = []
            for conf_res in configuration_result.ResultItems:
                if conf_res.Success:
                    message = "App '{0}' configured successfully".format(conf_res.AppName)
                    logger.info(message)
                else:
                    message = "App '{0}' configuration failed due to {1}".format(conf_res.AppName,
                                                                                 conf_res.Error)
                    logger.error(message)
                    failed_apps.append(conf_res.AppName)

            if not failed_apps:
                self._write_message(deployment_result.LogicalResourceName, reservation_id, api,
                                    'App was configured successfully ...')
            else:
                self._write_message(deployment_result.LogicalResourceName, reservation_id, api,
                                    'Apps: {0} configuration failed. See logs for more details'.format(
                                        ",".join(failed_apps)))

                raise Exception("Configuration of app failed see logs.")


        except Exception as exc:
            print "Error configuring deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                          str(exc))
            logger.error("Error configuring deployed app {0}. Error: {1}".format(deployment_result.LogicalResourceName,
                                                                                 str(exc)))
            raise

    def _power_on_deployed_app(self, api, app_name, deployment_result, reservation_id, logger):
        try:
            logger.info("Powering on deployed app {0}".format(deployment_result.LogicalResourceName))
            logger.debug("Powering on deployed app {0}. VM UUID: {1}".format(deployment_result.LogicalResourceName,
                                                                             deployment_result.VmUuid))
            api.ExecuteResourceConnectedCommand(reservation_id,
                                                deployment_result.LogicalResourceName,
                                                "PowerOn",
                                                "power")
        except Exception as exc:
            print "Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc))
            logger.error("Error powering on deployed app {0}. Error: {1}".format(app_name, str(exc)))
            api.SetResourceLiveStatus(app_name, "Error", "Powering on has failed")
            raise

    def _deploy_app(self, api, app_name, deployment_service, reservation_id, logger):
        try:
            logger.info("Executing '{0}' on app '{1}'...".format(deployment_service, app_name))
            return api.DeployAppToCloudProvider(reservation_id, app_name, [InputNameValue("Name", app_name)])
        except CloudShellAPIError as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml)
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, exc.rawxml))
            raise
        except Exception as exc:
            print "Error deploying app {0}. Error: {1}".format(app_name, str(exc))
            logger.error("Error deploying app {0}. Error: {1}".format(app_name, str(exc)))
            raise

    def _remap_connections(self, api, reservation_id, deployed_app_name, logger):
        """
        :param str reservation_id:
        :param CloudShellAPISession api:
        :param str deployed_app_name:
        :param logging.Logger logger:
        :return:
        """
        self._write_message(deployed_app_name, reservation_id, api, 'Remap connections started.')

        try:

            remap_result = api.RemapConnections(reservationId=reservation_id, resourcesFullPath=[deployed_app_name],
                                                printOutput=True)

            if not remap_result.ResultItems:
                logger.info('No resource connections remapped')
                return

            remap_result_item = remap_result.ResultItems[0]

            if remap_result_item.Success:
                message = "App '{0}' connections remapped successfully".format(remap_result_item.ResourceName)
                logger.info(message)
                api.WriteMessageToReservationOutput(reservationId=reservation_id,
                                                    message=message)

            else:
                message = "App '{0}' remap connections operation failed due to {1}".format(remap_result_item.ResourceName, remap_result_item.Error)
                logger.error(message)
                api.WriteMessageToReservationOutput(reservationId=reservation_id,
                                                    message='Failed to remap connections for app: {0}. See logs for more details'.format(remap_result_item.ResourceName))
                raise Exception("App '{0}' remap connections operation failed.")


        except Exception as ex:
            logger.error("Error in remap connections. Error: {0}".format(str(ex)))
            raise

    def _try_execute_autoload(self, session, reservation_id, deployed_app_name, logger):
        """
        :param str reservation_id:
        :param CloudShellAPISession session:
        :param str deployed_app_name:
        :return:
        """
        try:
            logger.info("Executing Autoload command on deployed app {0}".format(deployed_app_name))
            self._write_message(deployed_app_name, reservation_id, session, 'discovery started')

            session.AutoLoad(deployed_app_name)
            self._write_message(deployed_app_name, reservation_id, session, 'discovery ended successfully')
            self._remap_connections(api=session, reservation_id=reservation_id, deployed_app_name=deployed_app_name,
                                    logger=logger)

        except CloudShellAPIError as exc:
            if exc.code not in (
                    DeployAppOrchestrationDriver.NO_DRIVER_ERR, DeployAppOrchestrationDriver.DRIVER_FUNCTION_ERROR):
                print "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                                exc.rawxml)
                logger.error(
                    "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                              exc.rawxml))
                session.SetResourceLiveStatus(deployed_app_name, "Error", "Discovery failed")
                self._write_message(deployed_app_name, reservation_id, session,
                                    'discovery failed: {1}'.format(deployed_app_name, exc.message))
                raise

        except Exception as exc:
            print "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name, str(exc))
            logger.error(
                "Error executing Autoload command on deployed app {0}. Error: {1}".format(deployed_app_name,
                                                                                          str(exc)))
            session.SetResourceLiveStatus(deployed_app_name, "Error", "Discovery failed")
            self._write_message(deployed_app_name, reservation_id, session,
                                'discovery failed: {1}'.format(deployed_app_name, exc.message))
            raise


    @staticmethod
    def _was_connected(connect_results):
        return hasattr(connect_results, 'Routes') and len(connect_results.Routes) > 0


