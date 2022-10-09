import os

NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
FAUCET_URL = os.getenv("APTOS_FAUCET_URL", "https://faucet.devnet.aptoslabs.com")
#NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
#FAUCET_URL = os.getenv("APTOS_FAUCET_URL", "https://faucet.testnet.aptoslabs.com")
CONTRACT_ADDRESS = "0x5ac985f1fe40c5121eb33699952ce8a79b1d1cb7438709dbd1da8e840a04fbee::candy_machine_v2"
MAX_GAS = 200000
GAS_UNIT = 100
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
