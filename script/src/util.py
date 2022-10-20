
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

import io
from PIL import Image
from arweave.arweave_lib import Wallet, Transaction
import logging

with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
    config = json.load(f)
_CM_PUBLIC = config['candymachine']['cmPublicKey']
_CM_PRIVATE = config['candymachine']['cmPrivateKey']
_MINT_FEE_PER_MILLE = int(config['collection']['mintFee'])
_PRESALE_MINT_TIME = int(config['collection']['presaleMintTime'])
_PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
_COLLECTION_NAME = config['collection']['collectionName']
_WL_DIR = config['collection']['whitelistDir']
_STORAGE_SOLUTION = config["storage"]["solution"]
_ARWEAVE_WALLET_PATH = config["storage"]["arweave"]["keyfilePath"]
_API_ENDPOINT = config["storage"]['pinata']['pinataApi']
_API_KEY = config["storage"]['pinata']['pinataPublicKey']
_API_SECRETE_KEY = config["storage"]['pinata']['pinataSecretKey']
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
        ipfsUri = constants.IPFS_GATEWAY + ipfsHash
        print("Upload success! View file at: " + ipfsUri)
        return ipfsUri
    except requests.exceptions.HTTPError as e:
        print (e.response.text)
        return None

def uploadFolderToIpfs():
    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    uri_list = getUriList(uri_list_file_path)

    os.chdir(_ASSET_FOLDER)
    failed_file_names = []
    for file in os.listdir():
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            # special case: cover image
            file_name = file.split('.')[0]
            file_path = _ASSET_FOLDER + '/' + file

            if isFileAlreadyUploaded(file_name, uri_list): continue

            print('uploading file: ' + file_path)
            ipfsUri = uploadToIpfs(file_path)
            if (ipfsUri == None): 
                print(f"FAILED UPLOAD of file {file_name}")
                failed_file_names.append(file_name)
                continue

            uri_info = {
                "name": file_name,
                "uri": ipfsUri
            }
            uri_list = saveUploadInfo(uri_info, uri_list, uri_list_file_path)
    
    print(f"Files that failed to upload: {failed_file_names}")
    return len(failed_file_names) == 0 # whether all files were uploaded or not



def uploadToArweave(file_path, format: str):
    try:
        wallet = Wallet(_ARWEAVE_WALLET_PATH)

        img = Image.open(file_path)
        with io.BytesIO() as output:
            img.save(output, format=format.upper())
            imageData = output.getvalue()

            tx = Transaction(wallet, data=imageData)
            tx.add_tag('Content-Type', f'image/{format}')
            tx.sign()
            tx.send()

            uri = f"https://arweave.net/{tx.id}?ext={format}"
            return uri
    except:
        return None

def silenceArweaveTransactions():
    logger = logging.getLogger("arweave_lib")
    # only log really bad events
    logger.setLevel(logging.ERROR)

def getUriList(uri_list_file_path):
    uri_list = []

    if os.path.exists(_ASSET_FOLDER + '/' + 'image_uris.json'):
        print("Continuing previous storage upload...")
        with open(uri_list_file_path, "r") as uri_list_file:
            uri_list = json.load(uri_list_file)
    return uri_list

def isFileAlreadyUploaded(fileName, uri_list):
    for uploaded_file in uri_list:
        if uploaded_file["name"] == fileName: return True
    if fileName == 'cover' and len(config['collection']['collectionCover']) != 0: return True
    return False

def saveUploadInfo(uri_info, uri_list, uri_list_file_path):
    print(uri_info)
    if uri_info["name"] == 'cover':
        config['collection']['collectionCover'] = uri_info["uri"]
        with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
            json.dump(config, configfile, indent=4)
        return uri_list

    uri_list.append(uri_info)
    with open(uri_list_file_path, "w") as uri_list_file:
        json.dump(uri_list, uri_list_file, indent=4)
    return uri_list

def uploadFolderToArweave():
    silenceArweaveTransactions()

    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    uri_list = getUriList(uri_list_file_path)

    os.chdir(_ASSET_FOLDER)
    failed_file_names = []
    for file in os.listdir():
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            file_name, format = file.split('.')
            file_path = _ASSET_FOLDER + '/' + file

            if isFileAlreadyUploaded(file_name, uri_list): continue

            print('uploading file: ' + file_path + " of format: " + format)
            arweaveURI = uploadToArweave(file_path, format)
            if (arweaveURI == None): 
                print(f"FAILED UPLOAD of file {file_name}")
                failed_file_names.append(file_name)
                continue

            uri_info = {
                "name": file_name,
                "uri": arweaveURI
            }

            uri_list = saveUploadInfo(uri_info, uri_list, uri_list_file_path)
            
    
    print(f"Files that failed to upload: {failed_file_names}")
    return len(failed_file_names) == 0 # whether all files were uploaded or not

def uploadFolder():
    if _STORAGE_SOLUTION == "pinata": return uploadFolderToIpfs()
    elif _STORAGE_SOLUTION == "arweave": return uploadFolderToArweave()
    else: raise Exception("Storage solution is not supported. Please select either pinata or arweave")