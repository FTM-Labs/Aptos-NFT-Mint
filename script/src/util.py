
from client import RestClient
import os
import sys
from constants import NODE_URL
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.account import Account
from aptos_sdk import ed25519
import os
import json
import requests
import constants
import datetime

with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
    config = json.load(f)
_CM_PUBLIC = config['candymachine']['cmPublicKey']
_CM_PRIVATE = config['candymachine']['cmPrivateKey']
_MINT_FEE_PER_MILLE = float(config['collection']['mintFee'])
_PRESALE_MINT_TIME = int(config['collection']['presaleMintTime'])
_PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
_COLLECTION_NAME = config['collection']['collectionName']
_WL_DIR = config['collection']['whitelistDir']
_API_ENDPOINT = config['pinata']['pinataApi']
_API_KEY = config['pinata']['pinataPublicKey']
_API_SECRETE_KEY = config['pinata']['pinataSecretKey']
_ASSET_FOLDER = config['collection']['assetDir']
_HEADERS = {
    'pinata_api_key': _API_KEY,
    'pinata_secret_api_key': _API_SECRETE_KEY
}

rest_client = RestClient(NODE_URL)

if _CM_PUBLIC and _CM_PRIVATE:
    cmAccount =  Account(
        AccountAddress.from_hex(_CM_PUBLIC), 
        ed25519.PrivateKey.from_hex(_CM_PRIVATE))

def update_mint_fee():
    txn_hash = rest_client.set_mint_fee_per_mille(
        cmAccount, _COLLECTION_NAME, _MINT_FEE_PER_MILLE
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, mint fee per mille is set to:: " + str(_MINT_FEE_PER_MILLE) + " txn hash: " + txn_hash)

def update_presale_mint_time():
    txn_hash = rest_client.set_presale_mint_time(
        cmAccount, _COLLECTION_NAME, _PRESALE_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, presale mint time is set to: " + str (datetime.datetime.fromtimestamp(_PRESALE_MINT_TIME)) + " txn hash: " + txn_hash)

def update_public_mint_time():
    txn_hash = rest_client.set_public_mint_time(
        cmAccount, _COLLECTION_NAME, _PUBLIC_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, public mint time is set to: " + str(datetime.datetime.fromtimestamp(_PUBLIC_MINT_TIME)) + " txn hash: " + txn_hash)

def update_whitelist():
    tmp_file = open(_WL_DIR + '/whitelist.txt', 'r')
    lines = tmp_file.readlines()
    addresses = []
    wl_supplies = []
    for line in lines:
        address, wl_supply = line.split(' ')
        print("address: " + address + ' with supply: ' + wl_supply)
        addresses.append(AccountAddress.from_hex(address))
        wl_supplies.append(int(wl_supply))
    txn_hash = rest_client.update_whitelist(
        cmAccount, _COLLECTION_NAME, addresses, wl_supplies
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)

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
                continue
            cid_list.append(line)
    with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
        json.dump(config, configfile)
    with open(r'image_cid.txt', 'w') as fp:
        for item in cid_list:
            # write each item on a new line
            fp.write("%s\n" % item)
        print('Done')
