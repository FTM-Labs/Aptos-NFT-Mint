import constants
from client import RestClient
from aptos_sdk.client import FaucetClient
import sys
import os
import json
from aptos_sdk.account import Account, AccountAddress, ed25519
from nft import NFT 
import random 
import constants
import util
import datetime
from pick import pick

class CandyMachine:
    def __init__(self, mode, batch_num):
        self.mode = mode
        self.batch_num = batch_num
        self.node = None
        self.faucet = None
        self.account = None
        print(f"Mode: {self.mode}")
        print(f"Contract address: {constants.CONTRACT_ADDRESS}")
        if mode == 'dev':
            self.node = constants.DEV_NET_NODE
            self.faucet = constants.DEV_NET_FAUCET
        elif mode == 'test':
            self.node = constants.TEST_NET_NODE
            self.faucet = constants.TEST_NET_FAUCET
        else:
            self.node = constants.MAINNET_NODE

        self.rest_client = RestClient(self.node)
        if self.faucet:
            self.faucet_client = FaucetClient(self.faucet, self.rest_client)

        with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
            config = json.load(f)
        self.asset_folder = config['collection']['assetDir']
        self.metadata_folder = config['collection']['metadataDir']
        self.collection_name = config['collection']['collectionName']
        self.collection_description = config['collection']['collectionDescription']
        self.collection_size = config['collection']['collectionSize']
        self.collection_cover = config['collection']['collectionCover']
        self.max_mint_per_wallet = int(config['collection']['maxMintPerWallet'])
        self.mint_fee = int(config['collection']['mintFee'])
        self.public_mint_time = int(config['collection']['publicMintTime'])
        self.presale_mint_time = int(config['collection']['presaleMintTime'])
        self.royalty_points_denominator = config['collection']['royalty_points_denominator']
        self.royalty_points_numerator = config['collection']['royalty_points_numerator']
    
    def prepareAccount(self):
        with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
            config = json.load(f)
        if len(config['candymachine']['cmPublicKey']) == 66 and len(config['candymachine']['cmPrivateKey']) == 66:
            print("Candy machine addresses are already filled in config.json.")
            _, index = pick(["yes", "no"], "Candy machine addresses are already filled in config.json. Do you wish to override them with new funded accounts?")
            if index == 1:
                account = self.get_existing_account()
            else:
                account = self.generate_new_account()
        else:
            account = self.generate_new_account()
        print(f'Public key: {account.address()}\n')
        print(f'Private key: {account.private_key}\n')
        if self.mode == "dev":
            print("Airdropping 3 APT to your account on dev net")
            for i in range(3):
                self.faucet_client.fund_account(account.address(), 100000000)

        while (True):
            answer = "yes" if self.mode == "dev" else input("Enter yes if you have some aptos in the account above: ") 
            if answer == "yes":
                try:
                    print(f"Checking account address {account.address()}")
                    accountBalance = int (self.rest_client.account_balance(account.address().hex()))
                except TypeError:
                    print("Please add some Aptos to your candy machine account and try again.")
                    raise Exception("Not enough funds in account")
                if accountBalance > 2000:
                    print(f'Balance: {accountBalance}\n')
                    break
            else:
                continue
        self.account = account
    
    def get_existing_account(self):
        with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
            config = json.load(f)
        self.account_addr = config['candymachine']['cmPublicKey']
        self.account_private = config['candymachine']['cmPrivateKey']
        account_addr = AccountAddress.from_hex(self.account_addr)
        account_private = ed25519.PrivateKey.from_hex(self.account_private)
        account = Account(account_addr, account_private)
        return account
    
    def generate_new_account(self):
        with open(os.path.join(sys.path[0], "config.json"), 'r') as f:
            config = json.load(f)
        account = Account.generate()
        config['candymachine']['cmPublicKey'] = str(account.address())
        config['candymachine']['cmPrivateKey'] = str(account.private_key)
        self.account_addr = config['candymachine']['cmPublicKey']
        self.account_private = config['candymachine']['cmPrivateKey']
        with open(os.path.join(sys.path[0], "config.json"), 'w') as configfile:
            json.dump(config, configfile, indent=4)
        return account
        
    def create(self):
        print("\n=== Preparing candy machine account ===")
        self.prepareAccount()
        print("\n=== Verifying assets and metadata ===")
        if not util.verifyMetadataFiles(): return
        
        print('\n=== Upload assets to storage solution ===')
        if not util.uploadFolder():
            print("Not all files were uploaded to storage. Try again.")
            return
        self.createCandyMachine()
        self.createCollection()
        self.uploadNftsToCm()
        self.update_presale_mint_time()
        self.update_public_mint_time()
        self.update_mint_fee()



    def resetChainInfoFromUriInfo(self, asset_folder):
        uri_list_file_path = os.path.join(asset_folder, "image_uris.json")
        with open(uri_list_file_path, "r+") as uri_list_file:
            uri_list = json.load(uri_list_file)
            for uriInfo in uri_list:
                uriInfo["onChain"] = False
            uri_list_file.seek(0)
            json.dump(uri_list, uri_list_file, indent=4)
            uri_list_file.truncate()

    def createCandyMachine(self):
        print("\n=== Creating Candy Machine ===")
        txn_hash = self.rest_client.create_candy_machine(self.account)
        self.rest_client.wait_for_transaction(txn_hash)
        print("\n Success, txn hash: " + txn_hash)
        self.resetChainInfoFromUriInfo(self.asset_folder)

        
    def createCollection(self):
        print("\n=== Creating Collection ===")
        txn_hash = self.rest_client.create_collection(
            self.account, 
            self.collection_name, 
            self.collection_description, 
            self.collection_cover,
            self.max_mint_per_wallet,
            self.mint_fee,
            self.public_mint_time,
            self.presale_mint_time
        )
        self.rest_client.wait_for_transaction(txn_hash)
        print("\n Success, txn hash: " + txn_hash)

    def handleNftUpload(
        self,
        startIndex, 
        endIndex,
        all_token_names, 
        all_descrips, 
        all_uri, 
        _ROYALTY_POINTS_DENOMINATOR, 
        _ROYALTY_POINTS_NUMERATOR
    ):
        batch_token_names = all_token_names[startIndex:endIndex]
        batch_descrips = all_descrips[startIndex:endIndex]
        batch_uri = all_uri[startIndex:endIndex]
        try:
            txn_hash = self.rest_client.upload_nft(
                self.account, 
                self.collection_name, 
                batch_token_names, 
                batch_descrips, 
                batch_uri, 
                _ROYALTY_POINTS_DENOMINATOR, 
                _ROYALTY_POINTS_NUMERATOR
            )
            self.rest_client.wait_for_transaction(txn_hash)
        except Exception as e:
            print(f"An error occured while uploading batch from {startIndex} to {endIndex}")
            print(e)
            return False
        print("\n Success, txn hash: " + txn_hash)
        return True

    def uploadNftsToCm(self):
        print("\n=== Uploading NFT ===")
        uri_list_file_path = os.path.join(self.asset_folder, "image_uris.json")
        with open(uri_list_file_path, "r") as uri_list_file:
            uri_list = json.load(uri_list_file)

        all_descrips = list()
        all_token_names = list()
        all_uri = list()

        nfts = []
        for index, uriInfo in enumerate(uri_list):
            if "onChain" in uriInfo.keys() and uriInfo["onChain"]: continue
            tmp_uri = uriInfo["uri"]
            tmp_metadata_uri = uriInfo["metadata_uri"]
            metadataFilePath = self.metadata_folder + '/' + uriInfo["name"] + '.json'
            with open(metadataFilePath) as metadata_file:
                data = json.load(metadata_file)
                tmp_name = data["name"]
                tmp_description = data["description"]
            nfts.append(
                {"nft": NFT(tmp_name, tmp_uri, tmp_metadata_uri, tmp_description), "uriInfoIndex": index}
            )

        random.shuffle(nfts)
        for nftInfo in nfts:
            all_token_names.append(nftInfo["nft"].name)
            all_descrips.append(nftInfo["nft"].description)
            all_uri.append(nftInfo["nft"].metadataUri)

        print(f"Uploading {len(nfts)} NFTs out of {len(uri_list)} ({len(uri_list) - len(nfts)} already uploaded).")
        # batch upload x nft at a time
        batch_num = constants.BATCH_NUMBER
        num_batch = len(all_token_names) // batch_num
        remainder = len(all_token_names) % batch_num
        if remainder > 0 :
            batch_iter =  num_batch + 1
        else:
            batch_iter = num_batch
        successfulUploadIndexes = []
        for i in range(batch_iter):
            print(f"batch iter:{i}")
            startIndex = i * batch_num
            endIndex = min(startIndex + batch_num, len(all_token_names))
            success = self.handleNftUpload(
                startIndex, 
                endIndex, 
                all_token_names, 
                all_descrips, 
                all_uri, 
                self.royalty_points_denominator, 
                self.royalty_points_numerator)
            if success: successfulUploadIndexes.extend(range(startIndex, endIndex))
            for successfulUploadIndex in successfulUploadIndexes:
                uri_list[nfts[successfulUploadIndex]["uriInfoIndex"]]["onChain"] = True
            with open(uri_list_file_path, "w") as uri_list_file:
                json.dump(uri_list, uri_list_file, indent=4)
        if len(successfulUploadIndexes) != len(nfts):
            print(f"Not all nfts ({len(successfulUploadIndexes)} out of {len(nfts)}) were uploaded successfully to the candy machine. Try to \"Retry failed uploads\".")

    def retryFailedUploads(self):
        self.account = self.get_existing_account()
        if len(self.account_addr) != 66 or len(self.account_private) != 66:
            print("Can't continue upload as CM info is not valid in config file")

        self.uploadNftsToCm()
    def update_mint_fee(self):
        print("\n=== Setting  mint fee ===")
        txn_hash = self.rest_client.set_mint_fee_per_mille(
            self.account, self.collection_name, self.mint_fee
        )
        self.rest_client.wait_for_transaction(txn_hash)
        print("\n Success, mint fee is set to:: " + str(self.mint_fee/100000000) + " txn hash: " + txn_hash)

    def update_presale_mint_time(self):
        print("\n=== Setting presale mint time ===")
        txn_hash = self.rest_client.set_presale_mint_time(
            self.account, self.collection_name, self.presale_mint_time
        )
        self.rest_client.wait_for_transaction(txn_hash)
        print("\n Success, presale mint time is set to: " + str (datetime.datetime.fromtimestamp(self.presale_mint_time)) + " txn hash: " + txn_hash)

    def update_public_mint_time(self):
        print("\n=== Setting public mint time ===")
        txn_hash = self.rest_client.set_public_mint_time(
            self.account, self.collection_name, self.public_mint_time
        )
        self.rest_client.wait_for_transaction(txn_hash)
        print("\n Success, public mint time is set to: " + str(datetime.datetime.fromtimestamp(self.public_mint_time)) + " txn hash: " + txn_hash)