
from re import A
from client import RestClient
from aptos_sdk.client import FaucetClient
import os
import sys
from constants import NODE_URL, BATCH_NUMBER, FAUCET_URL, MODE
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

rest_client = RestClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, rest_client)

with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
    config = json.load(f)
_METADATA_FOLDER = config['collection']['metadataDir']
_MINT_FEE_PER_MILLE = int(config['collection']['mintFee'])
_PRESALE_MINT_TIME = int(config['collection']['presaleMintTime'])
_PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
_COLLECTION_NAME = config['collection']['collectionName']
_COLLECTION_SIZE = int(config['collection']['collectionSize'])
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

def get_cm_account():
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    cm_public = config['candymachine']['cmPublicKey']
    cm_private = config['candymachine']['cmPrivateKey']
    cmAccount =  Account(
        AccountAddress.from_hex(cm_public), 
        ed25519.PrivateKey.from_hex(cm_private))
    return cmAccount

def mint(num_mints, amount_per_mint):
    cmAccount = get_cm_account()
    
    print(cmAccount.address())
    user = cmAccount
    accountBalance = int (rest_client.account_balance(user.address().hex()))
    print(f"user account balance: {accountBalance}")
    print(f"\n=== Minting {amount_per_mint} nft per mint for {num_mints} mints===")
    for i in range(num_mints):
        txn_hash = rest_client.mint_tokens(
            user=user, admin_addr=cmAccount.address(), collection_name=_COLLECTION_NAME, amount=amount_per_mint)

        rest_client.wait_for_transaction(txn_hash)
        print("\n Success, txn hash: " + txn_hash)

def update_mint_fee():
    cmAccount = get_cm_account()
    print("\n=== Setting  mint fee ===")
    txn_hash = rest_client.set_mint_fee_per_mille(
        cmAccount, _COLLECTION_NAME, _MINT_FEE_PER_MILLE
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, mint fee is set to:: " + str(_MINT_FEE_PER_MILLE/100000000) + " txn hash: " + txn_hash)

def update_presale_mint_time():
    cmAccount = get_cm_account()
    print("\n=== Setting presale mint time ===")
    txn_hash = rest_client.set_presale_mint_time(
        cmAccount, _COLLECTION_NAME, _PRESALE_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, presale mint time is set to: " + str (datetime.datetime.fromtimestamp(_PRESALE_MINT_TIME)) + " txn hash: " + txn_hash)

def update_public_mint_time():
    cmAccount = get_cm_account()
    print("\n=== Setting public mint time ===")
    txn_hash = rest_client.set_public_mint_time(
        cmAccount, _COLLECTION_NAME, _PUBLIC_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, public mint time is set to: " + str(datetime.datetime.fromtimestamp(_PUBLIC_MINT_TIME)) + " txn hash: " + txn_hash)

def append_or_overwrite_whitelist():
    cmAccount = get_cm_account()
    print("\n=== Appending or Overwriting Whitelist ===")
    wl_file = open(_WL_DIR + '/whitelist.txt', 'r')
    lines = wl_file.readlines()
    addresses, wl_supplies = [], []
    for line in lines:
        address, wl_supply = line.split(' ')
        print("address: " + address + ' with supply: ' + wl_supply)
        addresses.append(AccountAddress.from_hex(address))
        wl_supplies.append(int(wl_supply))
    batch_num = BATCH_NUMBER
    num_batch = len(addresses) // batch_num
    remainder = len(addresses) % batch_num
    if remainder > 0:
        num_iter = num_batch + 1
    else:
        num_iter = num_batch
    for i in range(num_iter):
        print(f"batch iter:{i}")
        startIndex = i * batch_num
        endIndex = min(startIndex + batch_num, len(addresses))
        txn_hash = rest_client.append_or_overwrite_whitelist(
            cmAccount, _COLLECTION_NAME, addresses[startIndex:endIndex], wl_supplies[startIndex:endIndex]
        )
        rest_client.wait_for_transaction(txn_hash)
        print("\n Success, txn hash: " + txn_hash)

def prepareFormData(fileDir):
    multipart_form_data = {
        'file': open(fileDir, 'rb')
    }
    return multipart_form_data

def uploadToIpfs(file):
    multipart_form_data = prepareFormData(file)
    try:
        r = requests.post(url = _API_ENDPOINT, files = multipart_form_data, headers = _HEADERS)
        r.raise_for_status()
        jsonResponse = r.json()
        ipfsHash = jsonResponse['IpfsHash']
        ipfsUri = constants.IPFS_GATEWAY + ipfsHash
        print("Upload success! View file at: " + ipfsUri)
        return ipfsHash
    except requests.exceptions.HTTPError as e:
        print (e.response.text)
        return None

def uploadFolderToIpfs():
    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    uri_list = getUriList(uri_list_file_path)

    os.chdir(_ASSET_FOLDER)
    failed_file_names = []
    cover = None

    for file in os.listdir():
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            file_name = file.split('.')[0]
            file_path = _ASSET_FOLDER + '/' + file
            if file_name == "cover":
                cover = file_path
                continue
            if isFileAlreadyUploaded(file_name, uri_list): continue
            print('uploading file: ' + file_path)
            ipfsHash = uploadToIpfs(file_path)
            if (ipfsHash == None): 
                print(f"FAILED UPLOAD of file {file_name}")
                failed_file_names.append(file_name)
                continue
            metadataFilePath = _METADATA_FOLDER + '/' + file_name + '.json'
            with open(metadataFilePath) as metadata_file:
                data = json.load(metadata_file)
            token_name = data["name"]
            data['image'] = constants.IPFS_GATEWAY + ipfsHash
            with open(metadataFilePath, 'w') as metadata_file:
                json.dump(data, metadata_file, indent=4)
            metadataUri = uploadToIpfs(metadataFilePath)
            uri_info = {
                "name": file_name,
                "token_name": token_name,
                "uri": constants.IPFS_GATEWAY + ipfsHash,
                "metadata_uri": constants.IPFS_GATEWAY + metadataUri,
                "onChain": False
            }
            uri_list = saveUploadInfo(uri_info, uri_list, uri_list_file_path)
    
    print(f"Files that failed to upload: {failed_file_names}")
    if len(failed_file_names) == 0: print("All images were uploaded successfully")

    # set cover image if cover.png is not supplied
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    if not cover: 
        config['collection']['collectionCover'] = uri_list[0]["uri"]
    else:
        config['collection']['collectionCover'] = constants.IPFS_GATEWAY + uploadToIpfs(cover)
    with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
        json.dump(config, configfile, indent=4)
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

def uploadFolderToArweave():
    silenceArweaveTransactions()

    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    uri_list = getUriList(uri_list_file_path)

    os.chdir(_ASSET_FOLDER)
    failed_file_names = []
    cover = None
    for file in os.listdir():
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            file_name, format = file.split('.')
            file_path = _ASSET_FOLDER + '/' + file
            if file_name == "cover":
                cover = file_path
                continue
            if isFileAlreadyUploaded(file_name, uri_list): continue

            print('uploading file: ' + file_path + " of format: " + format)
            arweaveURI = uploadToArweave(file_path, format)
            if (arweaveURI == None): 
                print(f"FAILED UPLOAD of file {file_name}")
                failed_file_names.append(file_name)
                continue
            metadataFilePath = _METADATA_FOLDER + '/' + file_name + '.json'
            with open(metadataFilePath) as metadata_file:
                data = json.load(metadata_file)
            token_name = data["name"]
            data['image'] = arweaveURI
            # upload nft metadat file
            wallet = Wallet(_ARWEAVE_WALLET_PATH)
            tx = Transaction(wallet, data=json.dumps(data).encode('utf-8'))
            tx.add_tag('Content-Type', 'application/json')
            tx.sign()
            tx.send()

            metadataUri = f"https://arweave.net/{tx.id}?ext=json"
            with open(metadataFilePath, 'w') as metadata_file:
                json.dump(data, metadata_file, indent=4)
            uri_info = {
                "name": file_name,
                "token_name": token_name,
                "uri": arweaveURI,
                "metadata_uri": metadataUri,
                "onChain": False
            }

            uri_list = saveUploadInfo(uri_info, uri_list, uri_list_file_path)
            
    print(f"Files that failed to upload: {failed_file_names}")
    if len(failed_file_names) == 0: print("All images were uploaded successfully")
    # set cover image if cover.png is not supplied
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    if not cover: 
        config['collection']['collectionCover'] = uri_list[0]["uri"]
    else:
        config['collection']['collectionCover'] = uploadToArweave(cover)
    with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
        json.dump(config, configfile, indent=4)
    return len(failed_file_names) == 0 # whether all files were uploaded or not

def uploadFolder():
    if _STORAGE_SOLUTION == "pinata": return uploadFolderToIpfs()
    elif _STORAGE_SOLUTION == "arweave": return uploadFolderToArweave()
    else: raise Exception("Storage solution is not supported. Please select either pinata or arweave")

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
    uri_list.append(uri_info)
    with open(uri_list_file_path, "w") as uri_list_file:
        json.dump(uri_list, uri_list_file, indent=4)
    return uri_list

def verifyMetadataFiles():
    is_valid = True

    assets = os.listdir(_ASSET_FOLDER)
    images = [asset.split(".")[0] for asset in assets if asset.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    metadatas = [metadata for metadata in os.listdir(_METADATA_FOLDER) if metadata.endswith(".json")]
    token_names = []
    if len(metadatas) != _COLLECTION_SIZE:
        print("Metadata files error: Not the same amount of metadata files as the collectionSize in config.json.")
        is_valid = False

    for image in images:
        if image == "cover":
            continue
        metadata = image + ".json"
        if metadata not in metadatas:
            print("Metadata files error: Metadata files not following naming convention from 1 to collectionSize.")
            is_valid = False

        with open(os.path.join(_METADATA_FOLDER, metadata), "r") as metadata_file:
            metadata_config = json.load(metadata_file)
            token_names.append(metadata_config['name'])
            if "name" not in metadata_config.keys():
                print(f"Metadata file {metadata} does not have a name.")
                is_valid = False
            else:
                if type(metadata_config["name"]) != str:
                    print(f"{metadata} can only be a string.")
                    is_valid = False
            if "description" not in metadata_config.keys():
                print(f"Metadata file {metadata} does not have a description.")
                is_valid = False
            else:
                if type(metadata_config["description"]) != str:
                    print(f"{metadata} can only be a string.")
                    is_valid = False
            if "attributes" not in metadata_config.keys():
                print(f"Metadata file {metadata} does not have attributes.")
                is_valid = False
            else:
                if type(metadata_config["attributes"]) != list:
                    print(f"Metadata file {metadata} attributes is not a list.")
                    is_valid = False
                for attribute in metadata_config["attributes"]:
                    if "trait_type" not in attribute.keys():
                        print(f"Metadata file {metadata} trait_type not present on an attribute")
                        is_valid = False
                    if "value" not in attribute.keys():
                        print(f"Metadata file {metadata} value not present on an attribute")
                        is_valid = False

    if len(token_names) != len(set(token_names)):
        print("You have duplicate token names.")
        is_valid = False

    return is_valid
