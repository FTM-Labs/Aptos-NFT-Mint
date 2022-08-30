
from client import RestClient
import os
import sys
from constants import NODE_URL
from account_address import AccountAddress
from account import Account
import ed25519
import os
import json

def update():
    with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
        config = json.load(f)
    _CM_PUBLIC = config['candymachine']['cmPublicKey']
    _CM_PRIVATE = config['candymachine']['cmPrivateKey']
    _PUBLIC_MINT_TIME = int(config['collection']['publicMintTime'])
    _COLLECTION_NAME = config['collection', 'collectionName']
    rest_client = RestClient(NODE_URL)


    cmAccount =  Account(
        AccountAddress.from_hex(_CM_PUBLIC), 
        ed25519.PrivateKey.from_hex(_CM_PRIVATE))

    txn_hash = rest_client.set_public_mint_time(
        cmAccount, _COLLECTION_NAME, _PUBLIC_MINT_TIME
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)
