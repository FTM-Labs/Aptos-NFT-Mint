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

MAINNET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
TEST_NET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
TEST_NET_FAUCET = os.getenv("APTOS_FAUCET_URL", "https://faucet.testnet.aptoslabs.com")
DEV_NET_NODE = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
DEV_NET_FAUCET = os.getenv("APTOS_FAUCET_URL", "https://faucet.devnet.aptoslabs.com")

CONTRACT_ADDRESS = "0xf7b81362cb099f5f48df721dd2db9bd2c1832b31394540101acdb91e1d7b4d4a::candy_machine_v2"
MAX_GAS = 1500000
GAS_UNIT = 100
BATCH_NUMBER = 200
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
