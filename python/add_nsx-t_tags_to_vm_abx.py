import requests
import json

nsx_manager = 'nsxtmanager.your.domain'
nsx_api_user = 'admin'
nsx_api_password = 'SuperSecretPassword'
nsx_get_api_path = '/api/v1/fabric/virtual-machines?display_name='
nsx_post_api_path = '/api/v1/fabric/virtual-machines?action=update_tags'

def get_vm_json(vm_name):
    response = requests.get("https://" + nsx_manager + nsx_get_api_path + vm_name, verify=False,
                            auth=(nsx_api_user, nsx_api_password))
    if 400 <= response.status_code <= 499:
        print("Status code is a 4xx so exiting!")
        exit(1)

    vm_json_obj = json.loads(response.text)

    if vm_json_obj["result_count"] != 1:
        print("VM record not found in NSX. Exiting!")
        exit(2)

    return vm_json_obj


def get_orig_tag_json(orig_json):
    if "tags" in orig_json["results"][0].keys():
        tag_count = len(orig_json["results"][0]["tags"])
        if tag_count > 0:
            print("The number of tags found is: " + str(tag_count))
            orig_tags = orig_json["results"][0]["tags"]
        else:
            print("No existing tags found.")
            orig_tags = None
    # This should never be hit but the interpreter complains without it.
    else:
        orig_tags = None
    return orig_tags


def create_post_json(existing_tags_json, new_tags_json, vm_id_in):
    merged_tags = []
    # If we have any existing key, add them to the list since they will be overwritten
    if existing_tags_json is not None:
        for i in existing_tags_json:
            tag_item = {"scope": i["scope"], "tag": i["tag"]}
            merged_tags.append(tag_item)
    # Add the new tags to the list
    for i in new_tags_json:
        tag_item = {"scope": i["scope"], "tag": i["tag"]}
        merged_tags.append(tag_item)
    # Create the JSON to be submitted by combining the VM ID and the tag list
    post_json_out = {"external_id": vm_id_in, "tags": merged_tags}
    return post_json_out


def parse_tags(bp_json):
    tag_json = []
    for key, value in bp_json["tags"].items():
        if key.startswith("nsx-"):
            print(key, value)
            tag_item = {"scope": key, "tag": value}
            tag_json.append(tag_item)
    return tag_json


def handler(context, inputs):
    vm_name_in = inputs["resourceNames"][0]
    vm_json = get_vm_json(vm_name_in)
    orig_tag_json = get_orig_tag_json(vm_json)
    vm_id = vm_json["results"][0]["external_id"]
    new_tags = parse_tags(inputs)
    post_json = create_post_json(orig_tag_json, new_tags, vm_id)

    nsx_post = requests.post("https://" + nsx_manager + nsx_post_api_path, json=post_json, verify=False,
                             auth=(nsx_api_user, nsx_api_password))

    outputs = {
        "vm_name": vm_name_in
    }

    return outputs
