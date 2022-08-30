
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
    _WL_DIR = config['collection']['whitelistDir']
    _COLLECTION_NAME = config['collection']['collectionName']
    rest_client = RestClient(NODE_URL)

    tmp_file = open(_WL_DIR + '/whitelist.txt', 'r')
    lines = tmp_file.readlines()
    addresses = []
    wl_supplies = []
    for line in lines:
        address, wl_supply = line.split(' ')
        print("address: " + address + ' with supply: ' + wl_supply)
        addresses.append(AccountAddress.from_hex(address))
        wl_supplies.append(int(wl_supply))
    cmAccount =  Account(
        AccountAddress.from_hex(_CM_PUBLIC), 
        ed25519.PrivateKey.from_hex(_CM_PRIVATE))

    txn_hash = rest_client.update_whitelist(
        cmAccount, _COLLECTION_NAME, addresses, wl_supplies
    )
    rest_client.wait_for_transaction(txn_hash)
    print("\n Success, txn hash: " + txn_hash)
