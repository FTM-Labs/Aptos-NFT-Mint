from asyncio import constants
from constants import NODE_URL, FAUCET_URL, MODE, BATCH_NUMBER
from aptos_sdk.account import Account, AccountAddress, ed25519
from client import RestClient
from aptos_sdk.client import FaucetClient
import sys
import os
import random
import datetime
from nft import NFT
import json
import util
from pick import pick

def create():
    print(f"Mode: {MODE}")
        
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    _ASSET_FOLDER = config['collection']['assetDir']
    _METADATA_FOLDER = config['collection']['metadataDir']
    _COLLECTION_NAME = config['collection']['collectionName']
    _COLLECTION_DESCRIPTION = config['collection']['collectionDescription']
    _COLLECTION_COVER = config['collection']['collectionCover']
    _COLLECTION_SIZE = int(config['collection']['collectionSize'])
    _MAX_MINTS_PER_WALLET = int(config['collection']['maxMintPerWallet'])
    _MINT_FEE = int(config['collection']['mintFee'])
    _ROYALTY_POINTS_DENOMINATOR = config['collection']['royalty_points_denominator']
    _ROYALTY_POINTS_NUMERATOR = config['collection']['royalty_points_numerator']
    _PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
    _PRESALE_MINT_TIME = int(config['collection']['presaleMintTime'])
    _ACCOUNT_ADDRESS = config['candymachine']['cmPublicKey']
    _ACCOUNT_PRIVATE_KEY = config['candymachine']['cmPrivateKey']
    rest_client = RestClient(NODE_URL)

    print("\n=== Verifying assets and metadata ===")
    if not util.verifyMetadataFiles(): return

    print('\n=== Upload assets to storage solution ===')
    if not util.uploadFolder():
        print("Not all files were uploaded to storage. Try again.")
        return

    try:
        alice = prepareCandyMachineAccount(_ACCOUNT_ADDRESS, _ACCOUNT_PRIVATE_KEY, rest_client, config)
    except: return
    
    createCandyMachine(rest_client, alice, _ASSET_FOLDER)

    createCollection(rest_client, alice, _COLLECTION_NAME, _COLLECTION_DESCRIPTION, _COLLECTION_COVER, _MAX_MINTS_PER_WALLET, _MINT_FEE, _PUBLIC_MINT_TIME, _PRESALE_MINT_TIME)

    setPresaleMintTime(rest_client, alice, _COLLECTION_NAME, _PRESALE_MINT_TIME)
    setPublicMintTime(rest_client, alice, _COLLECTION_NAME, _PUBLIC_MINT_TIME)
    
    update_mint_fee(rest_client, alice, _COLLECTION_NAME, _MINT_FEE)
    uploadNftsToCm(_ASSET_FOLDER, _COLLECTION_NAME, _METADATA_FOLDER, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, alice, rest_client)
    #mint()
def prepareCandyMachineAccount(_ACCOUNT_ADDRESS, _ACCOUNT_PRIVATE_KEY, rest_client, config):
    print("\n=== Preparing Candy Machine account ===")
    if MODE == "dev":
        if len(_ACCOUNT_ADDRESS) == 66 and len(_ACCOUNT_PRIVATE_KEY) == 66:
            print("Candy machine addresses are already filled in config.json.")
            _, index = pick(["yes", "no"], "Candy machine addresses are already filled in config.json. Do you wish to override them with new funded accounts?")
            if index == 1: raise Exception
        alice = Account.generate()
        faucet_client = FaucetClient(FAUCET_URL, rest_client)
        for i in range(3):
            print(i)
            faucet_client.fund_account(alice.address(), 100000000)
    else:
        accountAddress = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
        privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
        alice = Account(accountAddress, privateKey)
    print(f'Public key: {alice.address()}\n')
    print(f'Private key: {alice.private_key}\n')
    config['candymachine']['cmPublicKey'] = str(alice.address())
    config['candymachine']['cmPrivateKey'] = str(alice.private_key)
    with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
        json.dump(config, configfile, indent=4)
    
    while (True):
        answer = "yes" if MODE == "dev" or MODE == "test" else input("Enter yes if you have some aptos in your account: ") 
        if answer == "yes":
            try:
                accountBalance = int (rest_client.account_balance(alice.address().hex()))
            except TypeError:
                print("Please add some Aptos to your candy machine account and try again.")
                raise Exception("Not enough funds in account")
            if accountBalance > 2000:
                print(f'Balance: {accountBalance}\n')
                break
        else:
            continue
    return alice

def createCandyMachine(rest_client, alice, _ASSET_FOLDER):
    print("\n=== Creating Candy Machine ===")
    txn_hash = rest_client.create_candy_machine(alice)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)
    resetChainInfoFromUriInfo(_ASSET_FOLDER)

def resetChainInfoFromUriInfo(_ASSET_FOLDER):
    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    with open(uri_list_file_path, "r+") as uri_list_file:
        uri_list = json.load(uri_list_file)
        for uriInfo in uri_list:
            uriInfo["onChain"] = False
        uri_list_file.seek(0)
        json.dump(uri_list, uri_list_file, indent=4)
        uri_list_file.truncate()

def createCollection(
    rest_client, alice, _COLLECTION_NAME, _COLLECTION_DESCRIPTION, _COLLECTION_COVER, _MAX_MINTS_PER_WALLET, _MINT_FEE, _PUBLIC_MINT_TIME, _PRESALE_MINT_TIME
):
    print("\n=== Creating Collection ===")

    txn_hash = rest_client.create_collection(
        alice, 
        _COLLECTION_NAME, 
        _COLLECTION_DESCRIPTION, 
        _COLLECTION_COVER,
        _MAX_MINTS_PER_WALLET,
        _MINT_FEE,
        _PUBLIC_MINT_TIME,
        _PRESALE_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)

def update_mint_fee(rest_client, alice, _COLLECTION_NAME, _MINT_FEE):
    print(f"checking mint fee config {_MINT_FEE}")
    txn_hash = rest_client.set_mint_fee_per_mille(
        alice, _COLLECTION_NAME, _MINT_FEE
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, mint fee per mille is set to:: " + str(_MINT_FEE) + " txn hash: " + txn_hash)

def setPresaleMintTime(rest_client, alice, _COLLECTION_NAME, _PRESALE_MINT_TIME):
    print("\n=== Setting presale mint time ===")
    txn_hash = rest_client.set_presale_mint_time(
            alice, _COLLECTION_NAME, _PRESALE_MINT_TIME)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, presale mint time is set to: " + str (datetime.datetime.fromtimestamp(_PRESALE_MINT_TIME)) + " txn hash: " + txn_hash)

def setPublicMintTime(rest_client, alice, _COLLECTION_NAME, _PUBLIC_MINT_TIME):
    print("\n=== Setting public mint time ===")
    txn_hash = rest_client.set_public_mint_time(
            alice, _COLLECTION_NAME, _PUBLIC_MINT_TIME)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, public mint time is set to: " + str(datetime.datetime.fromtimestamp(_PUBLIC_MINT_TIME)) + " txn hash: " + txn_hash)

def uploadNftsToCm(
    _ASSET_FOLDER, _COLLECTION_NAME, _METADATA_FOLDER, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR,
    alice, rest_client
):
    print("\n=== Uploading NFT ===")
    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    with open(uri_list_file_path, "r") as uri_list_file:
        uri_list = json.load(uri_list_file)

    all_descrips = list()
    all_token_names = list()
    all_uri = list()

    # test traits
    propertyKey = []
    propertyValue = []
    propertyType = []
    propertyKeys = []
    propertyValues = []
    propertyTypes = []

    nfts = []
    for index, uriInfo in enumerate(uri_list):
        if "onChain" in uriInfo.keys() and uriInfo["onChain"]: continue

        # tmp_name = _COLLECTION_NAME + " - #" + str(counter)
        tmp_uri = uriInfo["uri"]
        # tmp_description = tmp_name
        # read in traits
        metadataFilePath = _METADATA_FOLDER + '/' + uriInfo["name"] + '.json'
        with open(metadataFilePath) as metadata_file:
            data = json.load(metadata_file)
            tmp_name = data["name"]
            tmp_description = data["description"]
            for trait in data['attributes']:
                if isinstance(trait['value'], str): 
                    propertyKey.append(trait['trait_type'])
                    propertyValue.append(trait['value'].encode())
                    propertyType.append('String')
        nfts.append(
            {"nft": NFT(tmp_name, tmp_uri, tmp_description, propertyKey, propertyValue, propertyType), "uriInfoIndex": index}
        )
        propertyKey, propertyValue, propertyType = [], [], []
    random.shuffle(nfts)
    for nftInfo in nfts:
        all_token_names.append(nftInfo["nft"].name)
        all_descrips.append(nftInfo["nft"].description)
        all_uri.append(nftInfo["nft"].uri)
        propertyKeys.append(nftInfo["nft"].propertyKey)
        propertyValues.append(nftInfo["nft"].propertyValue)
        propertyTypes.append(nftInfo["nft"].propertyType)

    print(f"Uploading {len(nfts)} NFTs out of {len(uri_list)} ({len(uri_list) - len(nfts)} already uploaded).")
    # batch upload x nft at a time
    batch_num = BATCH_NUMBER
    num_batch = len(all_token_names) // batch_num
    remainder = len(all_token_names) % batch_num
    successfulUploadIndexes = []
    for i in range(num_batch):
        print(f"batch iter:{i}")
        startIndex = i * batch_num
        endIndex = startIndex + batch_num
        success = handleNftUpload(startIndex, endIndex, all_token_names, all_descrips, all_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, propertyKeys, propertyValues, propertyTypes, alice, _COLLECTION_NAME, rest_client)
        if success: successfulUploadIndexes.extend(range(startIndex, endIndex))
        for successfulUploadIndex in successfulUploadIndexes:
            uri_list[nfts[successfulUploadIndex]["uriInfoIndex"]]["onChain"] = True
        with open(uri_list_file_path, "w") as uri_list_file:
            json.dump(uri_list, uri_list_file, indent=4)
    if remainder:
        startIndex = num_batch*batch_num
        endIndex = len(all_token_names)
        success = handleNftUpload(startIndex, endIndex, all_token_names, all_descrips, all_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, propertyKeys, propertyValues, propertyTypes, alice, _COLLECTION_NAME, rest_client)
        if success: successfulUploadIndexes.extend(range(startIndex, endIndex))
        for successfulUploadIndex in successfulUploadIndexes:
            uri_list[nfts[successfulUploadIndex]["uriInfoIndex"]]["onChain"] = True
        with open(uri_list_file_path, "w") as uri_list_file:
            json.dump(uri_list, uri_list_file, indent=4)

    if len(successfulUploadIndexes) != len(nfts):
        print(f"Not all nfts ({len(successfulUploadIndexes)} out of {len(nfts)}) were uploaded successfully to the candy machine. Try to \"Retry failed uploads\".")
            


def handleNftUpload(
    startIndex, endIndex,
    all_token_names, all_descrips, all_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, propertyKeys, propertyValues, propertyTypes,
    alice, _COLLECTION_NAME,
    rest_client
):
    batch_token_names = all_token_names[startIndex:endIndex]
    batch_descrips = all_descrips[startIndex:endIndex]
    batch_uri = all_uri[startIndex:endIndex]
    batch_property_keys = propertyKeys[startIndex:endIndex]
    batch_property_values = propertyValues[startIndex:endIndex]
    batch_property_types = propertyTypes[startIndex:endIndex]
    try:
        txn_hash = rest_client.upload_nft(alice, _COLLECTION_NAME, batch_token_names, batch_descrips, batch_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, batch_property_keys, batch_property_values, batch_property_types)
        rest_client.wait_for_transaction(txn_hash)
    except Exception as e:
        print(f"An error occured while uploading batch from {startIndex} to {endIndex}")
        print(e)
        return False
    print("\n Success, txn hash: " + txn_hash)
    return True


def retryFailedUploads():
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    _ASSET_FOLDER = config['collection']['assetDir']
    _METADATA_FOLDER = config['collection']['metadataDir']
    _COLLECTION_NAME = config['collection']['collectionName']
    _ROYALTY_POINTS_DENOMINATOR = config['collection']['royalty_points_denominator']
    _ROYALTY_POINTS_NUMERATOR = config['collection']['royalty_points_numerator']
    _ACCOUNT_ADDRESS = config['candymachine']['cmPublicKey']
    _ACCOUNT_PRIVATE_KEY = config['candymachine']['cmPrivateKey']
    rest_client = RestClient(NODE_URL)

    if len(_ACCOUNT_ADDRESS) != 66 or len(_ACCOUNT_PRIVATE_KEY) != 66:
        print("Can't continue upload as CM info is not valid in config file")

    accountAddress = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
    privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
    alice = Account(accountAddress, privateKey)

    uploadNftsToCm(_ASSET_FOLDER, _COLLECTION_NAME, _METADATA_FOLDER, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, alice, rest_client)

def mint():
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)

    _COLLECTION_NAME = config['collection']['collectionName']
    _ACCOUNT_ADDRESS = config['candymachine']['cmPublicKey']
    _ACCOUNT_PRIVATE_KEY = config['candymachine']['cmPrivateKey']
    rest_client = RestClient(NODE_URL)

    accountAddres = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
    privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
    alice = Account(accountAddres, privateKey)
    #Testing mint
    print("\n=== Bob going to mint NFT ===")
    if MODE == 'test' or MODE == 'main':
        bob = alice
    else:
        bob = Account.generate()
    print(f"bob address: {bob.address()}")
    print(f"bob private: {bob.private_key}")
    print(f'Public key: {alice.address()}\n')
    print(f'Private key: {alice.private_key}\n')
    for i in range(3):
        FaucetClient(FAUCET_URL, rest_client).fund_account(bob.address(), 100000000)
    accountBalance = int (rest_client.account_balance(bob.address().hex()))
    print(accountBalance)
    txn_hash = rest_client.mint_tokens(
        user=bob, admin_addr=alice.address(), collection_name=_COLLECTION_NAME, amount=1)

    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)

# mint()