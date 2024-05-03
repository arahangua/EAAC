import json
import requests

# Retrieve and save the file
def get_from_ipfs(ipfs_node, file_hash):
    # Retrieve the file using its hash
    get_response = requests.post(f'{ipfs_node}/api/v0/cat?arg={file_hash}')
    content = get_response.text
    json_content = json.loads(content)
    return json_content