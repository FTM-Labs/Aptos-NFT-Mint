"""
This translates Aptos transactions to and from BCS for signing and submitting to the REST API.
"""

from __future__ import annotations

import hashlib
import typing

import ed25519
from account_address import AccountAddress
from authenticator import (Authenticator, Ed25519Authenticator,
                            MultiAgentAuthenticator)
from bcs import Deserializer, Serializer
from type_tag import StructTag, TypeTag


class RawTransaction:
    # Sender's address
    sender: AccountAddress
    # Sequence number of this transaction. This must match the sequence number in the sender's
    # account at the time of execution.
    sequence_number: int
    # The transaction payload, e.g., a script to execute.
    payload: TransactionPayload
    # Maximum total gas to spend for this transaction
    max_gas_amount: int
    # Price to be paid per gas unit.
    gas_unit_price: int
    # Expiration timestamp ffor this transactions, represented as seconds from the Unix epoch.
    expiration_timestamps_secs: int
    # Chain ID of the Aptos network this transaction is intended for.
    chain_id: int

    def __init__(
        self,
        sender: AccountAddress,
        sequence_number: int,
        payload: TransactionPayload,
        max_gas_amount: int,
        gas_unit_price: int,
        expiration_timestamps_secs: int,
        chain_id: int,
    ):
        self.sender = sender
        self.sequence_number = sequence_number
        self.payload = payload
        self.max_gas_amount = max_gas_amount
        self.gas_unit_price = gas_unit_price
        self.expiration_timestamps_secs = expiration_timestamps_secs
        self.chain_id = chain_id

    def __eq__(self, other: RawTranasction) -> bool:
        return (
            self.sender == other.sender
            and self.sequence_number == other.sequence_number
            and self.payload == other.payload
            and self.max_gas_amount == other.max_gas_amount
            and self.gas_unit_price == other.gas_unit_price
            and self.expiration_timestamps_secs == other.expiration_timestamps_secs
            and self.chain_id == other.chain_id
        )

    def __str__(self):
        return f"""RawTranasction:
    sender: {self.sender}
    sequence_number: {self.sequence_number}
    payload: {self.payload}
    max_gas_amount: {self.max_gas_amount}
    gas_unit_price: {self.gas_unit_price}
    expiration_timestamps_secs: {self.expiration_timestamps_secs}
    chain_id: {self.chain_id}
"""

    def prehash(self) -> bytes:
        hasher = hashlib.sha3_256()
        hasher.update(b"APTOS::RawTransaction")
        return hasher.digest()

    def keyed(self) -> bytes:
        ser = Serializer()
        self.serialize(ser)
        prehash = bytearray(self.prehash())
        prehash.extend(ser.output())
        return bytes(prehash)

    def sign(self, key: ed25519.PrivateKey) -> ed25519.Signature:
        return key.sign(self.keyed())

    def verify(self, key: ed25519.PublicKey, signature: ed25519.Signature) -> bool:
        return key.verify(self.keyed(), signature)

    def deserialize(deserializer: Deserializer) -> RawTransaction:
        return RawTransaction(
            AccountAddress.deserialize(deserializer),
            deserializer.u64(),
            TransactionPayload.deserialize(deserializer),
            deserializer.u64(),
            deserializer.u64(),
            deserializer.u64(),
            deserializer.u8(),
        )

    def serialize(self, serializer: Serializer):
        self.sender.serialize(serializer)
        serializer.u64(self.sequence_number)
        self.payload.serialize(serializer)
        serializer.u64(self.max_gas_amount)
        serializer.u64(self.gas_unit_price)
        serializer.u64(self.expiration_timestamps_secs)
        serializer.u8(self.chain_id)


class MultiAgentRawTransaction:
    raw_transaction: RawTransaction
    secondary_signers: List[AccountAddress]

    def __init__(
        self, raw_transaction: RawTransaction, secondary_signers: List[AccountAddress]
    ):
        self.raw_transaction = raw_transaction
        self.secondary_signers = secondary_signers

    def inner(self) -> RawTransaction:
        return self.raw_transaction

    def prehash(self) -> bytes:
        hasher = hashlib.sha3_256()
        hasher.update(b"APTOS::RawTransactionWithData")
        return hasher.digest()

    def keyed(self) -> bytes:
        serializer = Serializer()
        # This is a type indicator for an enum
        serializer.u8(0)
        serializer.struct(self.raw_transaction)
        serializer.sequence(self.secondary_signers, Serializer.struct)

        prehash = bytearray(self.prehash())
        prehash.extend(serializer.output())
        return bytes(prehash)

    def sign(self, key: ed25519.PrivateKey) -> ed25519.Signature:
        return key.sign(self.keyed())

    def verify(self, key: ed25519.PublicKey, signature: ed25519.Signature) -> bool:
        return key.verify(self.keyed(), signature)


class TransactionPayload:
    SCRIPT: int = 0
    MODULE_BUNDLE: int = 1
    SCRIPT_FUNCTION: int = 2

    variant: int
    value: typing.Any

    def __init__(self, payload: typing.Any):
        if isinstance(payload, Script):
            self.variant = TransactionPayload.SCRIPT
        elif isinstance(payload, ModuleBundle):
            self.variant = TransactionPayload.MODULE_BUNDLE
        elif isinstance(payload, EntryFunction):
            self.variant = TransactionPayload.SCRIPT_FUNCTION
        else:
            raise Exception("Invalid type")
        self.value = payload

    def __eq__(self, other: TransactionPayload) -> bool:
        return self.variant == other.variant and self.value == other.value

    def __str__(self) -> str:
        return self.value.__str__()

    def deserialize(deserializer: Deserializer) -> TransactionPayload:
        variant = deserializer.uleb128()

        if variant == TransactionPayload.SCRIPT:
            payload = Script.deserialize(deserializer)
        elif variant == TransactionPayload.MODULE_BUNDLE:
            payload = ModuleBundle.deserialize(deserializer)
        elif variant == TransactionPayload.SCRIPT_FUNCTION:
            payload = EntryFunction.deserialize(deserializer)
        else:
            raise Exception("Invalid type")

        return TransactionPayload(payload)

    def serialize(self, serializer: Serializer):
        serializer.uleb128(self.variant)
        self.value.serialize(serializer)


class ModuleBundle:
    def __init__(self):
        raise NotImplementedError

    def deserialize(deserializer: Deserializer) -> ModuleBundle:
        raise NotImplementedError

    def serialize(self, serializer: Serializer):
        raise NotImplementedError


class Script:
    def __init__(self):
        raise NotImplementedError

    def deserialize(deserializer: Deserializer) -> Script:
        raise NotImplementedError

    def serialize(self, serializer: Serializer):
        raise NotImplementedError


class EntryFunction:
    module: ModuleId
    function: str
    ty_args: List[TypeTag]
    args: List[bytes]

    def __init__(
        self, module: ModuleId, function: str, ty_args: List[TypeTag], args: List[bytes]
    ):
        self.module = module
        self.function = function
        self.ty_args = ty_args
        self.args = args

    def __eq__(self, other: EntryFunction) -> bool:
        return (
            self.module == other.module
            and self.function == other.function
            and self.ty_args == other.ty_args
            and self.args == other.args
        )

    def __str__(self):
        return f"{self.module}::{self.function}::<{self.ty_args}>({self.args})"

    def natural(
        module: str,
        function: str,
        ty_args: List[TypeTag],
        args: List[TransactionArgument],
    ) -> EntryFunction:
        module_id = ModuleId.from_str(module)

        byte_args = []
        for arg in args:
            byte_args.append(arg.encode())
        return EntryFunction(module_id, function, ty_args, byte_args)

    def deserialize(deserializer: Deserializer) -> EntryFunction:
        module = ModuleId.deserialize(deserializer)
        function = deserializer.str()
        ty_args = deserializer.sequence(TypeTag.deserialize)
        args = deserializer.sequence(Deserializer.bytes)
        return EntryFunction(module, function, ty_args, args)

    def serialize(self, serializer: Serializer):
        self.module.serialize(serializer)
        serializer.str(self.function)
        serializer.sequence(self.ty_args, Serializer.struct)
        serializer.sequence(self.args, Serializer.bytes)


class ModuleId:
    address: AccountAddress
    name: str

    def __init__(self, address: AccountAddress, name: str):
        self.address = address
        self.name = name

    def __eq__(self, other: ModuleId) -> bool:
        return self.address == other.address and self.name == other.name

    def __str__(self) -> str:
        return f"{self.address}::{self.name}"

    def from_str(module_id: str) -> ModuleId:
        split = module_id.split("::")
        return ModuleId(AccountAddress.from_hex(split[0]), split[1])

    def deserialize(deserializer: Deserializer) -> ModuleId:
        addr = AccountAddress.deserialize(deserializer)
        name = deserializer.str()
        return ModuleId(addr, name)

    def serialize(self, serializer: Serializer):
        self.address.serialize(serializer)
        serializer.str(self.name)


class TransactionArgument:
    value: typing.Any
    encoder: typing.Callable[[Serializer, typing.Any], bytes]

    def __init__(
        self,
        value: typing.Any,
        encoder: typing.Callable[[Serializer, typing.Any], bytes],
    ):
        self.value = value
        self.encoder = encoder

    def encode(self) -> bytes:
        ser = Serializer()
        self.encoder(ser, self.value)
        return ser.output()


class SignedTransaction:
    transaction: RawTransaction
    authenticator: Authenticator

    def __init__(self, transaction: RawTransaction, authenticator: Authenticator):
        self.transaction = transaction
        self.authenticator = authenticator

    def __eq__(self, other: SignedTransaction) -> bool:
        return (
            self.transaction == other.transaction
            and self.authenticator == other.authenticator
        )

    def __str__(self) -> str:
        return f"Transaction: {self.transaction}Authenticator: {self.authenticator}"

    def bytes(self) -> bytes:
        ser = Serializer()
        ser.struct(self)
        return ser.output()

    def verify(self) -> bool:
        if isinstance(self.authenticator.authenticator, MultiAgentAuthenticator):
            transaction = MultiAgentRawTransaction(
                self.transaction, self.authenticator.authenticator.secondary_addresses()
            )
            keyed = transaction.keyed()
        else:
            keyed = self.transaction.keyed()
        return self.authenticator.verify(keyed)

    def deserialize(deserializer: Deserializer) -> SignedTransaction:
        transaction = RawTransaction.deserialize(deserializer)
        authenticator = Authenticator.deserialize(deserializer)
        return SignedTransaction(transaction, authenticator)

    def serialize(self, serializer: Serializer):
        self.transaction.serialize(serializer)
        self.authenticator.serialize(serializer)
