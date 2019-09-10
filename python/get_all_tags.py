import requests
import json

nsx_manager = 'nsx_manager_fqdn'
nsx_api_user = 'admin'
nsx_api_password = 'super_secret_password'
nsx_api_path = '/api/v1/fabric/virtual-machines?included_fields=display_name,guest-info'

response = requests.get("https://" + nsx_manager + nsx_api_path, verify=False, auth=(nsx_api_user, nsx_api_password))

#f = open("sample_vm_data.json", "r")
#if f.mode == 'r':
#    response = f.read()
#else:
#    exit(1)

if 400 <= response.status_code <= 499:
    print("Status code is a 4xx so exiting!")
    exit(1)

tag_arr = []
json_obj = json.loads(response.text)

# Step through the results and only work on records with tags defined
for vm in json_obj['results']:
    if 'tags' in vm:
        for tag in vm['tags']:
            tag_arr.append(tag['tag'])

# Remove duplicate tags
tag_arr = list(dict.fromkeys(tag_arr))

# Print the list of tags in use
print(tag_arr)
