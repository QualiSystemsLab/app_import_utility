def attribute(name, value, overwrite=False):
    xml ="""
    <Attribute Name="{Name}" Value="{Value}" {overwrite}/>
    """
    return xml.format(Name=name, Value=value, overwrite='Override="true"' if overwrite else "")


def deployment_path(deploy_name, deploy_service_name, deploy_attributes, cloud_provider):
    xml = """
    <DeploymentPath Name="{dn}" Default="false">
    <DeploymentService Name="{dsn}" CloudProvider="{cp}">
    <Attributes>
    {DeployAttributes}
</Attributes>
</DeploymentService>
</DeploymentPath>
"""
    return xml.format(DeployAttributes="\n".join([attribute(x, y, True) for x, y in deploy_attributes.iteritems()]),
                      cp=cloud_provider, dn=deploy_name, dsn=deploy_service_name)


def app_resource(attributes, model, driver):
    xml = """
        <AppResources>
      <AppResource ModelName="{model}" Driver="{driver}">
        <Attributes>
          {Attributes}
        </Attributes>
      </AppResource>
    </AppResources>
    
    """
    return xml.format(Attributes="\n".join(attribute(x, y, True) for x, y in attributes.iteritems()), model=model, driver=driver)


def app_resource_info(app_name, deploy_name, deploy_service_name, app_attributes, model, driver, deploy_attributes, cloud_provider, image_name):
    xml = """
  <AppResourceInfo Name="{AppName}" ImagePath="{img}">
    {AppResource}
    <DeploymentPaths>
    {DeploymentPath}
    
    </DeploymentPaths>
    </AppResourceInfo>
    """
    return xml.format(AppName=app_name, img=image_name, AppResource=app_resource(app_attributes, model, driver), DeploymentPath=deployment_path(deploy_name, deploy_service_name, deploy_attributes, cloud_provider))


def add_category(category):
    xml = """
    <Category>{Category}</Category>
    """
    return xml.format(Category=category)


def categories_info(categories):
    xml = """
      <Categories>
        {Categories}
  </Categories>
    
    """
    return xml.format(Categories="\n".join([add_category(x) for x in categories]))


def app_template(app_name, deploy_name, deploy_service_name, categories, app_attributes, model, driver, deploy_attributes, cloud_provider, image_name):
    """

    :return:
    """
    xml ="""<?xml version="1.0" encoding="utf-8"?>
<AppTemplateInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    {AppResourceInfo}

        {Categories}
    </AppTemplateInfo>
    """
    app_resource = app_resource_info(app_name, deploy_name, deploy_service_name, app_attributes, model, driver, deploy_attributes, cloud_provider, image_name)
    categories = categories_info(categories)

    return xml.format(AppResourceInfo=app_resource, Categories=categories if categories else "")

# print app_template("testapp1", ["Cate1", "Cate2"], {"Password": "3M3u7nkDzxWb0aJ/IZYeWw==", "Public IP": "", "User": ""}, {"vCenter Image": "C:\Users\omri.a\Downddddddddddddddddddddddloads\photon-hw11-3.0-26156e2.ova1214"})