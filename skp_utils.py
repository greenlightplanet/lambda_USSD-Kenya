import time
import requests
def get_agent_roles_from_skp_using_phone_number(phone_number):
    response = {} 
    before_time = time.time()
    r = requests.get(url='https://admin.glpapps.com/glpadmin/skp/users_by_phone_number/all/{}?country=Kenya'.format(phone_number))
    response = r.json()
    after_time = time.time()
    print("skp agent detail by phone number API end time: {}".format(after_time))
    print("skp agent detail by phone number API overall time: {}".format(after_time - before_time))
    roles = []
    print(response)
    contents = response["content"]
    if len(contents) > 0:
        content = contents[0]
        if content["isEnable"] == True:
            userRoles = content["userRoles"]
            if userRoles is not None:
                for userRole in userRoles:
                    roles.append(userRole["name"])
                return roles
    return roles