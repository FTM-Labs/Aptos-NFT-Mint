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

MAINNET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.mainnet.aptoslabs.com/v1")
TEST_NET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
TEST_NET_FAUCET = os.getenv("APTOS_FAUCET_URL", "https://faucet.testnet.aptoslabs.com")
DEV_NET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
DEV_NET_FAUCET = os.getenv("APTOS_FAUCET_URL", "https://faucet.devnet.aptoslabs.com")

CONTRACT_ADDRESS = "0x5b71b400de0767bcec88464c33a0c74c839737206883a9379252f4907b8bf30e::ftmpad"
MAX_GAS = 2000000
GAS_UNIT = 100
BATCH_NUMBER = 300
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
AR_RESOLVER = "https://arweave.net/"
