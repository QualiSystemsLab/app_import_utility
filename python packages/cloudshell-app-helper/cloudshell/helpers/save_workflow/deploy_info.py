class DeployInfo(dict):
    def __init__(self, deployment_paths):

        deploypaths = []
        for deploy_path in deployment_paths:
            path = dict()
            path['name'] = deploy_path.Name
            path['is_default'] = deploy_path.IsDefault
            path['service_name'] = deploy_path.DeploymentService.Model
            path['attributes'] = dict()
            for attribute in deploy_path.DeploymentService.Attributes:
                path['attributes'][attribute.Name] = attribute.Value
            deploypaths.append(path)
        dict.__init__(self, deploypaths=deploypaths)
