"""
This translates Aptos transactions to and from BCS for signing and submitting to the REST API.
"""

from __future__ import annotations

import typing
from aptos_sdk.transactions import (ModuleId, TransactionArgument, Script, ModuleBundle)
from aptos_sdk.bcs import Deserializer, Serializer
from aptos_sdk.type_tag import TypeTag


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
