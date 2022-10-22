import os

MODE = "dev"
if MODE == "dev":
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
    FAUCET_URL = os.getenv("APTOS_FAUCET_URL", "https://faucet.devnet.aptoslabs.com")
elif MODE == "test":
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
    FAUCET_URL = os.getenv("APTOS_FAUCET_URL", "https://faucet.testnet.aptoslabs.com")
else:
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.mainnet.aptoslabs.com/v1")
    FAUCET_URL=None


CONTRACT_ADDRESS = "0xc071ef709539f7f9372f16050bf984fe6f11850594b8394f11bc74d22f48836b::candy_machine_v2"
MAX_GAS = 200000
GAS_UNIT = 100
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
