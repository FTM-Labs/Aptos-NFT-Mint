export const candyMachineAddress = "0xd681db00fffa1584c7c6c251ea903b65546e2dd11da571c9029fef06fa433800";
export const collectionName = "TestCollection101"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmV9Qkoux7Xkrm2FjZmhkrDHnWAPV4LnZ8ZjQPBzLxtduf";
export const mode = "dev"; // "dev" or "test" or "mainnet"

export let NODE_URL;
export const CONTRACT_ADDRESS = "0x4b8cec33043700c2e159b55d39dff908c28f21ebaf0d64b0539a465721021a3a";
export const COLLECTION_SIZE = 10
let FAUCET_URL;
if (mode == "dev") {
    NODE_URL = "https://fullnode.devnet.aptoslabs.com/v1";
    FAUCET_URL = "https://faucet.devnet.aptoslabs.com";
} else if (mode === "test") {
    NODE_URL = "https://fullnode.testnet.aptoslabs.com/v1";
    FAUCET_URL = "https://faucet.testnet.aptoslabs.com";
} else {
    NODE_URL = "https://fullnode.mainnet.aptoslabs.com/v1";
    FAUCET_URL = null;
}
