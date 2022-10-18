import time
from typing import Any, Dict, List, Optional

import httpx

from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress

from aptos_sdk.bcs import Serializer
from transactions import (EntryFunction, TransactionPayload)
from aptos_sdk.transactions import (RawTransaction,SignedTransaction, TransactionArgument)
from aptos_sdk.authenticator import (Authenticator, Ed25519Authenticator)
from constants import CONTRACT_ADDRESS
from constants import MAX_GAS
from constants import GAS_UNIT
from aptos_sdk import client
U64_MAX = 18446744073709551615

class RestClient(client.RestClient):
    """A wrapper around the Aptos-core Rest API"""

    chain_id: int
    client: httpx.Client
    base_url: str

    def __init__(self, base_url: str):
        super().__init__(base_url)

    def create_single_signer_bcs_transaction(
        self, sender: Account, payload: TransactionPayload
    ) -> SignedTransaction:
        raw_transaction = RawTransaction(
            sender.address(),
            self.account_sequence_number(sender.address()),
            payload,
            MAX_GAS,
            GAS_UNIT,
            int(time.time()) + 600,
            self.chain_id,
        )

        signature = sender.sign(raw_transaction.keyed())
        authenticator = Authenticator(
            Ed25519Authenticator(sender.public_key(), signature)
        )
        return SignedTransaction(raw_transaction, authenticator)
    #
    # Token transaction wrappers
    #

    def create_candy_machine(self, account: Account) -> str:
        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "create_cm_v2",
            [], [])
        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)     
        )
        return self.submit_bcs_transaction(signed_transaction)

    def create_collection(
        self, 
        account: Account, 
        name: str, 
        description: str, 
        uri: str,
        max_supply_per_user: int, 
        mint_fee_per_mille: int,
        public_mint_time: int,
        presale_mint_time: int
    ) -> str:
        """Creates a new collection within the specified account"""

        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(description, Serializer.str),
            TransactionArgument(uri, Serializer.str),
            TransactionArgument(U64_MAX, Serializer.u64),
            TransactionArgument(
                [False, False, False], Serializer.sequence_serializer(Serializer.bool)),
            TransactionArgument(True, Serializer.bool),
            TransactionArgument(max_supply_per_user, Serializer.u64),
            TransactionArgument(mint_fee_per_mille, Serializer.u64),
            TransactionArgument(public_mint_time, Serializer.u64),
            TransactionArgument(presale_mint_time, Serializer.u64)
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "create_collection",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)

    
    def update_whitelist(
        self, 
        account: Account, 
        name: str, 
        wl: list[AccountAddress], 
        sl: list[int]
    ) -> str:
        "Add wl into the whitelist with the supply up to sl."
        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(wl, Serializer.sequence_serializer(Serializer.struct)),
            TransactionArgument(sl, Serializer.sequence_serializer(Serializer.u64)),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "update_whitelist",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)


    def set_is_public(
        self,
        account: Account,
        name: str,
        is_public: bool
    ) -> str:
        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(is_public, Serializer.bool),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "set_is_public",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)

    def set_mint_fee_per_mille(
        self,
        account: Account,
        name: str,
        mint_fee_per_mille: float
    ) -> str:
        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(int(mint_fee_per_mille * 100000000), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "set_mint_fee",
            [],
            transaction_arguments,
        )
        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)

    def set_public_mint_time(
        self,
        account: Account,
        name: str,
        public_mint_time: int
    ) -> str:
        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(public_mint_time, Serializer.u64),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "set_public_mint_time",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)

    def set_presale_mint_time(
        self,
        account: Account,
        name: str,
        presale_mint_time: int
    ) -> str:
        transaction_arguments = [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(presale_mint_time, Serializer.u64),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "set_presale_mint_time",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)
    
    def upload_nft(
        self,
        account: Account,
        collection_name: str,
        token_names: list,
        token_descrip: list,
        token_uri: list,
        propertyKeys: list,
        propertyValues: list,
        propertyTypes: list
    ) -> str:
        transaction_arguments = [
            TransactionArgument(collection_name, Serializer.str),
            TransactionArgument(token_names, Serializer.sequence_serializer(Serializer.str)),
            TransactionArgument(token_descrip, Serializer.sequence_serializer(Serializer.str)),
            TransactionArgument(token_uri, Serializer.sequence_serializer(Serializer.str)),
            TransactionArgument(account.address(), Serializer.struct),
            TransactionArgument(1000, Serializer.u64),
            TransactionArgument(50, Serializer.u64),
            TransactionArgument([False, False, False, False, False], Serializer.sequence_serializer(Serializer.bool)),
            TransactionArgument(propertyKeys, Serializer.sequence_serializer(Serializer.sequence_serializer(Serializer.str))),
            TransactionArgument(propertyValues, Serializer.sequence_serializer(Serializer.sequence_serializer(Serializer.sequence_serializer(Serializer.u8)))),
            TransactionArgument(propertyTypes, Serializer.sequence_serializer(Serializer.sequence_serializer(Serializer.str))),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "upload_nft",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            account, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)


    def mint_tokens(
        self,
        user: Account,
        admin_addr: AccountAddress,
        collection_name: str,
        amount: int,
    ) -> str:
        transaction_arguments = [
            TransactionArgument(admin_addr, Serializer.struct),
            TransactionArgument(collection_name, Serializer.str),
            TransactionArgument(amount, Serializer.u64),
        ]

        payload = EntryFunction.natural(
            CONTRACT_ADDRESS,
            "mint_tokens",
            [],
            transaction_arguments,
        )

        signed_transaction = self.create_single_signer_bcs_transaction(
            user, TransactionPayload(payload)
        )
        return self.submit_bcs_transaction(signed_transaction)
