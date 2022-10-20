from asyncio import constants
from constants import NODE_URL, FAUCET_URL, MODE
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
import time

def create():
    print(f"Mode: {MODE}")

    print('\n=== Upload assets to storage solution ===')
    if not util.uploadFolder():
        print("Not all files were uploaded to storage. Try again.")
        return
        
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    _ASSET_FOLDER = config['collection']['assetDir']
    _METADATA_FOLDER = config['collection']['metadataDir']
    _COLLECTION_NAME = config['collection']['collectionName']
    _COLLECTION_DESCRIPTION = config['collection']['collectionDescription']
    _COLLECTION_COVER = config['collection']['collectionCover']
    _COLLECTION_SIZE = int(config['collection']['collectionSize'])
    _MINT_FEE = int(config['collection']['mintFee'])
    _ROYALTY_POINTS_DENOMINATOR = config['collection']['royalty_points_denominator']
    _ROYALTY_POINTS_NUMERATOR = config['collection']['royalty_points_numerator']
    _PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
    _PRESALE_MINT_TIME = int(config['collection']['presaleMintTime'])
    _ACCOUNT_ADDRESS = config['candymachine']['cmPublicKey']
    _ACCOUNT_PRIVATE_KEY = config['candymachine']['cmPrivateKey']
    rest_client = RestClient(NODE_URL)
    
    # print('\nSucces: asset ipfs hash can be found in ' + _ASSET_FOLDER + '/image_cid.txt')

    # TODO: remove fund account for mainnet and prompt for user to fund account themselves.

    print("\n=== Preparing Candy Machine account ===")
    if MODE == "dev" or MODE == "test":
        alice = Account.generate()
        faucet_client = FaucetClient(FAUCET_URL, rest_client)
        #for i in range (20):
        faucet_client.fund_account(alice.address(), 200000000)
        # accountAddres = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
        # privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
        # alice = Account(accountAddres, privateKey)
    else:
        accountAddres = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
        privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
        alice = Account(accountAddres, privateKey)
    print(f'Public key: {alice.address()}\n')
    print(f'Private key: {alice.private_key}\n')
    config['candymachine']['cmPublicKey'] = str(alice.address())
    config['candymachine']['cmPrivateKey'] = str(alice.private_key)
    with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
        json.dump(config, configfile, indent=4)
    
    try:
        accountBalance = int (rest_client.account_balance(alice.address().hex()))
    except TypeError:
        print("Please add some Aptos to your candy machine account")
        return 
    while (True):
        answer = input("Enter yes if you have some aptos in your account: ") 
        if answer == "yes": 
            if accountBalance > 2000:
                print(f'Balance: {accountBalance}\n')
                break
        else:
            continue
    
    print("\n=== Creating Candy Machine ===")
    txn_hash = rest_client.create_candy_machine(alice)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)

    print("\n=== Creating Collection ===")

    txn_hash = rest_client.create_collection(
        alice, 
        _COLLECTION_NAME, 
        _COLLECTION_DESCRIPTION, 
        _COLLECTION_COVER,
        _COLLECTION_SIZE,
        _MINT_FEE,
        _PUBLIC_MINT_TIME,
        _PRESALE_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)


    print("\n=== Setting presale mint time ===")
    txn_hash = rest_client.set_presale_mint_time(
            alice, _COLLECTION_NAME, _PRESALE_MINT_TIME)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, presale mint time is set to: " + str (datetime.datetime.fromtimestamp(_PRESALE_MINT_TIME)) + " txn hash: " + txn_hash)


    print("\n=== Setting public mint time ===")
    txn_hash = rest_client.set_public_mint_time(
            alice, _COLLECTION_NAME, _PUBLIC_MINT_TIME)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, public mint time is set to: " + str(datetime.datetime.fromtimestamp(_PUBLIC_MINT_TIME)) + " txn hash: " + txn_hash)

    print("\n=== Uploading NFT ===")
    # tmp_file = open(_ASSET_FOLDER + '/image_cid.txt', 'r')
    # lines = tmp_file.readlines()
    uri_list_file_path = os.path.join(_ASSET_FOLDER, "image_uris.json")
    with open(uri_list_file_path, "r") as uri_list_file:
        uri_list = json.load(uri_list_file)

    all_descrips = list()
    all_token_names = list()
    all_uri = list()
    counter = 0

    # test traits
    propertyKey = []
    propertyValue = []
    propertyType = []
    propertyKeys = []
    propertyValues = []
    propertyTypes = []

    nfts = []
    for uriInfo in uri_list:
        counter += 1

        tmp_name = _COLLECTION_NAME + " - #" + str(counter)
        tmp_uri = uriInfo["uri"]
        tmp_description = tmp_name
        # read in traits 
        with open(_METADATA_FOLDER + '/' + uriInfo["name"] + '.json') as metadata_file:    
            data = json.load(metadata_file)
            for trait in data['attributes']:
                if isinstance(trait['value'], str): 
                    propertyKey.append(trait['trait_type'])
                    # todo: wait aptos update on type of property values
                    propertyValue.append(trait['value'].encode())
                    #propertyValue.append([1])
                    propertyType.append('String')
        nfts.append(
            NFT(tmp_name, tmp_uri, tmp_description, propertyKey, propertyValue, propertyType)
        )
        propertyKey, propertyValue, propertyType = [], [], []
    random.shuffle(nfts)
    for nft in nfts:
        all_token_names.append(nft.name)
        all_descrips.append(nft.description)
        all_uri.append(nft.uri)
        propertyKeys.append(nft.propertyKey)
        propertyValues.append(nft.propertyValue)
        propertyTypes.append(nft.propertyType)

    # batch upload x nft at a time
    batch_num = 15
    num_batch = len(all_token_names) // batch_num
    remainder = len(all_token_names) % batch_num
    for i in range(num_batch):
        print(f"batch iter:{i}")
        startIndex = i * batch_num
        endIndex = startIndex + batch_num
        handleNftUpload(startIndex, endIndex, all_token_names, all_descrips, all_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, propertyKeys, propertyValues, propertyTypes, alice, _COLLECTION_NAME, rest_client)
        
    if remainder:
        startIndex = num_batch*batch_num
        endIndex = len(all_token_names)
        handleNftUpload(startIndex, endIndex, all_token_names, all_descrips, all_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, propertyKeys, propertyValues, propertyTypes, alice, _COLLECTION_NAME, rest_client)


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
    txn_hash = rest_client.upload_nft(alice, _COLLECTION_NAME, batch_token_names, batch_descrips, batch_uri, _ROYALTY_POINTS_DENOMINATOR, _ROYALTY_POINTS_NUMERATOR, batch_property_keys, batch_property_values, batch_property_types)
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)


# def mint():
#     with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
#         config = json.load(f)

#     _COLLECTION_NAME = config['collection']['collectionName']
#     _ACCOUNT_ADDRESS = config['candymachine']['cmPublicKey']
#     _ACCOUNT_PRIVATE_KEY = config['candymachine']['cmPrivateKey']
#     rest_client = RestClient(NODE_URL)

#     accountAddres = AccountAddress.from_hex(_ACCOUNT_ADDRESS)
#     privateKey = ed25519.PrivateKey.from_hex(_ACCOUNT_PRIVATE_KEY)
#     alice = Account(accountAddres, privateKey)
#     #Testing mint
#     print("\n=== Bob going to mint NFT ===")
#     bob = Account.generate()
#     print(f"bob address: {bob.address()}")
#     print(f"bob private: {bob.private_key}")
#     print(f'Public key: {alice.address()}\n')
#     print(f'Private key: {alice.private_key}\n')

#     FaucetClient(FAUCET_URL, rest_client).fund_account(bob.address(), 20000000000)
#     accountBalance = int (rest_client.account_balance(bob.address().hex()))
#     print(accountBalance)
#     txn_hash = rest_client.mint_tokens(
#         user=bob, admin_addr=alice.address(), collection_name=_COLLECTION_NAME, amount=1)

#     rest_client.wait_for_transaction(txn_hash)
#     print("\n Success, txn hash: " + txn_hash)

# mint()