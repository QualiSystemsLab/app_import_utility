class AutoEvents(object):
    def __init__(self, deployment_attributes):
        autoload_param = self._get_attribute_value(deployment_attributes, "Autoload", "true").lower()
        power_on_param = self._get_attribute_value(deployment_attributes, "Auto Power On", "true").lower()
        wait_for_ip_param = self._get_attribute_value(deployment_attributes, "Wait For IP", "true").lower()

        self.autoload = autoload_param == "true"
        self.wait_for_ip = wait_for_ip_param == "true"
        self.power_on = power_on_param == "true"

    @staticmethod
    def _get_attribute_value(deployment_attributes, attribute_name, default_value):
        attributes = filter(lambda x: x["name"].lower() == attribute_name.lower() or
                                      x["name"].lower().endswith("." + attribute_name.lower()),
                            deployment_attributes)
        if len(attributes) == 1:
            return attributes[0]["value"]
        return default_value
