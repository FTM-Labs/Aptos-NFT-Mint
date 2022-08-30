import os

NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
FAUCET_URL = os.getenv("APTOS_FAUCET_URL", "https://faucet.devnet.aptoslabs.com")
CONTRACT_ADDRESS = "0xfc0aba6b7264089f7817c3a2c1faa00601dea0713ee278df54ab6fc543a73e92::candy_machine_v2"
MAX_GAS = 200000
IPFS_GATEWAY = "https://cloudflare-ipfs.com/ipfs/"
