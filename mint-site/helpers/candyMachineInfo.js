export const candyMachineAddress = "0x8cbc1d0265706a924399d6ccbd3b1a611313d6a512cc5b9109313d6d6da2635a";
export const collectionName = "TestCollection101"; // Case sensitive!
export const collectionCoverUrl = "https://cloudflare-ipfs.com/ipfs/QmbNB4GzfpZJzMPw2qS5DEqbdnBJcmYDESPKA6bWyH1Dcm";
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
