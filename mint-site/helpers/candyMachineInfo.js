export const candyMachineAddress = "0xea556867064bb111cac0c090496239ea34fd5c2863b938d067fb6efa0061f85f";
export const collectionName = "Bamboo Test"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmRkJpqa6KXLxqYAHbjEWVT9AaG6iaX4qn4bWmiwWk1Zrq";
export const mode = "dev"; // "dev" or "test" or "mainnet"

export let NODE_URL;
export const CONTRACT_ADDRESS = "0x481efbf0c3cbec627b5f5674287d4ae6ee770da5949dcfe698a8520108236a33";
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
