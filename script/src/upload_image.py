import requests
import os
import sys
import constants
import json

with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
  config = json.load(f)

_API_ENDPOINT = config['pinata']['pinataApi']
_API_KEY = config['pinata']['pinataPublicKey']
_API_SECRETE_KEY = config['pinata']['pinataSecretKey']
_ASSET_FOLDER = config['collection']['assetDir']
_HEADERS = {
    'pinata_api_key': _API_KEY,
    'pinata_secret_api_key': _API_SECRETE_KEY
}


def prepareFormData(fileDir):
    # data to be sent to api
    multipart_form_data = {
        'file': open(fileDir, 'rb')
    }
    return multipart_form_data

def uploadToIpfs(file):

    multipart_form_data = prepareFormData(file)
    # sending post request and saving response as response object
    try:
        r = requests.post(url = _API_ENDPOINT, files = multipart_form_data, headers = _HEADERS)
        r.raise_for_status()
        jsonResponse = r.json()
        ipfsHash = jsonResponse['IpfsHash']
        print("Upload success! View file at: " + "https://cloudflare-ipfs.com/ipfs/" + ipfsHash)
        return ipfsHash
    except requests.exceptions.HTTPError as e:
        print (e.response.text)
        return None

def uploadFolder():
    if os.path.exists(_ASSET_FOLDER + '/' + 'image_cid.txt'):
        print("assets IPFS hash file already exist")
        return
    cid_list = []
    os.chdir(_ASSET_FOLDER)
    for file in os.listdir():
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            # special case: cover image
            fileName = file.split('.')[0]
            file_path = _ASSET_FOLDER + '/' + file
            print('uploading file: ' + file_path)
            ipfsHash = uploadToIpfs(file_path)
            line = fileName + ' ' + ipfsHash
            if fileName == 'cover':
                config['collection']['collectionCover'] = constants.IPFS_GATEWAY + '/' + ipfsHash
                with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
                    json.dump(config, configfile)
                continue
            cid_list.append(line)
    with open(r'image_cid.txt', 'w') as fp:
        for item in cid_list:
            # write each item on a new line
            fp.write("%s\n" % item)
        print('Done')