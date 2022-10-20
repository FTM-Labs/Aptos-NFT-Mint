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


CONTRACT_ADDRESS = "0xdcd69bc972f11bfbc3de6a8b656b66a227fe4d38c8880c781e8bf8785195e1a9::candy_machine_v2"
MAX_GAS = 200000
GAS_UNIT = 100
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
